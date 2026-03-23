"""
Module Manager for X-Shield Framework
Handles loading, execution, and coordination of all pentesting modules
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWidgets import QMessageBox
import time


class ModuleManager(QObject):
    """Manages all pentesting modules"""
    
    # Signals
    module_started = Signal(str, str)  # module_name, target
    module_finished = Signal(str, dict)  # module_name, results
    module_error = Signal(str, str)  # module_name, error_message
    progress_updated = Signal(str, int, int)  # module_name, current, total
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.loaded_modules = {}
        self.running_modules = {}
        self.module_results = {}
        
        # Load all modules
        self.load_modules()
    
    def load_modules(self):
        """Load all available pentesting modules"""
        modules_path = Path(__file__).parent.parent / "modules"
        
        for module_dir in modules_path.iterdir():
            if module_dir.is_dir() and (module_dir / "__init__.py").exists():
                module_name = module_dir.name
                try:
                    # Import module
                    spec = importlib.util.spec_from_file_location(
                        f"modules.{module_name}",
                        module_dir / "__init__.py"
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if module has required interface
                    if hasattr(module, 'Module') and inspect.isclass(module.Module):
                        self.loaded_modules[module_name] = module.Module
                        self.logger.info(f"Loaded module: {module_name}")
                    else:
                        self.logger.warning(f"Module {module_name} missing required interface")
                        
                except Exception as e:
                    self.logger.error(f"Failed to load module {module_name}: {str(e)}")
    
    def get_available_modules(self):
        """Get list of available modules"""
        return list(self.loaded_modules.keys())
    
    def get_module_info(self, module_name):
        """Get information about a specific module"""
        if module_name not in self.loaded_modules:
            return None
        
        module_class = self.loaded_modules[module_name]
        return {
            'name': module_name,
            'description': getattr(module_class, 'DESCRIPTION', 'No description'),
            'version': getattr(module_class, 'VERSION', '1.0.0'),
            'author': getattr(module_class, 'AUTHOR', 'Unknown'),
            'parameters': getattr(module_class, 'PARAMETERS', {}),
            'category': getattr(module_class, 'CATEGORY', 'General')
        }
    
    def run_module(self, module_name, target, parameters=None):
        """Run a module in a separate thread"""
        if module_name not in self.loaded_modules:
            self.logger.error(f"Module {module_name} not found")
            return False
        
        if module_name in self.running_modules:
            self.logger.warning(f"Module {module_name} already running")
            return False
        
        try:
            # Create module instance
            module_class = self.loaded_modules[module_name]
            module_instance = module_class(self.logger)
            
            # Create thread for module execution
            thread = ModuleThread(module_instance, target, parameters or {})
            
            # Connect signals
            thread.finished.connect(
                lambda results: self.on_module_finished(module_name, results)
            )
            thread.error.connect(
                lambda error: self.on_module_error(module_name, error)
            )
            thread.progress.connect(
                lambda current, total: self.progress_updated.emit(module_name, current, total)
            )
            
            # Store and start thread
            self.running_modules[module_name] = thread
            thread.start()
            
            # Emit start signal
            self.module_started.emit(module_name, target)
            self.logger.module_start(module_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start module {module_name}: {str(e)}")
            return False
    
    def stop_module(self, module_name):
        """Stop a running module"""
        if module_name not in self.running_modules:
            return False
        
        try:
            thread = self.running_modules[module_name]
            thread.stop()
            thread.wait(5000)  # Wait up to 5 seconds
            
            del self.running_modules[module_name]
            self.logger.info(f"Stopped module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop module {module_name}: {str(e)}")
            return False
    
    def on_module_finished(self, module_name, results):
        """Handle module completion"""
        if module_name in self.running_modules:
            del self.running_modules[module_name]
        
        self.module_results[module_name] = results
        self.module_finished.emit(module_name, results)
        self.logger.module_complete(module_name)
    
    def on_module_error(self, module_name, error):
        """Handle module error"""
        if module_name in self.running_modules:
            del self.running_modules[module_name]
        
        self.module_error.emit(module_name, error)
        self.logger.module_error(module_name, error)
    
    def get_module_results(self, module_name=None):
        """Get results from completed modules"""
        if module_name:
            return self.module_results.get(module_name)
        return self.module_results.copy()
    
    def clear_results(self):
        """Clear all module results"""
        self.module_results.clear()
        self.logger.info("Cleared all module results")


class ModuleThread(QThread):
    """Thread for running modules asynchronously"""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int, int)
    
    def __init__(self, module_instance, target, parameters):
        super().__init__()
        self.module_instance = module_instance
        self.target = target
        self.parameters = parameters
        self._stop_requested = False
    
    def run(self):
        """Execute the module"""
        try:
            start_time = time.time()
            
            # Connect module signals
            if hasattr(self.module_instance, 'progress_signal'):
                self.module_instance.progress_signal.connect(
                    lambda current, total: self.progress.emit(current, total)
                )
            
            # Execute module
            results = self.module_instance.run(self.target, self.parameters)
            
            # Add execution time
            results['execution_time'] = time.time() - start_time
            results['target'] = self.target
            results['parameters'] = self.parameters
            
            if not self._stop_requested:
                self.finished.emit(results)
                
        except Exception as e:
            if not self._stop_requested:
                self.error.emit(str(e))
    
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        if hasattr(self.module_instance, 'stop'):
            self.module_instance.stop()
