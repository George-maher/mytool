"""
Worker class for handling long-running tasks in separate threads
"""

from PySide6.QtCore import QObject, QThread, Signal, Slot
from typing import Dict, Any


class ModuleWorker(QObject):
    """Worker for running modules in separate threads"""
    
    # Signals
    finished = Signal(dict)  # results
    error = Signal(str)  # error message
    progress = Signal(int, int)  # current, total
    status = Signal(str)  # status message
    
    def __init__(self, module_instance, target: str, parameters: Dict[str, Any]):
        super().__init__()
        self.module_instance = module_instance
        self.target = target
        self.parameters = parameters
        self._is_running = False
    
    @Slot()
    def run(self):
        """Execute the module"""
        try:
            self._is_running = True
            
            # Connect module signals to worker signals
            self.module_instance.progress_signal.connect(self.progress.emit)
            self.module_instance.status_signal.connect(self.status.emit)
            self.module_instance.finished.connect(self.finished.emit)
            
            # Execute the module
            results = self.module_instance.execute(self.target, self.parameters)
            
            if not self._is_running:
                return
                
            self.finished.emit(results)
            
        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))
    
    @Slot()
    def stop(self):
        """Stop the worker"""
        self._is_running = False
        self.module_instance.stop()


class ThreadManager(QObject):
    """Manages multiple worker threads"""
    
    def __init__(self):
        super().__init__()
        self.workers = {}
        self.threads = {}
    
    def start_worker(self, worker_id: str, worker: ModuleWorker) -> bool:
        """Start a worker in a new thread"""
        if worker_id in self.workers:
            return False
        
        # Create thread
        thread = QThread()
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.finished.connect(lambda: self.cleanup_worker(worker_id))
        worker.error.connect(lambda: self.cleanup_worker(worker_id))
        
        # Store references
        self.workers[worker_id] = worker
        self.threads[worker_id] = thread
        
        # Start thread
        thread.start()
        return True
    
    def stop_worker(self, worker_id: str) -> bool:
        """Stop a specific worker"""
        if worker_id not in self.workers:
            return False
        
        worker = self.workers[worker_id]
        worker.stop()
        return True
    
    def cleanup_worker(self, worker_id: str):
        """Clean up a finished worker"""
        if worker_id in self.threads:
            thread = self.threads[worker_id]
            thread.quit()
            thread.wait(5000)  # Wait up to 5 seconds
            del self.threads[worker_id]
        
        if worker_id in self.workers:
            del self.workers[worker_id]
    
    def is_worker_running(self, worker_id: str) -> bool:
        """Check if a worker is running"""
        return worker_id in self.workers
    
    def stop_all_workers(self):
        """Stop all running workers"""
        for worker_id in list(self.workers.keys()):
            self.stop_worker(worker_id)
