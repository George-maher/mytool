"""
MVC Interfaces for X-Shield Framework
Abstract base classes defining the contract for Models, Views, and Controllers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Signal, QObject


class IModel(ABC):
    """Interface for all Model classes"""
    
    @abstractmethod
    def get_data(self) -> Any:
        """Get the model's data"""
        pass
    
    @abstractmethod
    def set_data(self, data: Any) -> None:
        """Set the model's data"""
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """Save the model's data"""
        pass
    
    @abstractmethod
    def load(self) -> bool:
        """Load the model's data"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the model's data"""
        pass


class IView(ABC):
    """Interface for all View classes"""
    
    @abstractmethod
    def update(self, data: Any) -> None:
        """Update the view with new data"""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """Show the view"""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide the view"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the view"""
        pass
    
    @abstractmethod
    def get_user_input(self) -> Any:
        """Get user input from the view"""
        pass


class IController(ABC):
    """Interface for all Controller classes"""
    
    @abstractmethod
    def handle_event(self, event_type: str, data: Any) -> None:
        """Handle events from views"""
        pass
    
    @abstractmethod
    def set_model(self, model: IModel) -> None:
        """Set the controller's model"""
        pass
    
    @abstractmethod
    def set_view(self, view: IView) -> None:
        """Set the controller's view"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the controller"""
        pass


class IObservable(ABC):
    """Interface for observable objects"""
    
    @abstractmethod
    def add_observer(self, observer: Any) -> None:
        """Add an observer"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Any) -> None:
        """Remove an observer"""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Any) -> None:
        """Notify all observers"""
        pass


class IObserver(ABC):
    """Interface for observer objects"""
    
    @abstractmethod
    def update(self, event_type: str, data: Any) -> None:
        """Handle notifications from observable"""
        pass


class IRepository(ABC):
    """Interface for data repositories"""
    
    @abstractmethod
    def create(self, entity: Any) -> Any:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def read(self, entity_id: Any) -> Optional[Any]:
        """Read an entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> bool:
        """Update an entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete an entity by ID"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Any]:
        """List all entities"""
        pass
    
    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[Any]:
        """Search entities by criteria"""
        pass


class IService(ABC):
    """Interface for service classes"""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service"""
        pass
    
    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """Validate service parameters"""
        pass
