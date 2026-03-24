"""
Base Module Interface for X-Shield Framework v2
Enhanced for complex task chaining and detailed telemetry
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from PySide6.QtCore import Signal, QObject, Slot


class BaseModule(QObject):
    """Base class for all pentesting modules in X-Shield v2"""
    
    # Module metadata
    NAME = "Base Module"
    DESCRIPTION = "Base module for pentesting framework"
    VERSION = "2.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "General"
    
    # Module parameters configuration
    PARAMETERS = {}
    
    # Signals for UI and Core coordination
    progress_signal = Signal(str, int, int)  # module_name, current, total
    status_signal = Signal(str, str)  # module_name, status message
    finding_signal = Signal(str, str, dict)  # module_name, finding type, details
    vulnerability_signal = Signal(str, dict)  # module_name, vulnerability details
    log_signal = Signal(str, str, str)  # module_name, level, message
    finished = Signal(str, dict)  # module_name, results
    
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self._stop_requested = False
        self._is_running = False
        self._state = "IDLE"
        
        # Results storage (v2 Enhanced)
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
            'telemetry': [],
            'errors': []
        }

    @property
    def state(self) -> str:
        return self._state

    def _update_state(self, new_state: str):
        self._state = new_state
        self.log("DEBUG", f"State transition: {new_state}")
    
    @abstractmethod
    def execute(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Main module execution method (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def validate_target(self, target: str) -> bool:
        """Validate if the target is appropriate for this module"""
        pass
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.log("WARNING", "Stop requested by user or system")
    
    def is_running(self) -> bool:
        """Check if module is currently running"""
        return self._is_running
    
    def _start_execution(self, target: str, parameters: Dict[str, Any]):
        """Initialize execution environment"""
        self._stop_requested = False
        self._is_running = True
        self._update_state("RUNNING")
        self.results['start_time'] = time.time()
        self.results['target'] = target
        self.results['parameters'] = parameters
        self.results['status'] = 'running'
        
        self.log("INFO", f"Initiating {self.NAME} execution on {target}")
        self.status_signal.emit(self.NAME, f"Starting {self.NAME}...")
    
    def _finish_execution(self):
        """Finalize execution and emit results"""
        self.results['end_time'] = time.time()
        self.results['execution_time'] = self.results['end_time'] - self.results['start_time']
        self.results['status'] = 'completed'
        
        self._is_running = False
        self._update_state("FINISHED")
        self.log("INFO", f"Execution completed in {self.results['execution_time']:.2f}s")
        self.status_signal.emit(self.NAME, f"{self.NAME} completed")
        self.finished.emit(self.NAME, self.results)
    
    def _handle_error(self, error: Exception):
        """Handle execution error gracefully"""
        self.results['end_time'] = time.time()
        self.results['execution_time'] = self.results['end_time'] - self.results['start_time']
        self.results['status'] = 'failed'
        error_msg = str(error)
        self.results['errors'].append(error_msg)
        
        self._is_running = False
        self._update_state("ERROR")
        self.log("ERROR", f"Execution failed: {error_msg}")
        self.status_signal.emit(self.NAME, f"Failed: {error_msg}")
        self.finished.emit(self.NAME, self.results)

    def log(self, level: str, message: str):
        """Log message and emit signal for UI terminal"""
        if self.logger:
            if level == "DEBUG": self.logger.debug(f"[{self.NAME}] {message}")
            elif level == "INFO": self.logger.info(f"[{self.NAME}] {message}")
            elif level == "WARNING": self.logger.warning(f"[{self.NAME}] {message}")
            elif level == "ERROR": self.logger.error(f"[{self.NAME}] {message}")
            elif level == "CRITICAL": self.logger.critical(f"[{self.NAME}] {message}")

        self.log_signal.emit(self.NAME, level, message)

        # Add to telemetry
        self.results['telemetry'].append({
            'timestamp': time.time(),
            'event': 'LOG',
            'level': level,
            'message': message
        })
    
    def add_finding(self, finding_type: str, details: Dict[str, Any]):
        """Add a general finding to results"""
        now = time.time()
        finding = {
            'type': finding_type,
            'timestamp': now,
            'details': details
        }
        self.results['findings'].append(finding)
        self.finding_signal.emit(self.NAME, finding_type, details)
        self.log("INFO", f"Finding discovered: {finding_type}")
    
    def add_vulnerability(self, vulnerability: Dict[str, Any]):
        """Add a security vulnerability to results"""
        required = ['title', 'severity', 'description']
        for field in required:
            if field not in vulnerability:
                self.log("ERROR", f"Vulnerability missing required field: {field}")
                return
        
        vulnerability['timestamp'] = time.time()
        vulnerability['module'] = self.NAME
        self.results['vulnerabilities'].append(vulnerability)
        self.vulnerability_signal.emit(self.NAME, vulnerability)
        
        sev = vulnerability['severity'].upper()
        self.log("WARNING", f"VULNERABILITY [{sev}]: {vulnerability['title']}")
    
    def update_progress(self, current: int, total: int):
        """Update execution progress"""
        self.progress_signal.emit(self.NAME, current, total)
    
    def set_summary(self, summary: str):
        """Set final summary of module execution"""
        self.results['summary'] = summary
    
    def increment_scanned(self, count: int = 1):
        """Increment scanned items counter"""
        self.results['items_scanned'] += count


class NetworkModule(BaseModule):
    """Base class for network-related modules"""
    CATEGORY = "Network"
    
    def validate_target(self, target: str) -> bool:
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, target):
            return all(0 <= int(part) <= 255 for part in target.split('.'))
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(hostname_pattern, target))


class WebModule(BaseModule):
    """Base class for web-related modules"""
    CATEGORY = "Web"
    
    def validate_target(self, target: str) -> bool:
        return target.startswith(('http://', 'https://'))


class AttackModule(BaseModule):
    """Base class for attack and stress testing modules"""
    CATEGORY = "Attack"
    
    def validate_target(self, target: str) -> bool:
        return len(target) > 0


class OSINTModule(BaseModule):
    """Base class for OSINT modules"""
    CATEGORY = "OSINT"
    
    def validate_target(self, target: str) -> bool:
        return len(target) > 0
