"""
Centralized Logging System for X-Shield
Provides real-time logging with GUI integration
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Signal, QObject
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class LogSignal(QObject):
    """Signal class for log messages"""
    log_signal = Signal(str, str, str)  # level, message, timestamp


class Logger:
    """Centralized logging system with GUI integration"""
    
    def __init__(self, log_file=None):
        self.log_signal = LogSignal()
        self.log_file = log_file or "data/logs/xshield.log"
        
        # Ensure log directory exists
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup Python logging configuration"""
        # Create logger
        self.logger = logging.getLogger("X-Shield")
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _log(self, level, message, color=None):
        """Internal logging method with GUI signal emission"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log to Python logger
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)
        
        # Print to console with color
        if color:
            print(f"{color}[{timestamp}] {level}: {message}{Style.RESET_ALL}")
        else:
            print(f"[{timestamp}] {level}: {message}")
        
        # Emit signal for GUI
        self.log_signal.log_signal.emit(level, message, timestamp)
    
    def debug(self, message):
        """Log debug message"""
        self._log("DEBUG", message, Fore.CYAN)
    
    def info(self, message):
        """Log info message"""
        self._log("INFO", message, Fore.GREEN)
    
    def warning(self, message):
        """Log warning message"""
        self._log("WARNING", message, Fore.YELLOW)
    
    def error(self, message):
        """Log error message"""
        self._log("ERROR", message, Fore.RED)
    
    def critical(self, message):
        """Log critical message"""
        self._log("CRITICAL", message, Fore.MAGENTA)
    
    def success(self, message):
        """Log success message"""
        self._log("SUCCESS", message, Fore.GREEN)
    
    def module_start(self, module_name):
        """Log module start"""
        self.info(f"Starting module: {module_name}")
    
    def module_complete(self, module_name, duration=None):
        """Log module completion"""
        if duration:
            self.success(f"Module {module_name} completed in {duration:.2f}s")
        else:
            self.success(f"Module {module_name} completed")
    
    def module_error(self, module_name, error):
        """Log module error"""
        self.error(f"Module {module_name} failed: {error}")
    
    def scan_progress(self, current, total, target=None):
        """Log scan progress"""
        percentage = (current / total) * 100 if total > 0 else 0
        if target:
            self.debug(f"Scanning {target}: {current}/{total} ({percentage:.1f}%)")
        else:
            self.debug(f"Progress: {current}/{total} ({percentage:.1f}%)")
    
    def vulnerability_found(self, vuln_type, target, details):
        """Log vulnerability discovery"""
        self.warning(f"VULNERABILITY FOUND: {vuln_type} on {target}")
        self.info(f"Details: {details}")
    
    def security_event(self, event_type, details):
        """Log security events"""
        self.critical(f"SECURITY EVENT: {event_type}")
        self.info(f"Details: {details}")
