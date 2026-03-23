"""
Event System for MVC Architecture
Centralized event handling and communication
"""

from typing import Any, Dict, List, Callable, Optional
from PySide6.QtCore import QObject, Signal


class Event:
    """Represents an event in the system"""
    
    def __init__(self, event_type: str, data: Any = None, source: str = None):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = None
        self._set_timestamp()
    
    def _set_timestamp(self):
        """Set event timestamp"""
        from datetime import datetime
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"Event({self.event_type}, {self.source}, {self.timestamp})"
    
    def __repr__(self):
        return self.__str__()


class EventBus(QObject):
    """Central event bus for system-wide communication"""
    
    # Qt signal for events
    event_fired = Signal(Event)
    
    def __init__(self):
        super().__init__()
        self._listeners: Dict[str, List[Callable]] = {}
        self._global_listeners: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: str, listener: Callable) -> None:
        """Subscribe to a specific event type"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type: str, listener: Callable) -> None:
        """Unsubscribe from a specific event type"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass
    
    def subscribe_all(self, listener: Callable) -> None:
        """Subscribe to all events"""
        self._global_listeners.append(listener)
    
    def unsubscribe_all(self, listener: Callable) -> None:
        """Unsubscribe from all events"""
        try:
            self._global_listeners.remove(listener)
        except ValueError:
            pass
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers"""
        # Add to history
        self._add_to_history(event)
        
        # Emit Qt signal
        self.event_fired.emit(event)
        
        # Notify specific listeners
        if event.event_type in self._listeners:
            for listener in self._listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    print(f"Error in event listener: {e}")
        
        # Notify global listeners
        for listener in self._global_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Error in global event listener: {e}")
    
    def publish_sync(self, event_type: str, data: Any = None, source: str = None) -> None:
        """Publish an event synchronously"""
        event = Event(event_type, data, source)
        self.publish(event)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """Get event history"""
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def get_listener_count(self, event_type: str = None) -> int:
        """Get number of listeners"""
        if event_type:
            return len(self._listeners.get(event_type, []))
        return sum(len(listeners) for listeners in self._listeners.values()) + len(self._global_listeners)


# Global event bus instance
event_bus = EventBus()


# Common event types
class EventTypes:
    """Standard event types for the X-Shield framework"""
    
    # Application events
    APP_STARTUP = "app.startup"
    APP_SHUTDOWN = "app.shutdown"
    APP_READY = "app.ready"
    
    # Module events
    MODULE_LOADED = "module.loaded"
    MODULE_STARTED = "module.started"
    MODULE_COMPLETED = "module.completed"
    MODULE_ERROR = "module.error"
    MODULE_PROGRESS = "module.progress"
    
    # Target events
    TARGET_ADDED = "target.added"
    TARGET_REMOVED = "target.removed"
    TARGET_UPDATED = "target.updated"
    TARGET_SELECTED = "target.selected"
    
    # Scanner events
    SCAN_STARTED = "scan.started"
    SCAN_COMPLETED = "scan.completed"
    SCAN_PROGRESS = "scan.progress"
    SCAN_ERROR = "scan.error"
    SCAN_RESULT = "scan.result"
    
    # Report events
    REPORT_GENERATED = "report.generated"
    REPORT_SAVED = "report.saved"
    REPORT_ERROR = "report.error"
    
    # UI events
    UI_PAGE_CHANGED = "ui.page_changed"
    UI_THEME_CHANGED = "ui.theme_changed"
    UI_SETTINGS_CHANGED = "ui.settings_changed"
    
    # Data events
    DATA_LOADED = "data.loaded"
    DATA_SAVED = "data.saved"
    DATA_ERROR = "data.error"
    DATA_VALIDATED = "data.validated"


class EventFilter:
    """Event filter for selective event handling"""
    
    def __init__(self, event_types: List[str] = None, sources: List[str] = None):
        self.event_types = event_types or []
        self.sources = sources or []
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria"""
        if self.event_types and event.event_type not in self.event_types:
            return False
        if self.sources and event.source not in self.sources:
            return False
        return True


class EventQueue:
    """Queue for batching events"""
    
    def __init__(self, event_bus: EventBus, batch_size: int = 10):
        self.event_bus = event_bus
        self.batch_size = batch_size
        self._queue: List[Event] = []
        self._timer = None
        self._interval = 100  # milliseconds
    
    def enqueue(self, event: Event) -> None:
        """Add event to queue"""
        self._queue.append(event)
        if len(self._queue) >= self.batch_size:
            self.flush()
        elif not self._timer:
            self._start_timer()
    
    def flush(self) -> None:
        """Flush all queued events"""
        if self._queue:
            for event in self._queue:
                self.event_bus.publish(event)
            self._queue.clear()
        self._stop_timer()
    
    def _start_timer(self):
        """Start flush timer"""
        from PySide6.QtCore import QTimer
        self._timer = QTimer()
        self._timer.timeout.connect(self.flush)
        self._timer.start(self._interval)
    
    def _stop_timer(self):
        """Stop flush timer"""
        if self._timer:
            self._timer.stop()
            self._timer = None
