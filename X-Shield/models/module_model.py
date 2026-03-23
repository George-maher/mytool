"""
Module Model for X-Shield Framework
MVC Model for module management and configuration
"""

import json
import os
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class ModuleInfo:
    """Information about a loaded module"""
    
    def __init__(self, module_class: Type, module_path: str):
        self.class_name = module_class.__name__
        self.module_path = module_path
        self.name = getattr(module_class, 'NAME', 'Unknown Module')
        self.description = getattr(module_class, 'DESCRIPTION', '')
        self.version = getattr(module_class, 'VERSION', '1.0.0')
        self.author = getattr(module_class, 'AUTHOR', 'Unknown')
        self.category = getattr(module_class, 'CATEGORY', 'General')
        self.parameters = getattr(module_class, 'PARAMETERS', {})
        self.dependencies = getattr(module_class, 'DEPENDENCIES', [])
        self.is_loaded = False
        self.instance = None
        self.load_time = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'class_name': self.class_name,
            'module_path': self.module_path,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'category': self.category,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'is_loaded': self.is_loaded,
            'load_time': self.load_time,
            'error': self.error
        }


class ModuleModel(BaseModel):
    """Model for managing scanner modules"""
    
    def __init__(self, modules_dir: str = "modules", storage_path: str = "data/modules.json"):
        super().__init__()
        self.modules_dir = Path(modules_dir)
        self.storage_path = storage_path
        self._data = {
            'modules': {},
            'categories': [
                'Network', 'Web', 'Intelligence', 'Attack', 'General'
            ],
            'loaded_modules': {},
            'module_configs': {},
            'last_updated': None
        }
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure directories exist"""
        os.makedirs(self.modules_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def discover_modules(self) -> List[ModuleInfo]:
        """Discover all available modules"""
        discovered_modules = []
        
        if not self.modules_dir.exists():
            return discovered_modules
        
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and (module_dir / '__init__.py').exists():
                module_path = module_dir / '__init__.py'
                try:
                    module_info = self._load_module_info(module_path)
                    if module_info:
                        discovered_modules.append(module_info)
                        self._data['modules'][module_info.name] = module_info.to_dict()
                except Exception as e:
                    print(f"Error loading module info from {module_path}: {e}")
        
        self._data['last_updated'] = self._get_current_time()
        self.set_data(self._data)
        
        return discovered_modules
    
    def _load_module_info(self, module_path: Path) -> Optional[ModuleInfo]:
        """Load module information from file"""
        spec = importlib.util.spec_from_file_location(
            module_path.stem, module_path
        )
        
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the Module class
        module_class = None
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                name == 'Module' and 
                hasattr(obj, 'NAME')):
                module_class = obj
                break
        
        if module_class is None:
            return None
        
        return ModuleInfo(module_class, str(module_path))
    
    def load_module(self, module_name: str) -> bool:
        """Load a specific module"""
        if module_name not in self._data['modules']:
            return False
        
        module_data = self._data['modules'][module_name]
        module_path = module_data['module_path']
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                module_name, module_path
            )
            
            if spec is None or spec.loader is None:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate the Module class
            module_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    name == 'Module' and 
                    hasattr(obj, 'NAME')):
                    module_class = obj
                    break
            
            if module_class is None:
                return False
            
            # Create instance
            from core.logger import Logger
            logger = Logger()
            module_instance = module_class(logger)
            
            # Update module data
            module_data['is_loaded'] = True
            module_data['load_time'] = self._get_current_time()
            module_data['error'] = None
            
            self._data['loaded_modules'][module_name] = {
                'instance': module_instance,
                'class': module_class,
                'loaded_at': self._get_current_time()
            }
            
            self._data['last_updated'] = self._get_current_time()
            self.set_data(self._data)
            
            # Emit event
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.MODULE_LOADED, {
                    'name': module_name,
                    'info': module_data
                }, 'ModuleModel')
            
            return True
            
        except Exception as e:
            module_data['is_loaded'] = False
            module_data['error'] = str(e)
            self._data['last_updated'] = self._get_current_time()
            self.set_data(self._data)
            
            # Emit error event
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.MODULE_ERROR, {
                    'name': module_name,
                    'error': str(e)
                }, 'ModuleModel')
            
            return False
    
    def unload_module(self, module_name: str) -> bool:
        """Unload a specific module"""
        if module_name not in self._data['loaded_modules']:
            return False
        
        # Remove from loaded modules
        del self._data['loaded_modules'][module_name]
        
        # Update module data
        if module_name in self._data['modules']:
            self._data['modules'][module_name]['is_loaded'] = False
            self._data['modules'][module_name]['load_time'] = None
        
        self._data['last_updated'] = self._get_current_time()
        self.set_data(self._data)
        
        return True
    
    def get_module_instance(self, module_name: str) -> Optional[Any]:
        """Get loaded module instance"""
        if module_name in self._data['loaded_modules']:
            return self._data['loaded_modules'][module_name]['instance']
        return None
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get module information"""
        return self._data['modules'].get(module_name)
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all module information"""
        return self._data['modules'].copy()
    
    def get_loaded_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get only loaded modules"""
        loaded = {}
        for name, info in self._data['modules'].items():
            if info.get('is_loaded', False):
                loaded[name] = info
        return loaded
    
    def get_modules_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get modules by category"""
        return {
            name: info for name, info in self._data['modules'].items()
            if info.get('category') == category
        }
    
    def get_module_categories(self) -> List[str]:
        """Get all module categories"""
        categories = set()
        for info in self._data['modules'].values():
            categories.add(info.get('category', 'General'))
        return sorted(list(categories))
    
    def validate_module_parameters(self, module_name: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate module parameters"""
        module_info = self.get_module_info(module_name)
        if not module_info:
            return False, "Module not found"
        
        module_params = module_info.get('parameters', {})
        
        # Check required parameters
        for param_name, param_config in module_params.items():
            if param_config.get('required', False) and param_name not in parameters:
                return False, f"Required parameter '{param_name}' is missing"
            
            # Validate parameter type
            if param_name in parameters:
                param_type = param_config.get('type', 'string')
                value = parameters[param_name]
                
                if param_type == 'integer':
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        return False, f"Parameter '{param_name}' must be an integer"
                
                elif param_type == 'float':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        return False, f"Parameter '{param_name}' must be a float"
                
                elif param_type == 'boolean':
                    if not isinstance(value, bool):
                        return False, f"Parameter '{param_name}' must be a boolean"
                
                elif param_type == 'choice':
                    choices = param_config.get('choices', [])
                    if value not in choices:
                        return False, f"Parameter '{param_name}' must be one of: {choices}"
        
        return True, "Parameters are valid"
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Get module configuration"""
        return self._data['module_configs'].get(module_name, {})
    
    def set_module_config(self, module_name: str, config: Dict[str, Any]) -> None:
        """Set module configuration"""
        self._data['module_configs'][module_name] = config
        self._data['last_updated'] = self._get_current_time()
        self.set_data(self._data)
    
    def reload_module(self, module_name: str) -> bool:
        """Reload a module"""
        # Unload first
        self.unload_module(module_name)
        
        # Load again
        return self.load_module(module_name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get module statistics"""
        stats = {
            'total_modules': len(self._data['modules']),
            'loaded_modules': len(self._data['loaded_modules']),
            'by_category': {},
            'by_status': {
                'loaded': 0,
                'failed': 0,
                'not_loaded': 0
            },
            'total_parameters': 0,
            'modules_with_errors': 0
        }
        
        for name, info in self._data['modules'].items():
            category = info.get('category', 'General')
            
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
            
            # Count by status
            if info.get('is_loaded', False):
                stats['by_status']['loaded'] += 1
            elif info.get('error'):
                stats['by_status']['failed'] += 1
                stats['modules_with_errors'] += 1
            else:
                stats['by_status']['not_loaded'] += 1
            
            # Count parameters
            params = info.get('parameters', {})
            stats['total_parameters'] += len(params)
        
        return stats
    
    def export_module_list(self, file_path: str) -> bool:
        """Export module list to file"""
        try:
            export_data = {
                'exported_at': self._get_current_time(),
                'version': '1.0',
                'modules': self.get_all_modules(),
                'categories': self.get_module_categories()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self._errors.append(f"Export failed: {str(e)}")
            return False
    
    def _get_current_time(self) -> str:
        """Get current time as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save modules to file"""
        try:
            # Don't save module instances (only metadata)
            save_data = {
                'modules': self._data['modules'],
                'categories': self._data['categories'],
                'module_configs': self._data['module_configs'],
                'last_updated': self._data['last_updated']
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load modules from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                if isinstance(loaded_data, dict):
                    self._data.update(loaded_data)
                    # Ensure required keys
                    if 'modules' not in self._data:
                        self._data['modules'] = {}
                    if 'loaded_modules' not in self._data:
                        self._data['loaded_modules'] = {}
                    if 'module_configs' not in self._data:
                        self._data['module_configs'] = {}
                    
                    # Discover modules on load
                    self.discover_modules()
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate module data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        required_keys = ['modules', 'categories', 'loaded_modules']
        for key in required_keys:
            if key not in self._data:
                self._errors.append(f"Missing required key: {key}")
                return False
            if not isinstance(self._data[key], dict):
                self._errors.append(f"Key {key} must be a dictionary")
                return False
        
        # Validate module entries
        for name, info in self._data['modules'].items():
            if not isinstance(info, dict):
                self._errors.append(f"Module {name} must be a dictionary")
                continue
            
            required_fields = ['name', 'description', 'version', 'category']
            for field in required_fields:
                if field not in info:
                    self._errors.append(f"Module {name} missing required field: {field}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
