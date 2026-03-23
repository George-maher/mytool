"""
Settings Model for X-Shield Framework
MVC Model for application settings and configuration
"""

import json
import os
from typing import Dict, Any, Optional

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class SettingsModel(BaseModel):
    """Model for managing application settings"""
    
    def __init__(self, storage_path: str = "data/settings.json"):
        super().__init__()
        self.storage_path = storage_path
        self._data = {
            'general': {
                'max_console_lines': 1000,
                'auto_save_reports': True,
                'report_directory': 'data/reports',
                'theme': 'dark_cyan',
                'language': 'en'
            },
            'scanner': {
                'default_threads': 5,
                'default_timeout': 30,
                'auto_chain': True,
                'parallel_scans': False
            },
            'api': {
                'shodan_key': '',
                'virustotal_key': '',
                'custom_endpoints': '{}'
            },
            'ui': {
                'font_size': 12,
                'enable_animations': True,
                'window_geometry': '',
                'sidebar_width': 280
            },
            'advanced': {
                'debug_mode': False,
                'log_level': 'INFO',
                'database_path': 'data/xshield.db',
                'max_log_size': 10485760,  # 10MB
                'backup_enabled': True
            },
            'security': {
                'require_admin': True,
                'encrypt_reports': False,
                'session_timeout': 3600,
                'max_failed_attempts': 3
            }
        }
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self._data.get(category, {}).get(key, default)
    
    def set_setting(self, category: str, key: str, value: Any) -> None:
        """Set a specific setting value"""
        if category not in self._data:
            self._data[category] = {}
        
        old_value = self._data[category].get(key)
        self._data[category][key] = value
        self.set_data(self._data)
        
        # Emit event if value changed
        if old_value != value:
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.UI_SETTINGS_CHANGED, {
                    'category': category,
                    'key': key,
                    'value': value,
                    'old_value': old_value
                }, 'SettingsModel')
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category"""
        return self._data.get(category, {}).copy()
    
    def set_category(self, category: str, settings: Dict[str, Any]) -> None:
        """Set all settings in a category"""
        if category not in self._data:
            self._data[category] = {}
        
        self._data[category].update(settings)
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.UI_SETTINGS_CHANGED, {
                'category': category,
                'settings': settings
            }, 'SettingsModel')
    
    def reset_category(self, category: str) -> None:
        """Reset a category to defaults"""
        defaults = self._get_default_settings()
        if category in defaults:
            self._data[category] = defaults[category].copy()
            self.set_data(self._data)
            
            # Emit event
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.UI_SETTINGS_CHANGED, {
                    'category': category,
                    'reset': True
                }, 'SettingsModel')
    
    def reset_all(self) -> None:
        """Reset all settings to defaults"""
        self._data = self._get_default_settings()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.UI_SETTINGS_CHANGED, {
                'reset_all': True
            }, 'SettingsModel')
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            'general': {
                'max_console_lines': 1000,
                'auto_save_reports': True,
                'report_directory': 'data/reports',
                'theme': 'dark_cyan',
                'language': 'en'
            },
            'scanner': {
                'default_threads': 5,
                'default_timeout': 30,
                'auto_chain': True,
                'parallel_scans': False
            },
            'api': {
                'shodan_key': '',
                'virustotal_key': '',
                'custom_endpoints': '{}'
            },
            'ui': {
                'font_size': 12,
                'enable_animations': True,
                'window_geometry': '',
                'sidebar_width': 280
            },
            'advanced': {
                'debug_mode': False,
                'log_level': 'INFO',
                'database_path': 'data/xshield.db',
                'max_log_size': 10485760,
                'backup_enabled': True
            },
            'security': {
                'require_admin': True,
                'encrypt_reports': False,
                'session_timeout': 3600,
                'max_failed_attempts': 3
            }
        }
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to file"""
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'version': '1.0',
                'settings': self._data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self._errors.append(f"Export failed: {str(e)}")
            return False
    
    def import_settings(self, file_path: str, merge: bool = True) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_settings = import_data.get('settings', {})
            
            if merge:
                # Merge with existing settings
                for category, settings in imported_settings.items():
                    if category not in self._data:
                        self._data[category] = {}
                    self._data[category].update(settings)
            else:
                # Replace all settings
                self._data = imported_settings
            
            self.set_data(self._data)
            return True
            
        except Exception as e:
            self._errors.append(f"Import failed: {str(e)}")
            return False
    
    def validate_api_key(self, service: str, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return True  # Empty key is valid (optional)
        
        if service == 'shodan':
            # Shodan API keys are 32 characters alphanumeric
            return len(api_key) == 32 and api_key.isalnum()
        
        elif service == 'virustotal':
            # VirusTotal API keys are 64 characters hexadecimal
            return len(api_key) == 64 and all(c in '0123456789abcdefABCDEF' for c in api_key)
        
        return True  # Unknown service, assume valid
    
    def get_theme_settings(self) -> Dict[str, Any]:
        """Get theme-related settings"""
        return {
            'theme': self.get_setting('general', 'theme'),
            'font_size': self.get_setting('ui', 'font_size'),
            'enable_animations': self.get_setting('ui', 'enable_animations'),
            'sidebar_width': self.get_setting('ui', 'sidebar_width')
        }
    
    def get_scanner_settings(self) -> Dict[str, Any]:
        """Get scanner-related settings"""
        return {
            'default_threads': self.get_setting('scanner', 'default_threads'),
            'default_timeout': self.get_setting('scanner', 'default_timeout'),
            'auto_chain': self.get_setting('scanner', 'auto_chain'),
            'parallel_scans': self.get_setting('scanner', 'parallel_scans')
        }
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API-related settings"""
        return {
            'shodan_key': self.get_setting('api', 'shodan_key'),
            'virustotal_key': self.get_setting('api', 'virustotal_key'),
            'custom_endpoints': self.get_setting('api', 'custom_endpoints')
        }
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security-related settings"""
        return {
            'require_admin': self.get_setting('security', 'require_admin'),
            'encrypt_reports': self.get_setting('security', 'encrypt_reports'),
            'session_timeout': self.get_setting('security', 'session_timeout'),
            'max_failed_attempts': self.get_setting('security', 'max_failed_attempts')
        }
    
    def update_window_geometry(self, geometry: str) -> None:
        """Update window geometry"""
        self.set_setting('ui', 'window_geometry', geometry)
    
    def get_window_geometry(self) -> str:
        """Get window geometry"""
        return self.get_setting('ui', 'window_geometry', '')
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get_setting('advanced', 'debug_mode', False)
    
    def get_log_level(self) -> str:
        """Get log level"""
        return self.get_setting('advanced', 'log_level', 'INFO')
    
    def get_database_path(self) -> str:
        """Get database path"""
        return self.get_setting('advanced', 'database_path', 'data/xshield.db')
    
    def requires_admin(self) -> bool:
        """Check if admin privileges are required"""
        return self.get_setting('security', 'require_admin', True)
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load settings from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                if isinstance(loaded_data, dict):
                    # Merge with defaults to ensure all categories exist
                    defaults = self._get_default_settings()
                    for category, default_settings in defaults.items():
                        if category not in loaded_data:
                            loaded_data[category] = default_settings.copy()
                        else:
                            # Ensure all default keys exist
                            for key, default_value in default_settings.items():
                                if key not in loaded_data[category]:
                                    loaded_data[category][key] = default_value
                    
                    self._data = loaded_data
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate settings data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        # Validate required categories
        required_categories = ['general', 'scanner', 'api', 'ui', 'advanced', 'security']
        for category in required_categories:
            if category not in self._data:
                self._errors.append(f"Missing required category: {category}")
                return False
            if not isinstance(self._data[category], dict):
                self._errors.append(f"Category {category} must be a dictionary")
                return False
        
        # Validate specific settings
        # General settings
        max_lines = self.get_setting('general', 'max_console_lines')
        if not isinstance(max_lines, int) or max_lines < 100 or max_lines > 10000:
            self._errors.append("max_console_lines must be an integer between 100 and 10000")
        
        # Scanner settings
        threads = self.get_setting('scanner', 'default_threads')
        if not isinstance(threads, int) or threads < 1 or threads > 100:
            self._errors.append("default_threads must be an integer between 1 and 100")
        
        timeout = self.get_setting('scanner', 'default_timeout')
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            self._errors.append("default_timeout must be an integer between 1 and 300")
        
        # UI settings
        font_size = self.get_setting('ui', 'font_size')
        if not isinstance(font_size, int) or font_size < 8 or font_size > 24:
            self._errors.append("font_size must be an integer between 8 and 24")
        
        # Advanced settings
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        log_level = self.get_setting('advanced', 'log_level')
        if log_level not in log_levels:
            self._errors.append(f"log_level must be one of: {', '.join(log_levels)}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
