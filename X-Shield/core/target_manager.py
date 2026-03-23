"""
Central Target Manager for X-Shield MVC Architecture
Manages all targets and provides active target to scanner modules
"""

import uuid
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal
import json
import os


class Target:
    """Represents a single target"""
    
    def __init__(self, target_id: str, target_type: str, target_value: str, 
                 description: str = "", status: str = "Active"):
        self.id = target_id
        self.type = target_type  # IP Address, Domain, URL, IP Range, File
        self.value = target_value
        self.description = description
        self.status = status  # Active, Inactive, Scanning, Completed
        self.created_at = None
        self.updated_at = None
        self.scan_results = {}
        self.tags = []
        
        # Set timestamps
        import datetime
        now = datetime.datetime.now()
        self.created_at = now.isoformat()
        self.updated_at = now.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert target to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'scan_results': self.scan_results,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        """Create target from dictionary"""
        target = cls(
            data['id'], data['type'], data['value'], 
            data.get('description', ''), data.get('status', 'Active')
        )
        target.created_at = data.get('created_at', target.created_at)
        target.updated_at = data.get('updated_at', target.updated_at)
        target.scan_results = data.get('scan_results', {})
        target.tags = data.get('tags', [])
        return target
    
    def update_status(self, status: str):
        """Update target status"""
        self.status = status
        import datetime
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_scan_result(self, scanner_type: str, result: Dict[str, Any]):
        """Add scan result for this target"""
        self.scan_results[scanner_type] = result
        import datetime
        self.updated_at = datetime.datetime.now().isoformat()


class TargetManager(QObject):
    """Central target management system"""
    
    # Signals
    target_added = Signal(str, dict)  # target_id, target_data
    target_removed = Signal(str)       # target_id
    target_updated = Signal(str, dict)  # target_id, target_data
    active_target_changed = Signal(str, dict)  # target_id, target_data
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.targets: Dict[str, Target] = {}
        self.active_target_id: Optional[str] = None
        self.data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'data', 'targets.json')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Load existing targets
        self.load_targets()
        
        self.logger.info("Target Manager initialized")
    
    def add_target(self, target_type: str, target_value: str, 
                   description: str = "", tags: List[str] = None) -> str:
        """Add a new target"""
        target_id = str(uuid.uuid4())
        
        target = Target(target_id, target_type, target_value, description)
        if tags:
            target.tags = tags
        
        self.targets[target_id] = target
        
        # Set as active if no active target
        if self.active_target_id is None:
            self.set_active_target(target_id)
        
        # Save targets
        self.save_targets()
        
        # Emit signal
        self.target_added.emit(target_id, target.to_dict())
        
        self.logger.info(f"Target added: {target_value} ({target_type})")
        return target_id
    
    def remove_target(self, target_id: str) -> bool:
        """Remove a target"""
        if target_id not in self.targets:
            return False
        
        del self.targets[target_id]
        
        # If this was the active target, set a new one
        if self.active_target_id == target_id:
            self.active_target_id = None
            if self.targets:
                # Set first available target as active
                self.active_target_id = next(iter(self.targets))
                self.active_target_changed.emit(self.active_target_id, 
                                              self.targets[self.active_target_id].to_dict())
        
        # Save targets
        self.save_targets()
        
        # Emit signal
        self.target_removed.emit(target_id)
        
        self.logger.info(f"Target removed: {target_id}")
        return True
    
    def update_target(self, target_id: str, **kwargs) -> bool:
        """Update target properties"""
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        
        # Update properties
        if 'type' in kwargs:
            target.type = kwargs['type']
        if 'value' in kwargs:
            target.value = kwargs['value']
        if 'description' in kwargs:
            target.description = kwargs['description']
        if 'status' in kwargs:
            target.update_status(kwargs['status'])
        if 'tags' in kwargs:
            target.tags = kwargs['tags']
        
        # Update timestamp
        import datetime
        target.updated_at = datetime.datetime.now().isoformat()
        
        # Save targets
        self.save_targets()
        
        # Emit signal
        self.target_updated.emit(target_id, target.to_dict())
        
        self.logger.info(f"Target updated: {target_id}")
        return True
    
    def set_active_target(self, target_id: str) -> bool:
        """Set the active target"""
        if target_id not in self.targets:
            return False
        
        old_active_id = self.active_target_id
        self.active_target_id = target_id
        
        # Emit signal
        self.active_target_changed.emit(target_id, self.targets[target_id].to_dict())
        
        self.logger.info(f"Active target changed from {old_active_id} to {target_id}")
        return True
    
    def get_active_target(self) -> Optional[Target]:
        """Get the currently active target"""
        if self.active_target_id and self.active_target_id in self.targets:
            return self.targets[self.active_target_id]
        return None
    
    def get_active_target_info(self) -> Optional[Dict[str, Any]]:
        """Get active target information as dictionary"""
        target = self.get_active_target()
        return target.to_dict() if target else None
    
    def get_target(self, target_id: str) -> Optional[Target]:
        """Get target by ID"""
        return self.targets.get(target_id)
    
    def get_all_targets(self) -> List[Target]:
        """Get all targets"""
        return list(self.targets.values())
    
    def get_targets_by_type(self, target_type: str) -> List[Target]:
        """Get targets by type"""
        return [target for target in self.targets.values() if target.type == target_type]
    
    def get_targets_by_status(self, status: str) -> List[Target]:
        """Get targets by status"""
        return [target for target in self.targets.values() if target.status == status]
    
    def search_targets(self, query: str) -> List[Target]:
        """Search targets by value or description"""
        query = query.lower()
        results = []
        
        for target in self.targets.values():
            if (query in target.value.lower() or 
                query in target.description.lower() or
                any(query in tag.lower() for tag in target.tags)):
                results.append(target)
        
        return results
    
    def get_target_statistics(self) -> Dict[str, Any]:
        """Get target statistics"""
        total = len(self.targets)
        by_type = {}
        by_status = {}
        
        for target in self.targets.values():
            # Count by type
            by_type[target.type] = by_type.get(target.type, 0) + 1
            
            # Count by status
            by_status[target.status] = by_status.get(target.status, 0) + 1
        
        return {
            'total': total,
            'active': len(self.get_targets_by_status('Active')),
            'by_type': by_type,
            'by_status': by_status,
            'active_target_id': self.active_target_id
        }
    
    def save_targets(self):
        """Save targets to file"""
        try:
            data = {
                'targets': [target.to_dict() for target in self.targets.values()],
                'active_target_id': self.active_target_id
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save targets: {e}")
    
    def load_targets(self):
        """Load targets from file"""
        try:
            if not os.path.exists(self.data_file):
                return
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Load targets
            self.targets = {}
            for target_data in data.get('targets', []):
                target = Target.from_dict(target_data)
                self.targets[target.id] = target
            
            # Set active target
            self.active_target_id = data.get('active_target_id')
            if self.active_target_id and self.active_target_id not in self.targets:
                self.active_target_id = None
            
            self.logger.info(f"Loaded {len(self.targets)} targets from file")
            
        except Exception as e:
            self.logger.error(f"Failed to load targets: {e}")
    
    def export_targets(self, file_path: str) -> bool:
        """Export targets to file"""
        try:
            data = {
                'exported_at': str(datetime.datetime.now()),
                'targets': [target.to_dict() for target in self.targets.values()],
                'statistics': self.get_target_statistics()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Targets exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export targets: {e}")
            return False
    
    def import_targets(self, file_path: str) -> int:
        """Import targets from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            for target_data in data.get('targets', []):
                # Generate new ID to avoid conflicts
                target_data['id'] = str(uuid.uuid4())
                target = Target.from_dict(target_data)
                self.targets[target.id] = target
                imported_count += 1
            
            # Save imported targets
            self.save_targets()
            
            # Emit signals for imported targets
            for target in self.targets.values():
                self.target_added.emit(target.id, target.to_dict())
            
            self.logger.info(f"Imported {imported_count} targets from {file_path}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Failed to import targets: {e}")
            return 0
    
    def cleanup(self):
        """Cleanup resources"""
        self.save_targets()
        self.logger.info("Target Manager cleanup completed")
