"""
Scan Model for X-Shield Framework
MVC Model for scan management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class ScanModel(BaseModel):
    """Model for managing scan operations and results"""
    
    def __init__(self, storage_path: str = "data/scans.json"):
        super().__init__()
        self.storage_path = storage_path
        self._data = {
            'scans': {},
            'active_scans': {},
            'scan_types': [
                'Network Scanner',
                'Web Scanner', 
                'OSINT Scanner',
                'Brute Force',
                'Attack/Stress',
                'Threat Intelligence'
            ],
            'last_updated': None
        }
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def create_scan(self, scan_type: str, target: str, parameters: Dict[str, Any] = None) -> str:
        """Create a new scan"""
        scan_id = str(uuid4())
        
        scan = {
            'id': scan_id,
            'type': scan_type,
            'target': target,
            'parameters': parameters or {},
            'status': 'created',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'duration': 0,
            'results': {
                'vulnerabilities': [],
                'findings': [],
                'statistics': {},
                'raw_output': ''
            },
            'error': None,
            'metadata': {}
        }
        
        self._data['scans'][scan_id] = scan
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        return scan_id
    
    def start_scan(self, scan_id: str) -> bool:
        """Start a scan"""
        if scan_id not in self._data['scans']:
            return False
        
        scan = self._data['scans'][scan_id]
        scan['status'] = 'running'
        scan['started_at'] = datetime.now().isoformat()
        scan['progress'] = 0
        
        # Move to active scans
        self._data['active_scans'][scan_id] = scan
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.SCAN_STARTED, scan, 'ScanModel')
        
        return True
    
    def update_scan_progress(self, scan_id: str, progress: int, message: str = "") -> bool:
        """Update scan progress"""
        if scan_id not in self._data['active_scans']:
            return False
        
        scan = self._data['active_scans'][scan_id]
        scan['progress'] = max(0, min(100, progress))
        
        if message:
            scan['status_message'] = message
        
        # Update in main scans too
        if scan_id in self._data['scans']:
            self._data['scans'][scan_id].update({
                'progress': scan['progress'],
                'status_message': scan.get('status_message', '')
            })
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.SCAN_PROGRESS, {
                'scan_id': scan_id,
                'progress': progress,
                'message': message
            }, 'ScanModel')
        
        return True
    
    def add_scan_result(self, scan_id: str, result_type: str, result_data: Any) -> bool:
        """Add result to scan"""
        if scan_id not in self._data['active_scans']:
            return False
        
        scan = self._data['active_scans'][scan_id]
        
        if result_type == 'vulnerability':
            scan['results']['vulnerabilities'].append(result_data)
        elif result_type == 'finding':
            scan['results']['findings'].append(result_data)
        elif result_type == 'statistics':
            scan['results']['statistics'].update(result_data)
        elif result_type == 'raw_output':
            scan['results']['raw_output'] += str(result_data) + '\n'
        
        # Update in main scans too
        if scan_id in self._data['scans']:
            self._data['scans'][scan_id]['results'] = scan['results'].copy()
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            self._event_bus.publish_sync(EventTypes.SCAN_RESULT, {
                'scan_id': scan_id,
                'type': result_type,
                'data': result_data
            }, 'ScanModel')
        
        return True
    
    def complete_scan(self, scan_id: str, success: bool = True, error: str = None) -> bool:
        """Complete a scan"""
        if scan_id not in self._data['active_scans']:
            return False
        
        scan = self._data['active_scans'][scan_id]
        scan['status'] = 'completed' if success else 'failed'
        scan['completed_at'] = datetime.now().isoformat()
        scan['progress'] = 100
        
        if error:
            scan['error'] = error
        
        # Calculate duration
        if scan['started_at']:
            start_time = datetime.fromisoformat(scan['started_at'])
            end_time = datetime.fromisoformat(scan['completed_at'])
            scan['duration'] = (end_time - start_time).total_seconds()
        
        # Move from active to completed
        self._data['scans'][scan_id] = scan
        del self._data['active_scans'][scan_id]
        
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        # Emit event
        if hasattr(self, '_event_bus') and self._event_bus:
            event_type = EventTypes.SCAN_COMPLETED if success else EventTypes.SCAN_ERROR
            self._event_bus.publish_sync(event_type, scan, 'ScanModel')
        
        return True
    
    def stop_scan(self, scan_id: str) -> bool:
        """Stop a running scan"""
        if scan_id not in self._data['active_scans']:
            return False
        
        return self.complete_scan(scan_id, success=False, error="Scan stopped by user")
    
    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan by ID"""
        # Check active scans first
        if scan_id in self._data['active_scans']:
            return self._data['active_scans'][scan_id]
        
        # Check completed scans
        return self._data['scans'].get(scan_id)
    
    def get_all_scans(self) -> List[Dict[str, Any]]:
        """Get all scans"""
        all_scans = list(self._data['scans'].values())
        all_scans.extend(self._data['active_scans'].values())
        return all_scans
    
    def get_active_scans(self) -> List[Dict[str, Any]]:
        """Get active scans"""
        return list(self._data['active_scans'].values())
    
    def get_scans_by_target(self, target: str) -> List[Dict[str, Any]]:
        """Get scans for a specific target"""
        return [scan for scan in self.get_all_scans() if scan['target'] == target]
    
    def get_scans_by_type(self, scan_type: str) -> List[Dict[str, Any]]:
        """Get scans by type"""
        return [scan for scan in self.get_all_scans() if scan['type'] == scan_type]
    
    def get_scans_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get scans by status"""
        return [scan for scan in self.get_all_scans() if scan['status'] == status]
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scans"""
        all_scans = self.get_all_scans()
        all_scans.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return all_scans[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scan statistics"""
        all_scans = self.get_all_scans()
        
        stats = {
            'total_scans': len(all_scans),
            'active_scans': len(self._data['active_scans']),
            'by_type': {},
            'by_status': {},
            'by_target': {},
            'total_vulnerabilities': 0,
            'total_findings': 0,
            'average_duration': 0,
            'success_rate': 0
        }
        
        completed_scans = [s for s in all_scans if s['status'] == 'completed']
        successful_scans = [s for s in completed_scans if not s.get('error')]
        
        # Count by type, status, and target
        for scan in all_scans:
            scan_type = scan['type']
            status = scan['status']
            target = scan['target']
            
            if scan_type not in stats['by_type']:
                stats['by_type'][scan_type] = 0
            stats['by_type'][scan_type] += 1
            
            if status not in stats['by_status']:
                stats['by_status'][status] = 0
            stats['by_status'][status] += 1
            
            if target not in stats['by_target']:
                stats['by_target'][target] = 0
            stats['by_target'][target] += 1
            
            # Count vulnerabilities and findings
            results = scan.get('results', {})
            stats['total_vulnerabilities'] += len(results.get('vulnerabilities', []))
            stats['total_findings'] += len(results.get('findings', []))
        
        # Calculate average duration
        if completed_scans:
            total_duration = sum(s.get('duration', 0) for s in completed_scans)
            stats['average_duration'] = total_duration / len(completed_scans)
        
        # Calculate success rate
        if completed_scans:
            stats['success_rate'] = (len(successful_scans) / len(completed_scans)) * 100
        
        return stats
    
    def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan"""
        success = False
        
        # Remove from active scans
        if scan_id in self._data['active_scans']:
            del self._data['active_scans'][scan_id]
            success = True
        
        # Remove from completed scans
        if scan_id in self._data['scans']:
            del self._data['scans'][scan_id]
            success = True
        
        if success:
            self._data['last_updated'] = datetime.now().isoformat()
            self.set_data(self._data)
        
        return success
    
    def clear_completed_scans(self) -> int:
        """Clear all completed scans"""
        count = len(self._data['scans'])
        self._data['scans'].clear()
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        return count
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save scans to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load scans from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Validate loaded data
                if isinstance(loaded_data, dict):
                    self._data = loaded_data
                    # Ensure required keys
                    if 'scans' not in self._data:
                        self._data['scans'] = {}
                    if 'active_scans' not in self._data:
                        self._data['active_scans'] = {}
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate scan data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        required_keys = ['scans', 'active_scans']
        for key in required_keys:
            if key not in self._data:
                self._errors.append(f"Missing required key: {key}")
                return False
            if not isinstance(self._data[key], dict):
                self._errors.append(f"Key {key} must be a dictionary")
                return False
        
        # Validate scan objects
        all_scans = {**self._data['scans'], **self._data['active_scans']}
        for scan_id, scan in all_scans.items():
            if not isinstance(scan, dict):
                self._errors.append(f"Scan {scan_id} must be a dictionary")
                continue
            
            required_fields = ['id', 'type', 'target', 'status']
            for field in required_fields:
                if field not in scan:
                    self._errors.append(f"Scan {scan_id} missing required field: {field}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
