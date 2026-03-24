"""
Enhanced Module Manager for X-Shield Framework v2
Improved asynchronous execution and thread management
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
import time


class ModuleManager(QObject):
    """Registry and controller for X-Shield pentesting modules"""
    
    # Unified Signals
    module_started = Signal(str, str)  # module_name, target
    module_finished = Signal(str, dict)  # module_name, results
    module_error = Signal(str, str)  # module_name, error_message
    progress_updated = Signal(str, int, int)  # module_name, current, total
    log_received = Signal(str, str, str)  # module_name, level, message
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self._registry = {}  # module_name -> module_class
        self.running_threads = {}
        self.module_results = {}
        
        self.load_modules()

    @property
    def loaded_modules(self):
        return self._registry
    
    def load_modules(self):
        """Dynamic loading of modules from directory structure"""
        modules_path = Path(__file__).parent.parent / "modules"
        
        if not modules_path.exists():
            self.logger.error(f"Modules path not found: {modules_path}")
            return

        for module_dir in modules_path.iterdir():
            if module_dir.is_dir() and (module_dir / "__init__.py").exists():
                module_name = module_dir.name
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"modules.{module_name}",
                        module_dir / "__init__.py"
                    )
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'Module') and inspect.isclass(module.Module):
                        self._registry[module_name] = module.Module
                        self.logger.info(f"Successfully registered module: {module_name}")
                    else:
                        self.logger.warning(f"Validation Error: Module '{module_name}' missing 'Module' class.")
                        
                except Exception as e:
                    self.logger.error(f"Failed to load module '{module_name}': {str(e)}")
    
    def run_module(self, module_name: str, target: str, parameters: dict = None) -> bool:
        """Starts a module in a dedicated background thread"""
        if module_name not in self._registry:
            self.logger.error(f"Module '{module_name}' is not registered.")
            return False
        
        if module_name in self.running_threads:
            self.logger.warning(f"Module '{module_name}' is already running.")
            return False
        
        try:
            module_class = self._registry[module_name]
            module_instance = module_class(self.logger)
            
            # Create execution thread
            thread = ModuleThread(module_instance, target, parameters or {})
            
            # Connect module signals to manager signals
            module_instance.progress_signal.connect(self.progress_updated.emit)
            module_instance.log_signal.connect(self.log_received.emit)
            module_instance.finished.connect(self.on_thread_finished)
            
            # Start execution
            self.running_threads[module_name] = thread
            thread.start()
            
            self.module_started.emit(module_name, target)
            return True
            
        except Exception as e:
            self.logger.error(f"Execution Error: Could not start '{module_name}': {str(e)}")
            return False
    
    def stop_module(self, module_name: str):
        """Signal a running module to terminate"""
        if module_name not in self.running_threads:
            return False
        
        try:
            thread = self.running_threads[module_name]
            thread.stop()
            return True
        except Exception as e:
            self.logger.error(f"Could not stop module '{module_name}': {str(e)}")
            return False
    
    def on_thread_finished(self, module_name, results):
        """Cleanup and store results when a module finishes"""
        if module_name in self.running_threads:
            thread = self.running_threads[module_name]
            thread.quit()
            thread.wait(1000)
            del self.running_threads[module_name]
        
        self.module_results[module_name] = results
        self.module_finished.emit(module_name, results)
        self.logger.module_complete(module_name, results)
    
    def get_results(self, module_name=None):
        if module_name:
            return self.module_results.get(module_name)
        return self.module_results.copy()


class ModuleThread(QThread):
    """Background worker thread for non-blocking module execution"""
    
    def __init__(self, module_instance, target, parameters):
        super().__init__()
        self.module_instance = module_instance
        self.target = target
        self.parameters = parameters
    
    def run(self):
        """Thread entry point"""
        try:
            self.module_instance.execute(self.target, self.parameters)
        except Exception as e:
            pass
    
    def stop(self):
        """Stop the running module instance"""
        if hasattr(self.module_instance, 'stop'):
            self.module_instance.stop()
