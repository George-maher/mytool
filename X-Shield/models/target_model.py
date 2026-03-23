"""
Target Model for X-Shield Framework
MVC Model for target management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class TargetModel(BaseModel):
    """Model for managing scan targets"""
    
    def __init__(self, storage_path: str = "data/targets.json"):
        super().__init__()
        self.storage_path = storage_path
        self._data = {
            'targets': {},
            'categories': ['IP Address', 'Domain', 'URL', 'File', 'IP Range'],
            'last_updated': None
        }
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def add_target(self, name: str, target_type: str, value: str, 
                   description: str = "", tags: List[str] = None) -> str:
        """Add a new target"""
        target_id = str(uuid4())
        
        target = {
            'id': target_id,
            'name': name,
            'type': target_type,
            'value': value,
            'description': description,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'scan_count': 0,
            'last_scanned': None,
            'status': 'active',
            'metadata': {}
        }
        
        self._data['targets'][target_id] = target
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.TARGET_ADDED, target, 'TargetModel')
        
        return target_id
    
    def update_target(self, target_id: str, **kwargs) -> bool:
        """Update an existing target"""
        if target_id not in self._data['targets']:
            return False
        
        target = self._data['targets'][target_id]
        target.update(kwargs)
        target['updated_at'] = datetime.now().isoformat()
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.TARGET_UPDATED, target, 'TargetModel')
        
        return True
    
    def remove_target(self, target_id: str) -> bool:
        """Remove a target"""
        if target_id not in self._data['targets']:
            return False
        
        target = self._data['targets'].pop(target_id)
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.TARGET_REMOVED, target, 'TargetModel')
        
        return True
    
    def get_target(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Get a target by ID"""
        return self._data['targets'].get(target_id)
    
    def get_target_by_value(self, value: str) -> Optional[Dict[str, Any]]:
        """Get a target by value"""
        for target in self._data['targets'].values():
            if target['value'] == value:
                return target
        return None
    
    def get_all_targets(self) -> List[Dict[str, Any]]:
        """Get all targets"""
        return list(self._data['targets'].values())
    
    def get_targets_by_type(self, target_type: str) -> List[Dict[str, Any]]:
        """Get targets by type"""
        return [t for t in self._data['targets'].values() if t['type'] == target_type]
    
    def get_targets_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get targets by tag"""
        return [t for t in self._data['targets'].values() if tag in t.get('tags', [])]
    
    def search_targets(self, query: str) -> List[Dict[str, Any]]:
        """Search targets"""
        query = query.lower()
        results = []
        
        for target in self._data['targets'].values():
            if (query in target['name'].lower() or 
                query in target['value'].lower() or 
                query in target.get('description', '').lower() or
                any(query in tag.lower() for tag in target.get('tags', []))):
                results.append(target)
        
        return results
    
    def increment_scan_count(self, target_id: str) -> bool:
        """Increment scan count for a target"""
        if target_id not in self._data['targets']:
            return False
        
        target = self._data['targets'][target_id]
        target['scan_count'] += 1
        target['last_scanned'] = datetime.now().isoformat()
        target['updated_at'] = datetime.now().isoformat()
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get target statistics"""
        targets = list(self._data['targets'].values())
        
        stats = {
            'total_targets': len(targets),
            'by_type': {},
            'by_status': {},
            'recently_scanned': 0,
            'never_scanned': 0,
            'total_scans': 0
        }
        
        # Count by type and status
        for target in targets:
            target_type = target['type']
            status = target['status']
            
            if target_type not in stats['by_type']:
                stats['by_type'][target_type] = 0
            stats['by_type'][target_type] += 1
            
            if status not in stats['by_status']:
                stats['by_status'][status] = 0
            stats['by_status'][status] += 1
            
            # Scan statistics
            if target['last_scanned']:
                stats['recently_scanned'] += 1
            else:
                stats['never_scanned'] += 1
            
            stats['total_scans'] += target['scan_count']
        
        return stats
    
    def validate_target(self, target_type: str, value: str) -> bool:
        """Validate target value based on type"""
        import re
        import ipaddress
        
        if target_type == 'IP Address':
            try:
                ipaddress.ip_address(value)
                return True
            except ValueError:
                return False
        
        elif target_type == 'IP Range':
            try:
                ipaddress.ip_network(value, strict=False)
                return True
            except ValueError:
                # Check range format (x.x.x.x-y.y.y.y)
                range_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
                return bool(re.match(range_pattern, value))
        
        elif target_type == 'Domain':
            domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            return bool(re.match(domain_pattern, value))
        
        elif target_type == 'URL':
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return bool(re.match(url_pattern, value))
        
        elif target_type == 'File':
            return os.path.exists(value)
        
        return False
    
    def export_targets(self, file_path: str) -> bool:
        """Export targets to file"""
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'version': '1.0',
                'targets': self.get_all_targets(),
                'categories': self._data['categories']
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self._errors.append(f"Export failed: {str(e)}")
            return False
    
    def import_targets(self, file_path: str) -> int:
        """Import targets from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for target_data in import_data.get('targets', []):
                # Check if target already exists
                existing = self.get_target_by_value(target_data['value'])
                if not existing:
                    self.add_target(
                        target_data['name'],
                        target_data['type'],
                        target_data['value'],
                        target_data.get('description', ''),
                        target_data.get('tags', [])
                    )
                    imported_count += 1
            
            return imported_count
        except Exception as e:
            self._errors.append(f"Import failed: {str(e)}")
            return 0
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save targets to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load targets from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Validate loaded data
                if isinstance(loaded_data, dict) and 'targets' in loaded_data:
                    self._data = loaded_data
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate target data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        if 'targets' not in self._data:
            self._errors.append("Missing targets key")
            return False
        
        if not isinstance(self._data['targets'], dict):
            self._errors.append("Targets must be a dictionary")
            return False
        
        # Validate each target
        for target_id, target in self._data['targets'].items():
            if not isinstance(target, dict):
                self._errors.append(f"Target {target_id} must be a dictionary")
                continue
            
            required_fields = ['name', 'type', 'value']
            for field in required_fields:
                if field not in target:
                    self._errors.append(f"Target {target_id} missing required field: {field}")
            
            # Validate target type
            if 'type' in target and 'value' in target:
                if not self.validate_target(target['type'], target['value']):
                    self._errors.append(f"Invalid {target['type']}: {target['value']}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
