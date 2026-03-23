"""
Base MVC Classes for X-Shield Framework
Abstract base classes implementing common MVC patterns
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import QObject, Signal, Slot
from .interfaces import IModel, IView, IController, IObservable, IObserver
from .events import EventBus, Event, EventTypes


class BaseModel(QObject, IModel, IObservable):
    """Base class for all Model classes"""
    
    # Signals
    data_changed = Signal(object)  # new data
    data_saved = Signal()
    data_loaded = Signal()
    data_validated = Signal(bool)  # is_valid
    
    def __init__(self):
        super().__init__()
        self._data = {}
        self._observers: List[IObserver] = []
        self._is_dirty = False
        self._is_valid = True
        self._errors: List[str] = []
        
    # IModel implementation
    def get_data(self) -> Any:
        """Get the model's data"""
        return self._data.copy()
    
    def set_data(self, data: Any) -> None:
        """Set the model's data"""
        old_data = self._data.copy()
        self._data = data if isinstance(data, dict) else {}
        self._is_dirty = True
        self.data_changed.emit(self._data)
        
        # Notify observers
        if old_data != self._data:
            self.notify_observers("data_changed", self._data)
    
    def save(self) -> bool:
        """Save the model's data"""
        try:
            success = self._persist_data()
            if success:
                self._is_dirty = False
                self.data_saved.emit()
                self.notify_observers("data_saved", None)
            return success
        except Exception as e:
            self._errors.append(str(e))
            return False
    
    def load(self) -> bool:
        """Load the model's data"""
        try:
            success = self._load_data()
            if success:
                self._is_dirty = False
                self.data_loaded.emit()
                self.notify_observers("data_loaded", self._data)
            return success
        except Exception as e:
            self._errors.append(str(e))
            return False
    
    def validate(self) -> bool:
        """Validate the model's data"""
        self._errors.clear()
        is_valid = self._validate_data()
        self._is_valid = is_valid
        self.data_validated.emit(is_valid)
        self.notify_observers("data_validated", is_valid)
        return is_valid
    
    # IObservable implementation
    def add_observer(self, observer: IObserver) -> None:
        """Add an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: IObserver) -> None:
        """Remove an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Any) -> None:
        """Notify all observers"""
        for observer in self._observers:
            observer.update(event_type, data)
    
    # Abstract methods to be implemented by subclasses
    def _persist_data(self) -> bool:
        """Persist data to storage (to be implemented)"""
        return True
    
    def _load_data(self) -> bool:
        """Load data from storage (to be implemented)"""
        return True
    
    def _validate_data(self) -> bool:
        """Validate data (to be implemented)"""
        return True
    
    # Helper methods
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property from data"""
        return self._data.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """Set a property in data"""
        if key not in self._data or self._data[key] != value:
            self._data[key] = value
            self._is_dirty = True
            self.data_changed.emit(self._data)
            self.notify_observers("property_changed", {key: value})
    
    def is_dirty(self) -> bool:
        """Check if model has unsaved changes"""
        return self._is_dirty
    
    def is_valid(self) -> bool:
        """Check if model data is valid"""
        return self._is_valid
    
    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self._errors.copy()
    
    def clear_errors(self) -> None:
        """Clear all errors"""
        self._errors.clear()


class BaseView(QObject, IView, IObserver):
    """Base class for all View classes"""
    
    # Signals
    user_action = Signal(str, object)  # action_type, data
    view_closed = Signal()
    view_shown = Signal()
    
    def __init__(self):
        super().__init__()
        self._controller = None
        self._is_visible = False
        self._data = None
    
    # IView implementation
    def update(self, event_type: str, data: Any) -> None:
        """Handle model updates"""
        if event_type == "data_changed":
            self._data = data
            self.refresh_view()
        elif event_type == "data_loaded":
            self._data = data
            self.refresh_view()
        elif event_type == "data_saved":
            self.on_data_saved()
        elif event_type == "data_validated":
            self.on_data_validated(data)
    
    def show(self) -> None:
        """Show the view"""
        self._is_visible = True
        self.on_show()
        self.view_shown.emit()
    
    def hide(self) -> None:
        """Hide the view"""
        self._is_visible = False
        self.on_hide()
    
    def clear(self) -> None:
        """Clear the view"""
        self._data = None
        self.on_clear()
    
    def get_user_input(self) -> Any:
        """Get user input from the view"""
        return self._collect_user_input()
    
    # Controller management
    def set_controller(self, controller: 'BaseController') -> None:
        """Set the view's controller"""
        self._controller = controller
    
    def get_controller(self) -> 'BaseController':
        """Get the view's controller"""
        return self._controller
    
    # Event handling
    def emit_user_action(self, action_type: str, data: Any = None) -> None:
        """Emit user action event"""
        self.user_action.emit(action_type, data)
        if self._controller:
            self._controller.handle_event(action_type, data)
    
    # Abstract methods to be implemented by subclasses
    def refresh_view(self) -> None:
        """Refresh the view with current data (to be implemented)"""
        pass
    
    def on_show(self) -> None:
        """Called when view is shown (to be implemented)"""
        pass
    
    def on_hide(self) -> None:
        """Called when view is hidden (to be implemented)"""
        pass
    
    def on_clear(self) -> None:
        """Called when view is cleared (to be implemented)"""
        pass
    
    def on_data_saved(self) -> None:
        """Called when data is saved (to be implemented)"""
        pass
    
    def on_data_validated(self, is_valid: bool) -> None:
        """Called when data is validated (to be implemented)"""
        pass
    
    def _collect_user_input(self) -> Any:
        """Collect user input (to be implemented)"""
        return None
    
    # Helper methods
    def is_visible(self) -> bool:
        """Check if view is visible"""
        return self._is_visible
    
    def get_data(self) -> Any:
        """Get current view data"""
        return self._data


class BaseController(QObject, IController, IObserver):
    """Base class for all Controller classes"""
    
    # Signals
    controller_ready = Signal()
    controller_error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._view = None
        self._event_bus = None
        self._is_initialized = False
    
    # IController implementation
    def handle_event(self, event_type: str, data: Any) -> None:
        """Handle events from views"""
        try:
            self._process_event(event_type, data)
        except Exception as e:
            self.controller_error.emit(str(e))
    
    def set_model(self, model: BaseModel) -> None:
        """Set the controller's model"""
        if self._model:
            self._model.remove_observer(self)
        self._model = model
        self._model.add_observer(self)
    
    def set_view(self, view: BaseView) -> None:
        """Set the controller's view"""
        self._view = view
        self._view.set_controller(self)
    
    def initialize(self) -> None:
        """Initialize the controller"""
        if not self._is_initialized:
            self._initialize_components()
            self._is_initialized = True
            self.controller_ready.emit()
    
    # IObserver implementation
    def update(self, event_type: str, data: Any) -> None:
        """Handle model updates"""
        if event_type == "data_changed":
            self.on_model_data_changed(data)
        elif event_type == "data_saved":
            self.on_model_data_saved()
        elif event_type == "data_loaded":
            self.on_model_data_loaded()
        elif event_type == "data_validated":
            self.on_model_data_validated(data)
    
    # Event bus management
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Set the event bus"""
        self._event_bus = event_bus
    
    def publish_event(self, event_type: str, data: Any = None) -> None:
        """Publish an event to the event bus"""
        if self._event_bus:
            self._event_bus.publish_sync(event_type, data, self.__class__.__name__)
    
    def subscribe_to_event(self, event_type: str, handler: callable) -> None:
        """Subscribe to an event"""
        if self._event_bus:
            self._event_bus.subscribe(event_type, handler)
    
    # Abstract methods to be implemented by subclasses
    def _process_event(self, event_type: str, data: Any) -> None:
        """Process an event (to be implemented)"""
        pass
    
    def _initialize_components(self) -> None:
        """Initialize controller components (to be implemented)"""
        pass
    
    # Event handlers
    def on_model_data_changed(self, data: Any) -> None:
        """Handle model data changes"""
        if self._view:
            self._view.update("data_changed", data)
    
    def on_model_data_saved(self) -> None:
        """Handle model data save"""
        if self._view:
            self._view.update("data_saved", None)
    
    def on_model_data_loaded(self) -> None:
        """Handle model data load"""
        if self._view:
            self._view.update("data_loaded", self._model.get_data())
    
    def on_model_data_validated(self, is_valid: bool) -> None:
        """Handle model data validation"""
        if self._view:
            self._view.update("data_validated", is_valid)
    
    # Helper methods
    def get_model(self) -> BaseModel:
        """Get the controller's model"""
        return self._model
    
    def get_view(self) -> BaseView:
        """Get the controller's view"""
        return self._view
    
    def is_initialized(self) -> bool:
        """Check if controller is initialized"""
        return self._is_initialized
    
    def execute_model_action(self, action: str, *args, **kwargs) -> Any:
        """Execute an action on the model"""
        if self._model and hasattr(self._model, action):
            return getattr(self._model, action)(*args, **kwargs)
        return None
    
    def update_view(self, *args, **kwargs) -> None:
        """Update the view"""
        if self._view and hasattr(self._view, 'update'):
            self._view.update(*args, **kwargs)
