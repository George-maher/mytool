"""
Global Target Store for X-Shield Framework
Manages targets across all modules and pages
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal


class Target:
    """Represents a single target"""
    
    def __init__(self, name: str, target_type: str, value: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = target_type  # 'ip', 'url', 'domain', 'file', 'range'
        self.value = value
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.last_scanned = None
        self.scan_count = 0
        self.tags = []
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert target to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at,
            'last_scanned': self.last_scanned,
            'scan_count': self.scan_count,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        """Create target from dictionary"""
        target = cls(data['name'], data['type'], data['value'], data.get('description', ''))
        target.id = data['id']
        target.created_at = data['created_at']
        target.last_scanned = data.get('last_scanned')
        target.scan_count = data.get('scan_count', 0)
        target.tags = data.get('tags', [])
        target.metadata = data.get('metadata', {})
        return target
    
    def update_scan_info(self):
        """Update scan information"""
        self.last_scanned = datetime.now().isoformat()
        self.scan_count += 1
    
    def add_tag(self, tag: str):
        """Add tag to target"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove tag from target"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)


class TargetStore(QObject):
    """Global target store managing all targets"""
    
    # Signals
    target_added = Signal(Target)
    target_removed = Signal(str)  # target id
    target_updated = Signal(Target)
    targets_updated = Signal()
    targets_cleared = Signal()
    
    def __init__(self):
        super().__init__()
        self.targets: Dict[str, Target] = {}  # target_id -> Target
        self.value_to_id: Dict[str, str] = {}  # value -> target_id mapping
        
    def add_target(self, name: str, target_type: str, value: str, description: str = "") -> bool:
        """Add a new target
        
        Args:
            name: Target display name
            target_type: Type of target ('ip', 'url', 'domain', 'file', 'range')
            value: Target value (IP address, URL, etc.)
            description: Optional description
            
        Returns:
            True if added successfully, False if target already exists
        """
        # Check if target already exists
        if value in self.value_to_id:
            return False
        
        # Create new target
        target = Target(name, target_type, value, description)
        
        # Add to store
        self.targets[target.id] = target
        self.value_to_id[value] = target.id
        
        # Emit signals
        self.target_added.emit(target)
        self.targets_updated.emit()
        
        return True
    
    def remove_target(self, target_value: str) -> bool:
        """Remove target by value
        
        Args:
            target_value: Target value to remove
            
        Returns:
            True if removed successfully, False if target not found
        """
        if target_value not in self.value_to_id:
            return False
        
        target_id = self.value_to_id[target_value]
        target = self.targets[target_id]
        
        # Remove from store
        del self.targets[target_id]
        del self.value_to_id[target_value]
        
        # Emit signals
        self.target_removed.emit(target_id)
        self.targets_updated.emit()
        
        return True
    
    def remove_target_by_id(self, target_id: str) -> bool:
        """Remove target by ID
        
        Args:
            target_id: Target ID to remove
            
        Returns:
            True if removed successfully, False if target not found
        """
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        
        # Remove from store
        del self.targets[target_id]
        del self.value_to_id[target.value]
        
        # Emit signals
        self.target_removed.emit(target_id)
        self.targets_updated.emit()
        
        return True
    
    def get_target(self, target_value: str) -> Optional[Target]:
        """Get target by value"""
        if target_value not in self.value_to_id:
            return None
        
        target_id = self.value_to_id[target_value]
        return self.targets[target_id]
    
    def get_target_by_id(self, target_id: str) -> Optional[Target]:
        """Get target by ID"""
        return self.targets.get(target_id)
    
    def get_all_targets(self) -> List[Target]:
        """Get all targets"""
        return list(self.targets.values())
    
    def get_targets_by_type(self, target_type: str) -> List[Target]:
        """Get targets by type"""
        return [target for target in self.targets.values() if target.type == target_type]
    
    def update_target(self, target_id: str, **kwargs) -> bool:
        """Update target properties
        
        Args:
            target_id: Target ID to update
            **kwargs: Properties to update
            
        Returns:
            True if updated successfully, False if target not found
        """
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)
        
        # Update value mapping if value changed
        if 'value' in kwargs:
            # Remove old mapping
            old_value = None
            for val, tid in list(self.value_to_id.items()):
                if tid == target_id:
                    old_value = val
                    break
            
            if old_value:
                del self.value_to_id[old_value]
            
            # Add new mapping
            self.value_to_id[target.value] = target_id
        
        # Emit signals
        self.target_updated.emit(target)
        self.targets_updated.emit()
        
        return True
    
    def clear_all_targets(self):
        """Clear all targets"""
        self.targets.clear()
        self.value_to_id.clear()
        self.targets_cleared.emit()
    
    def get_target_count(self) -> int:
        """Get total target count"""
        return len(self.targets)
    
    def get_target_count_by_type(self, target_type: str) -> int:
        """Get target count by type"""
        return len(self.get_targets_by_type(target_type))
    
    def search_targets(self, query: str) -> List[Target]:
        """Search targets by name, value, or description"""
        query = query.lower()
        results = []
        
        for target in self.targets.values():
            if (query in target.name.lower() or 
                query in target.value.lower() or 
                query in target.description.lower() or
                any(query in tag.lower() for tag in target.tags)):
                results.append(target)
        
        return results
    
    def get_target_values(self) -> List[str]:
        """Get all target values for combo boxes"""
        return list(self.value_to_id.keys())
    
    def get_target_names(self) -> List[str]:
        """Get all target names"""
        return [target.name for target in self.targets.values()]
    
    def validate_target(self, target_type: str, value: str) -> bool:
        """Validate target value based on type"""
        import re
        import ipaddress
        
        if target_type == 'ip':
            try:
                ipaddress.ip_address(value)
                return True
            except ValueError:
                return False
        
        elif target_type == 'range':
            # Check CIDR notation
            try:
                ipaddress.ip_network(value, strict=False)
                return True
            except ValueError:
                # Check range format (x.x.x.x-y.y.y.y)
                range_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
                return bool(re.match(range_pattern, value))
        
        elif target_type == 'domain':
            # Basic domain validation
            domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            return bool(re.match(domain_pattern, value))
        
        elif target_type == 'url':
            # Basic URL validation
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return bool(re.match(url_pattern, value))
        
        elif target_type == 'file':
            # Check if file path exists (basic check)
            import os
            return os.path.exists(value)
        
        return False
    
    def export_targets(self, filepath: str) -> bool:
        """Export targets to JSON file"""
        try:
            data = {
                'targets': [target.to_dict() for target in self.targets.values()],
                'exported_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def import_targets(self, filepath: str) -> int:
        """Import targets from JSON file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Number of targets imported
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            
            for target_data in data.get('targets', []):
                target = Target.from_dict(target_data)
                
                # Don't import if already exists
                if target.value not in self.value_to_id:
                    self.targets[target.id] = target
                    self.value_to_id[target.value] = target.id
                    imported_count += 1
            
            if imported_count > 0:
                self.targets_updated.emit()
            
            return imported_count
        except Exception:
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get target statistics"""
        stats = {
            'total_targets': len(self.targets),
            'by_type': {},
            'recently_scanned': 0,
            'never_scanned': 0
        }
        
        # Count by type
        for target in self.targets.values():
            target_type = target.type
            if target_type not in stats['by_type']:
                stats['by_type'][target_type] = 0
            stats['by_type'][target_type] += 1
            
            # Scan statistics
            if target.last_scanned:
                stats['recently_scanned'] += 1
            else:
                stats['never_scanned'] += 1
        
        return stats
