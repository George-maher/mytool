"""
Base Module Interface for X-Shield Framework
All pentesting modules must inherit from this base class
"""

from abc import ABC, abstractmethod
from PySide6.QtCore import Signal, QObject, Slot
import time
from typing import Dict, Any, List


class BaseModule(QObject):
    """Base class for all pentesting modules"""
    
    # Module metadata (to be overridden by subclasses)
    NAME = "Base Module"
    DESCRIPTION = "Base module for pentesting framework"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "General"
    
    # Module parameters configuration
    PARAMETERS = {}
    
    # Signals
    progress_signal = Signal(int, int)  # current, total
    status_signal = Signal(str)  # status message
    finding_signal = Signal(str, dict)  # finding type, details
    vulnerability_signal = Signal(dict)  # vulnerability details
    finished = Signal(dict)  # results
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self._stop_requested = False
        self._is_running = False
        self._state = "IDLE"
        
        # Results storage
        self.results = {
            'module_name': self.NAME,
            'start_time': None,
            'end_time': None,
            'execution_time': 0,
            'target': None,
            'parameters': {},
            'findings': [],
            'vulnerabilities': [],
            'items_scanned': 0,
            'summary': '',
            'status': 'not_started',
            'telemetry': []
        }

    @property
    def state(self) -> str:
        return self._state

    def _update_state(self, new_state: str):
        self._state = new_state
        self.logger.info(f"Module {self.NAME} state transition: {new_state}")
    
    @abstractmethod
    def execute(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main module execution method
        
        Args:
            target: The target to scan (IP, domain, URL, etc.)
            parameters: Dictionary of module-specific parameters
            
        Returns:
            Dictionary containing scan results
        """
        pass
    
    @abstractmethod
    def validate_target(self, target: str) -> bool:
        """
        Validate if the target is appropriate for this module
        
        Args:
            target: The target to validate
            
        Returns:
            True if target is valid, False otherwise
        """
        pass
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
    
    def is_running(self) -> bool:
        """Check if module is currently running"""
        return self._is_running
    
    def _start_execution(self, target: str, parameters: Dict[str, Any]):
        """Initialize execution"""
        self._stop_requested = False
        self._is_running = True
        self._update_state("RUNNING")
        self.results['start_time'] = time.time()
        self.results['target'] = target
        self.results['parameters'] = parameters
        self.results['status'] = 'running'
        
        self.logger.module_start(self.NAME)
        self.status_signal.emit(f"Starting {self.NAME} scan...")
    
    def _finish_execution(self):
        """Finalize execution"""
        self.results['end_time'] = time.time()
        self.results['execution_time'] = self.results['end_time'] - self.results['start_time']
        self.results['status'] = 'completed'
        
        self._is_running = False
        self._update_state("FINISHED")
        self.logger.module_complete(self.NAME, self.results['execution_time'])
        self.status_signal.emit(f"{self.NAME} scan completed")
        self.finished.emit(self.results)
    
    def _handle_error(self, error: Exception):
        """Handle execution error"""
        self.results['end_time'] = time.time()
        self.results['execution_time'] = self.results['end_time'] - self.results['start_time']
        self.results['status'] = 'failed'
        self.results['error'] = str(error)
        
        self._is_running = False
        self.logger.module_error(self.NAME, str(error))
        self.status_signal.emit(f"{self.NAME} scan failed: {str(error)}")
        self.finished.emit(self.results)
    
    def add_finding(self, finding_type: str, details: Dict[str, Any]):
        """Add a finding to the results"""
        now = time.time()
        finding = {
            'type': finding_type,
            'timestamp': now,
            'details': details
        }
        self.results['findings'].append(finding)
        self.results['telemetry'].append({
            'timestamp': now,
            'event': 'FINDING_DISCOVERED',
            'type': finding_type
        })
        self.finding_signal.emit(finding_type, details)
        
        self.logger.info(f"Finding: {finding_type} - {details}")
    
    def add_vulnerability(self, vulnerability: Dict[str, Any]):
        """Add a vulnerability to the results"""
        # Ensure required fields
        required_fields = ['title', 'severity', 'description']
        for field in required_fields:
            if field not in vulnerability:
                raise ValueError(f"Vulnerability missing required field: {field}")
        
        vulnerability['timestamp'] = time.time()
        vulnerability['module'] = self.NAME
        self.results['vulnerabilities'].append(vulnerability)
        self.vulnerability_signal.emit(vulnerability)
        
        self.logger.vulnerability_found(
            vulnerability['severity'],
            vulnerability.get('target', 'Unknown'),
            vulnerability['title']
        )
    
    def update_progress(self, current: int, total: int):
        """Update progress"""
        self.progress_signal.emit(current, total)
        self.logger.scan_progress(current, total, self.results.get('target'))
    
    def set_summary(self, summary: str):
        """Set execution summary"""
        self.results['summary'] = summary
    
    def increment_items_scanned(self, count: int = 1):
        """Increment items scanned counter"""
        self.results['items_scanned'] += count
    
    def get_results(self) -> Dict[str, Any]:
        """Get current results"""
        return self.results.copy()
    
    @classmethod
    def get_module_info(cls) -> Dict[str, Any]:
        """Get module information"""
        return {
            'name': cls.NAME,
            'description': cls.DESCRIPTION,
            'version': cls.VERSION,
            'author': cls.AUTHOR,
            'category': cls.CATEGORY,
            'parameters': cls.PARAMETERS
        }
    
    @classmethod
    def validate_parameters(cls, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate module parameters
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for param_name, param_config in cls.PARAMETERS.items():
            param_type = param_config.get('type', 'string')
            required = param_config.get('required', False)
            
            # Check if required parameter is missing
            if required and param_name not in parameters:
                return False, f"Required parameter '{param_name}' is missing"
            
            # Validate parameter type
            if param_name in parameters:
                value = parameters[param_name]
                
                if param_type == 'integer':
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        return False, f"Parameter '{param_name}' must be an integer"
                
                elif param_type == 'boolean':
                    if not isinstance(value, bool):
                        return False, f"Parameter '{param_name}' must be a boolean"
                
                elif param_type == 'choice':
                    choices = param_config.get('choices', [])
                    if value not in choices:
                        return False, f"Parameter '{param_name}' must be one of: {choices}"
        
        return True, "Parameters are valid"


class NetworkModule(BaseModule):
    """Base class for network-related modules"""
    
    CATEGORY = "Network"
    
    def validate_target(self, target: str) -> bool:
        """Validate network target (IP address or hostname)"""
        import re
        
        # IP address validation
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, target):
            parts = target.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # Hostname validation
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(hostname_pattern, target))


class WebModule(BaseModule):
    """Base class for web-related modules"""
    
    CATEGORY = "Web"
    
    def validate_target(self, target: str) -> bool:
        """Validate web target (URL)"""
        return target.startswith(('http://', 'https://'))


class ExploitationModule(BaseModule):
    """Base class for exploitation modules"""
    
    CATEGORY = "Exploitation"
    
    def validate_target(self, target: str) -> bool:
        """Validate exploitation target"""
        # More permissive validation for exploitation
        return len(target) > 0


class OSINTModule(BaseModule):
    """Base class for OSINT modules"""
    
    CATEGORY = "OSINT"
    
    def validate_target(self, target: str) -> bool:
        """Validate OSINT target (domain, email, etc.)"""
        return len(target) > 0
