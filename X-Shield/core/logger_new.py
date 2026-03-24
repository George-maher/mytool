"""
X-Shield Logger for MVC Architecture
Centralized logging system for the application
"""

import logging
import os
from datetime import datetime
from typing import Optional


class XShieldLogger:
    """X-Shield application logger"""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = log_level.upper()
        self.log_file = log_file or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'logs', 'xshield.log'
        )
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Setup logger
        self.setup_logger()
    
    def setup_logger(self):
        """Setup the logger configuration"""
        # Create logger
        self.logger = logging.getLogger('XShield')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(getattr(logging, self.log_level))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def set_level(self, level: str):
        """Set logging level"""
        self.log_level = level.upper()
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Update handlers
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, self.log_level))
    
    def get_log_file_path(self) -> str:
        """Get current log file path"""
        return self.log_file
    
    def cleanup(self):
        """Cleanup logger resources"""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()
    
    def module_start(self, module_name: str):
        """Log module start"""
        self.logger.info(f"Module {module_name} started")
    
    def module_error(self, module_name: str, error: str):
        """Log module error"""
        self.logger.error(f"Module {module_name} error: {error}")
    
    def module_finished(self, module_name: str, results: dict):
        """Log module completion"""
        self.logger.info(f"Module {module_name} completed with {len(results.get('findings', []))} findings")
    
    def module_complete(self, module_name: str, results: dict = None):
        """Log module completion"""
        if results and isinstance(results, dict):
            self.logger.info(f"Module {module_name} completed with {len(results.get('findings', []))} findings")
        elif results:
            self.logger.info(f"Module {module_name} completed")
        else:
            self.logger.info(f"Module {module_name} completed")
