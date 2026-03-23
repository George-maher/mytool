"""
User Model for X-Shield Framework
MVC Model for user management and authentication
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class User:
    """User entity"""
    
    def __init__(self, user_id: str, username: str, email: str = "", role: str = "user"):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        self.login_count = 0
        self.is_active = True
        self.preferences = {}
        self.permissions = self._get_default_permissions(role)
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions based on role"""
        if role == "admin":
            return [
                "scan_all", "manage_targets", "generate_reports", 
                "manage_users", "manage_settings", "view_all"
            ]
        elif role == "analyst":
            return [
                "scan_all", "manage_targets", "generate_reports", "view_all"
            ]
        elif role == "operator":
            return [
                "scan_basic", "view_own", "generate_basic_reports"
            ]
        else:  # user
            return [
                "view_own", "scan_own_targets"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'login_count': self.login_count,
            'is_active': self.is_active,
            'preferences': self.preferences,
            'permissions': self.permissions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        user = cls(data['id'], data['username'], data.get('email', ''), data.get('role', 'user'))
        user.created_at = data.get('created_at', user.created_at)
        user.last_login = data.get('last_login')
        user.login_count = data.get('login_count', 0)
        user.is_active = data.get('is_active', True)
        user.preferences = data.get('preferences', {})
        user.permissions = data.get('permissions', user.permissions)
        return user


class UserModel(BaseModel):
    """Model for managing users and authentication"""
    
    def __init__(self, storage_path: str = "data/users.json"):
        super().__init__()
        self.storage_path = storage_path
        self._data = {
            'users': {},
            'sessions': {},
            'roles': ['admin', 'analyst', 'operator', 'user'],
            'default_role': 'user',
            'session_timeout': 3600,  # 1 hour
            'max_failed_attempts': 3,
            'lockout_duration': 900  # 15 minutes
        }
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def create_user(self, username: str, password: str, email: str = "", 
                   role: str = "user") -> str:
        """Create a new user"""
        if username in [u['username'] for u in self._data['users'].values()]:
            raise ValueError("Username already exists")
        
        if role not in self._data['roles']:
            role = self._data['default_role']
        
        user_id = str(uuid4())
        user = User(user_id, username, email, role)
        
        # Hash password
        password_hash = self._hash_password(password)
        
        user_data = user.to_dict()
        user_data['password_hash'] = password_hash
        
        self._data['users'][user_id] = user_data
        self.set_data(self._data)
        
        return user_id
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token"""
        # Find user
        user_data = None
        for user in self._data['users'].values():
            if user['username'] == username:
                user_data = user
                break
        
        if not user_data:
            return None
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return None
        
        # Check failed attempts
        failed_attempts = user_data.get('failed_attempts', 0)
        if failed_attempts >= self._data['max_failed_attempts']:
            lockout_time = user_data.get('locked_until')
            if lockout_time and datetime.fromisoformat(lockout_time) > datetime.now():
                return None
            else:
                # Reset failed attempts after lockout period
                user_data['failed_attempts'] = 0
        
        # Verify password
        if not self._verify_password(password, user_data['password_hash']):
            # Increment failed attempts
            user_data['failed_attempts'] = failed_attempts + 1
            
            # Lock account if max attempts reached
            if user_data['failed_attempts'] >= self._data['max_failed_attempts']:
                lockout_time = datetime.now() + timedelta(seconds=self._data['lockout_duration'])
                user_data['locked_until'] = lockout_time.isoformat()
            
            self.set_data(self._data)
            return None
        
        # Reset failed attempts on successful login
        user_data['failed_attempts'] = 0
        user_data['locked_until'] = None
        user_data['last_login'] = datetime.now().isoformat()
        user_data['login_count'] = user_data.get('login_count', 0) + 1
        
        # Create session
        session_token = str(uuid4())
        session_data = {
            'user_id': user_data['id'],
            'username': username,
            'role': user_data['role'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=self._data['session_timeout'])).isoformat()
        }
        
        self._data['sessions'][session_token] = session_data
        self.set_data(self._data)
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        if session_token not in self._data['sessions']:
            return None
        
        session = self._data['sessions'][session_token]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            # Session expired
            del self._data['sessions'][session_token]
            self.set_data(self._data)
            return None
        
        # Update session expiry
        new_expires = datetime.now() + timedelta(seconds=self._data['session_timeout'])
        session['expires_at'] = new_expires.isoformat()
        self.set_data(self._data)
        
        return session
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session"""
        if session_token in self._data['sessions']:
            del self._data['sessions'][session_token]
            self.set_data(self._data)
            return True
        return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self._data['users'].get(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user_data in self._data['users'].values():
            if user_data['username'] == username:
                return User.from_dict(user_data)
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return [User.from_dict(user_data) for user_data in self._data['users'].values()]
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user data"""
        if user_id not in self._data['users']:
            return False
        
        user_data = self._data['users'][user_id]
        
        # Don't allow changing password through this method
        if 'password' in kwargs:
            del kwargs['password']
        
        # Update allowed fields
        allowed_fields = ['email', 'role', 'is_active', 'preferences']
        for field, value in kwargs.items():
            if field in allowed_fields:
                user_data[field] = value
                
                # Update permissions if role changed
                if field == 'role':
                    user = User.from_dict(user_data)
                    user_data['permissions'] = user._get_default_permissions(value)
        
        self.set_data(self._data)
        return True
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if user_id not in self._data['users']:
            return False
        
        user_data = self._data['users'][user_id]
        
        # Verify old password
        if not self._verify_password(old_password, user_data['password_hash']):
            return False
        
        # Set new password
        user_data['password_hash'] = self._hash_password(new_password)
        self.set_data(self._data)
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id not in self._data['users']:
            return False
        
        # Remove user
        del self._data['users'][user_id]
        
        # Remove any sessions for this user
        sessions_to_remove = []
        for token, session in self._data['sessions'].items():
            if session['user_id'] == user_id:
                sessions_to_remove.append(token)
        
        for token in sessions_to_remove:
            del self._data['sessions'][token]
        
        self.set_data(self._data)
        return True
    
    def has_permission(self, session_token: str, permission: str) -> bool:
        """Check if user has specific permission"""
        session = self.validate_session(session_token)
        if not session:
            return False
        
        user = self.get_user(session['user_id'])
        if not user:
            return False
        
        return permission in user.permissions
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        active_sessions = []
        current_time = datetime.now()
        
        for token, session in self._data['sessions'].items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if current_time < expires_at:
                session_copy = session.copy()
                session_copy['token'] = token
                active_sessions.append(session_copy)
        
        return active_sessions
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_tokens = []
        
        for token, session in self._data['sessions'].items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if current_time >= expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self._data['sessions'][token]
        
        if expired_tokens:
            self.set_data(self._data)
        
        return len(expired_tokens)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        users = self.get_all_users()
        active_sessions = self.get_active_sessions()
        
        stats = {
            'total_users': len(users),
            'active_users': len([u for u in users if u.is_active]),
            'by_role': {},
            'total_logins': sum(u.login_count for u in users),
            'recent_logins': len([u for u in users 
                               if u.last_login and 
                               (datetime.now() - datetime.fromisoformat(u.last_login)).days <= 7]),
            'active_sessions': len(active_sessions),
            'failed_attempts': sum(u.get('failed_attempts', 0) for u in self._data['users'].values())
        }
        
        # Count by role
        for user in users:
            role = user.role
            if role not in stats['by_role']:
                stats['by_role'][role] = 0
            stats['by_role'][role] += 1
        
        return stats
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        import secrets
        
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == hash_value
        except ValueError:
            return False
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save users to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load users from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                if isinstance(loaded_data, dict):
                    self._data = loaded_data
                    # Ensure required keys
                    if 'users' not in self._data:
                        self._data['users'] = {}
                    if 'sessions' not in self._data:
                        self._data['sessions'] = {}
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate user data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        required_keys = ['users', 'sessions', 'roles']
        for key in required_keys:
            if key not in self._data:
                self._errors.append(f"Missing required key: {key}")
                return False
            if not isinstance(self._data[key], dict):
                self._errors.append(f"Key {key} must be a dictionary")
                return False
        
        # Validate each user
        for user_id, user in self._data['users'].items():
            if not isinstance(user, dict):
                self._errors.append(f"User {user_id} must be a dictionary")
                continue
            
            required_fields = ['id', 'username', 'password_hash', 'role']
            for field in required_fields:
                if field not in user:
                    self._errors.append(f"User {user_id} missing required field: {field}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
