"""
Service Locator for MVC Architecture
Centralized service management and dependency injection
"""

from typing import Any, Dict, Type, Optional, Callable
from threading import Lock
import inspect


class ServiceLocator:
    """Centralized service locator for dependency injection"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, bool] = {}
        self._lock = Lock()
    
    def register(self, name: str, service: Any, singleton: bool = True) -> None:
        """Register a service instance"""
        with self._lock:
            self._services[name] = service
            self._singletons[name] = singleton
    
    def register_factory(self, name: str, factory: Callable, singleton: bool = True) -> None:
        """Register a service factory"""
        with self._lock:
            self._factories[name] = factory
            self._singletons[name] = singleton
    
    def get(self, name: str) -> Any:
        """Get a service by name"""
        with self._lock:
            # Return existing instance if it's a singleton
            if name in self._services and self._singletons.get(name, False):
                return self._services[name]
            
            # Create instance from factory
            if name in self._factories:
                factory = self._factories[name]
                instance = factory()
                
                # Store if singleton
                if self._singletons.get(name, False):
                    self._services[name] = instance
                
                return instance
            
            raise KeyError(f"Service '{name}' not found")
    
    def create(self, name: str) -> Any:
        """Create a new instance of a service (always creates new instance)"""
        with self._lock:
            if name in self._factories:
                return self._factories[name]()
            elif name in self._services:
                service_class = self._services[name]
                if inspect.isclass(service_class):
                    return service_class()
                else:
                    return service_class
            else:
                raise KeyError(f"Service '{name}' not found")
    
    def has(self, name: str) -> bool:
        """Check if a service is registered"""
        with self._lock:
            return name in self._services or name in self._factories
    
    def unregister(self, name: str) -> None:
        """Unregister a service"""
        with self._lock:
            self._services.pop(name, None)
            self._factories.pop(name, None)
            self._singletons.pop(name, None)
    
    def clear(self) -> None:
        """Clear all services"""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()
    
    def list_services(self) -> list:
        """List all registered services"""
        with self._lock:
            return list(set(self._services.keys()) | set(self._factories.keys()))


class ServiceRegistry:
    """Registry for service configuration"""
    
    def __init__(self):
        self._registrations: Dict[str, Dict[str, Any]] = {}
    
    def register_service(self, name: str, service_class: Type, 
                        singleton: bool = True, dependencies: list = None,
                        factory: Callable = None) -> None:
        """Register a service configuration"""
        self._registrations[name] = {
            'class': service_class,
            'singleton': singleton,
            'dependencies': dependencies or [],
            'factory': factory
        }
    
    def get_service_config(self, name: str) -> Dict[str, Any]:
        """Get service configuration"""
        if name not in self._registrations:
            raise KeyError(f"Service '{name}' not registered")
        return self._registrations[name]
    
    def create_service_locator(self) -> ServiceLocator:
        """Create a service locator from registry"""
        locator = ServiceLocator()
        
        # Register all services
        for name, config in self._registrations.items():
            if config['factory']:
                locator.register_factory(name, config['factory'], config['singleton'])
            else:
                # Create factory that handles dependencies
                def create_factory(service_config):
                    def factory():
                        dependencies = []
                        for dep_name in service_config['dependencies']:
                            dependencies.append(locator.get(dep_name))
                        return service_config['class'](*dependencies)
                    return factory
                
                locator.register_factory(name, create_factory(config), config['singleton'])
        
        return locator


class DependencyInjector:
    """Dependency injection utility"""
    
    def __init__(self, service_locator: ServiceLocator):
        self._service_locator = service_locator
    
    def inject_into(self, target: Any) -> None:
        """Inject dependencies into target object"""
        if inspect.isclass(target):
            self._inject_into_class(target)
        else:
            self._inject_into_instance(target)
    
    def _inject_into_class(self, target_class: Type) -> None:
        """Inject dependencies into class"""
        for name, annotation in target_class.__annotations__.items():
            if hasattr(annotation, '__origin__') and annotation.__origin__ is type:
                # Type annotation like ServiceType
                service_name = annotation.__args__[0].__name__
                if self._service_locator.has(service_name):
                    setattr(target_class, name, self._service_locator.get(service_name))
    
    def _inject_into_instance(self, instance: Any) -> None:
        """Inject dependencies into instance"""
        init_signature = inspect.signature(instance.__class__.__init__)
        
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
            
            # Check if parameter has annotation
            if param.annotation != inspect.Parameter.empty:
                service_name = param.annotation.__name__
                if self._service_locator.has(service_name):
                    setattr(instance, param_name, self._service_locator.get(service_name))


# Global service locator instance
service_locator = ServiceLocator()


# Decorators for service registration
def service(name: str = None, singleton: bool = True):
    """Decorator to register a class as a service"""
    def decorator(cls):
        service_name = name or cls.__name__
        service_locator.register(service_name, cls(), singleton)
        return cls
    return decorator


def service_factory(name: str = None, singleton: bool = True):
    """Decorator to register a factory function as a service"""
    def decorator(factory_func):
        service_name = name or factory_func.__name__
        service_locator.register_factory(service_name, factory_func, singleton)
        return factory_func
    return decorator


def inject(service_name: str):
    """Decorator to inject a service into a method"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if service_name not in kwargs:
                kwargs[service_name] = service_locator.get(service_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Context manager for service registration
class ServiceContext:
    """Context manager for temporary service registration"""
    
    def __init__(self, service_locator: ServiceLocator = None):
        self._locator = service_locator or ServiceLocator()
        self._registered_services = []
    
    def register(self, name: str, service: Any, singleton: bool = True) -> 'ServiceContext':
        """Register a service"""
        self._locator.register(name, service, singleton)
        self._registered_services.append(name)
        return self
    
    def register_factory(self, name: str, factory: Callable, singleton: bool = True) -> 'ServiceContext':
        """Register a service factory"""
        self._locator.register_factory(name, factory, singleton)
        self._registered_services.append(name)
        return self
    
    def __enter__(self) -> ServiceLocator:
        return self._locator
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up registered services
        for name in self._registered_services:
            self._locator.unregister(name)
