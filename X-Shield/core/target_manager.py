"""
Enhanced Target Manager for X-Shield Framework v2
Improved target persistence and metadata management
"""

import uuid
import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal


class Target:
    """Represents a pentesting target with extensive metadata and scan results"""
    
    def __init__(self, target_id: str, target_type: str, target_value: str, 
                 description: str = "", status: str = "Active"):
        self.id = target_id
        self.type = target_type  # IP, Domain, URL, Network Range
        self.value = target_value
        self.description = description
        self.status = status  # Active, Inactive, Scanning, Compromised
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.scan_results = {}  # module_name -> results_dict
        self.tags = []
        self.vulnerabilities = []
        self.findings = []
        self.telemetry = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize target to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'scan_results': self.scan_results,
            'tags': self.tags,
            'vulnerabilities': self.vulnerabilities,
            'findings': self.findings,
            'telemetry': self.telemetry
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        """Create target from serialized dictionary"""
        target = cls(
            data['id'], data['type'], data['value'], 
            data.get('description', ''), data.get('status', 'Active')
        )
        target.created_at = data.get('created_at', target.created_at)
        target.updated_at = data.get('updated_at', target.updated_at)
        target.scan_results = data.get('scan_results', {})
        target.tags = data.get('tags', [])
        target.vulnerabilities = data.get('vulnerabilities', [])
        target.findings = data.get('findings', [])
        target.telemetry = data.get('telemetry', [])
        return target
    
    def update_status(self, status: str):
        """Transition target to a new state"""
        self.status = status
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_module_results(self, module_name: str, results: Dict[str, Any]):
        """Consolidate module findings and vulnerabilities into the target model"""
        self.scan_results[module_name] = results
        self.updated_at = datetime.datetime.now().isoformat()

        # Merge vulnerabilities
        if 'vulnerabilities' in results:
            for v in results['vulnerabilities']:
                if 'target' not in v:
                    v['target'] = self.value
                self.vulnerabilities.append(v)

        # Merge findings
        if 'findings' in results:
            for f in results['findings']:
                self.findings.append(f)

        # Merge telemetry
        if 'telemetry' in results:
            for t in results['telemetry']:
                self.telemetry.append(t)


class TargetManager(QObject):
    """Central repository and management system for pentesting targets"""
    
    # MVC Signals
    target_added = Signal(str, dict)  # target_id, target_data
    target_removed = Signal(str)       # target_id
    target_updated = Signal(str, dict)  # target_id, target_data
    active_target_changed = Signal(str, dict)  # target_id, target_data
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.targets: Dict[str, Target] = {}
        self.active_target_id: Optional[str] = None
        self.data_file = Path(__file__).parent.parent / 'data' / 'targets.json'
        
        # Create data directory if missing
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Hydrate from persistence layer
        self.load_targets()
        
        self.logger.info("Target Manager (v2) successfully initialized")
    
    def add_target(self, target_type: str, target_value: str, 
                   description: str = "", tags: List[str] = None) -> str:
        """Create and persist a new target"""
        target_id = str(uuid.uuid4())
        target = Target(target_id, target_type, target_value, description)
        if tags: target.tags = tags
        
        self.targets[target_id] = target
        
        # Auto-set first target as active
        if self.active_target_id is None:
            self.set_active_target(target_id)
        
        self.save_targets()
        self.target_added.emit(target_id, target.to_dict())
        
        self.logger.info(f"New Target Identified: {target_value} ({target_type})")
        return target_id
    
    def remove_target(self, target_id: str) -> bool:
        """Remove target from persistence and notify listeners"""
        if target_id not in self.targets:
            return False
        
        del self.targets[target_id]
        
        # Reset active target if removed
        if self.active_target_id == target_id:
            self.active_target_id = None
            if self.targets:
                new_id = next(iter(self.targets))
                self.set_active_target(new_id)
        
        self.save_targets()
        self.target_removed.emit(target_id)
        self.logger.info(f"Target Decommissioned: {target_id}")
        return True
    
    def update_target(self, target_id: str, **kwargs) -> bool:
        """Update target metadata or state"""
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)
        
        target.updated_at = datetime.datetime.now().isoformat()
        self.save_targets()
        self.target_updated.emit(target_id, target.to_dict())
        return True
    
    def set_active_target(self, target_id: str) -> bool:
        """Set primary focus target for application"""
        if target_id not in self.targets:
            return False
        
        self.active_target_id = target_id
        self.active_target_changed.emit(target_id, self.targets[target_id].to_dict())
        self.logger.info(f"Target Focus Switched: {target_id}")
        return True
    
    def get_active_target(self) -> Optional[Target]:
        if self.active_target_id:
            return self.targets.get(self.active_target_id)
        return None
    
    def get_all_targets(self) -> List[Target]:
        return list(self.targets.values())
    
    def get_target(self, target_id: str) -> Optional[Target]:
        return self.targets.get(target_id)

    def get_target_statistics(self) -> Dict[str, Any]:
        """Aggregate data for dashboard visualization"""
        total = len(self.targets)
        by_type = {}
        for t in self.targets.values():
            by_type[t.type] = by_type.get(t.type, 0) + 1
        
        return {
            'total': total,
            'active': total,
            'by_type': by_type,
            'active_target_id': self.active_target_id
        }
    
    def save_targets(self):
        """Persist target model to JSON storage"""
        try:
            data = {
                'targets': [t.to_dict() for t in self.targets.values()],
                'active_target_id': self.active_target_id,
                'version': '2.0.0'
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Persistence Failure: Could not save targets: {e}")
    
    def load_targets(self):
        """Hydrate target model from JSON storage"""
        try:
            if not self.data_file.exists():
                return
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            self.targets = {}
            for t_data in data.get('targets', []):
                target = Target.from_dict(t_data)
                self.targets[target.id] = target
            
            self.active_target_id = data.get('active_target_id')
            self.logger.info(f"Hydrated {len(self.targets)} targets from persistence layer")
        except Exception as e:
            self.logger.error(f"Hydration Failure: Could not load targets: {e}")
    
    def cleanup(self):
        """Ensures persistence before shutdown"""
        self.save_targets()
