"""
Main Core Application for X-Shield Framework
Handles admin checks, module coordination, and SQLite database
"""

import sys
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import QMessageBox

# Windows admin check
import ctypes
from ctypes import wintypes


class AdminChecker:
    """Check for Windows Administrator privileges"""
    
    @staticmethod
    def is_admin() -> bool:
        """Check if application is running as Administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def request_admin():
        """Request admin privileges and restart"""
        if sys.platform == 'win32':
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, 
                f'"{os.path.abspath(sys.argv[0])}"', 
                None, 1
            )
            sys.exit(0)


class DatabaseManager(QObject):
    """SQLite database manager for X-Shield"""
    
    database_connected = Signal()
    database_error = Signal(str)
    
    def __init__(self, db_path: str = "data/xshield.db"):
        super().__init__()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.connect_database()
    
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            self.create_tables()
            self.database_connected.emit()
        except Exception as e:
            self.database_error.emit(f"Database connection failed: {str(e)}")
    
    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.connection.cursor()
        
        # Targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                target_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scanned TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Scan history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                module_name TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                parameters TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration REAL,
                items_scanned INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                results TEXT,
                FOREIGN KEY (target_id) REFERENCES targets (id)
            )
        ''')
        
        # Vulnerabilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                target_id INTEGER,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                target_service TEXT,
                cvss_score REAL,
                cve_id TEXT,
                recommendation TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scan_history (id),
                FOREIGN KEY (target_id) REFERENCES targets (id)
            )
        ''')
        
        # Module configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT NOT NULL,
                config_name TEXT NOT NULL,
                parameters TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(module_name, config_name)
            )
        ''')
        
        self.connection.commit()
    
    def add_target(self, target: str, target_type: str, description: str = None):
        """Add new target to database"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO targets (target, target_type, description)
            VALUES (?, ?, ?)
        ''', (target, target_type, description))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_targets(self) -> List[Dict]:
        """Get all targets from database"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM targets ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def save_scan_result(self, target_id: int, module_name: str, scan_type: str, 
                      parameters: Dict, results: Dict):
        """Save scan results to database"""
        cursor = self.connection.cursor()
        
        # Save scan history
        cursor.execute('''
            INSERT INTO scan_history 
            (target_id, module_name, scan_type, parameters, start_time, end_time, 
             duration, items_scanned, status, results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            target_id, module_name, scan_type,
            json.dumps(parameters), results.get('start_time'),
            results.get('end_time'), results.get('execution_time', 0),
            results.get('items_scanned', 0), results.get('status', 'completed'),
            json.dumps(results)
        ))
        
        scan_id = cursor.lastrowid
        
        # Save vulnerabilities
        for vuln in results.get('vulnerabilities', []):
            cursor.execute('''
                INSERT INTO vulnerabilities 
                (scan_id, target_id, title, severity, description, 
                 target_service, cvss_score, cve_id, recommendation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id, target_id, vuln.get('title'),
                vuln.get('severity'), vuln.get('description'),
                vuln.get('target'), vuln.get('cvss_score'),
                vuln.get('cve_id'), vuln.get('recommendation')
            ))
        
        self.connection.commit()
        return scan_id
    
    def get_scan_history(self, limit: int = 50) -> List[Dict]:
        """Get scan history"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT sh.*, t.target 
            FROM scan_history sh
            JOIN targets t ON sh.target_id = t.id
            ORDER BY sh.start_time DESC
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            scan_data = dict(row)
            if scan_data['results']:
                scan_data['results'] = json.loads(scan_data['results'])
            history.append(scan_data)
        
        return history
    
    def get_vulnerabilities(self, target_id: int = None) -> List[Dict]:
        """Get vulnerabilities"""
        cursor = self.connection.cursor()
        
        if target_id:
            cursor.execute('''
                SELECT v.*, t.target 
                FROM vulnerabilities v
                JOIN targets t ON v.target_id = t.id
                WHERE v.target_id = ?
                ORDER BY v.discovered_at DESC
            ''', (target_id,))
        else:
            cursor.execute('''
                SELECT v.*, t.target 
                FROM vulnerabilities v
                JOIN targets t ON v.target_id = t.id
                ORDER BY v.discovered_at DESC
                LIMIT 100
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def save_module_config(self, module_name: str, config_name: str, parameters: Dict):
        """Save module configuration"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO module_configs 
            (module_name, config_name, parameters)
            VALUES (?, ?, ?)
        ''', (module_name, config_name, json.dumps(parameters)))
        self.connection.commit()
    
    def get_module_configs(self, module_name: str = None) -> List[Dict]:
        """Get module configurations"""
        cursor = self.connection.cursor()
        
        if module_name:
            cursor.execute('''
                SELECT * FROM module_configs 
                WHERE module_name = ?
                ORDER BY created_at DESC
            ''', (module_name,))
        else:
            cursor.execute('''
                SELECT * FROM module_configs 
                ORDER BY created_at DESC
            ''')
        
        configs = []
        for row in cursor.fetchall():
            config_data = dict(row)
            config_data['parameters'] = json.loads(config_data['parameters'])
            configs.append(config_data)
        
        return configs
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        cursor = self.connection.cursor()
        
        # Total targets
        cursor.execute('SELECT COUNT(*) as count FROM targets')
        total_targets = cursor.fetchone()['count']
        
        # Total scans
        cursor.execute('SELECT COUNT(*) as count FROM scan_history')
        total_scans = cursor.fetchone()['count']
        
        # Total vulnerabilities by severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count 
            FROM vulnerabilities 
            GROUP BY severity
        ''')
        vuln_by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM scan_history 
            WHERE start_time > datetime('now', '-7 days')
        ''')
        recent_scans = cursor.fetchone()['count']
        
        return {
            'total_targets': total_targets,
            'total_scans': total_scans,
            'vulnerabilities_by_severity': vuln_by_severity,
            'recent_scans': recent_scans,
            'last_updated': datetime.now().isoformat()
        }


class ModuleChainingEngine(QObject):
    """Intelligent module chaining engine"""
    
    chain_triggered = Signal(str, dict)  # module_name, results
    
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.db_manager = database_manager
        self.chains = {
            'network_to_web': {
                'trigger_modules': ['Network Scanner'],
                'target_modules': ['Web Scanner'],
                'condition': lambda results: self._has_web_ports(results)
            },
            'vulnerability_to_exploitation': {
                'trigger_modules': ['Network Scanner', 'Web Scanner'],
                'target_modules': ['Exploitation Module'],
                'condition': lambda results: self._has_critical_vulns(results)
            }
        }
    
    def _has_web_ports(self, results: Dict) -> bool:
        """Check if results show open web ports"""
        findings = results.get('findings', [])
        for finding in findings:
            if finding.get('type') == 'open_port':
                port = finding.get('details', {}).get('port')
                if port in [80, 443, 8080, 8443]:
                    return True
        return False
    
    def _has_critical_vulns(self, results: Dict) -> bool:
        """Check if results contain critical vulnerabilities"""
        vulnerabilities = results.get('vulnerabilities', [])
        return any(v.get('severity') == 'critical' for v in vulnerabilities)
    
    def evaluate_chain(self, module_name: str, results: Dict):
        """Evaluate if module chaining should be triggered"""
        for chain_name, chain_config in self.chains.items():
            if module_name in chain_config['trigger_modules']:
                if chain_config['condition'](results):
                    for target_module in chain_config['target_modules']:
                        self.chain_triggered.emit(target_module, results)
    
    def get_chain_suggestions(self, module_name: str, results: Dict) -> List[str]:
        """Get suggestions for next modules to run"""
        suggestions = []
        
        for chain_name, chain_config in self.chains.items():
            if module_name in chain_config['trigger_modules']:
                if chain_config['condition'](results):
                    suggestions.extend(chain_config['target_modules'])
        
        return list(set(suggestions))


class StealthConfiguration(QObject):
    """Stealth and evasion configuration"""
    
    def __init__(self):
        super().__init__()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.current_agent_index = 0
        self.delays = {
            'minimal': 0.1,
            'normal': 0.5,
            'stealth': 2.0,
            'paranoid': 5.0
        }
        self.current_delay = 'normal'
        self.proxy_config = {
            'enabled': False,
            'host': None,
            'port': None,
            'type': 'http'
        }
    
    def get_random_user_agent(self) -> str:
        """Get random user agent for stealth"""
        import random
        return random.choice(self.user_agents)
    
    def get_delay(self) -> float:
        """Get current delay setting"""
        return self.delays.get(self.current_delay, 0.5)
    
    def rotate_user_agent(self) -> str:
        """Rotate to next user agent"""
        self.current_agent_index = (self.current_agent_index + 1) % len(self.user_agents)
        return self.user_agents[self.current_agent_index]
    
    def set_stealth_level(self, level: str):
        """Set stealth level"""
        if level in self.delays:
            self.current_delay = level
    
    def get_proxy_config(self) -> Dict:
        """Get proxy configuration"""
        return self.proxy_config
    
    def set_proxy(self, host: str, port: int, proxy_type: str = 'http'):
        """Set proxy configuration"""
        self.proxy_config = {
            'enabled': True,
            'host': host,
            'port': port,
            'type': proxy_type
        }


class MainCore(QObject):
    """Main application core managing all components"""
    
    # Core signals
    admin_required = Signal()
    admin_granted = Signal()
    module_loaded = Signal(str)
    scan_started = Signal(str, str)  # module_name, target
    scan_completed = Signal(str, dict)  # module_name, results
    chain_suggested = Signal(str, list)  # module_name, suggestions
    error_occurred = Signal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self.is_admin = False
        self.database_manager = DatabaseManager()
        self.chaining_engine = ModuleChainingEngine(self.database_manager)
        self.stealth_config = StealthConfiguration()
        
        # Connect database signals
        self.database_manager.database_connected.connect(self.on_database_connected)
        self.database_manager.database_error.connect(self.on_database_error)
        
        # Connect chaining signals
        self.chaining_engine.chain_triggered.connect(self.on_chain_triggered)
        
        # Check admin privileges
        self.check_admin_privileges()
        
        # Setup periodic tasks
        self.setup_periodic_tasks()
    
    def check_admin_privileges(self):
        """Check and request admin privileges if needed"""
        if not AdminChecker.is_admin():
            self.admin_required.emit()
            return False
        else:
            self.is_admin = True
            self.admin_granted.emit()
            return True
    
    def request_admin_privileges(self):
        """Request admin privileges and restart"""
        AdminChecker.request_admin()
    
    @Slot()
    def on_database_connected(self):
        """Handle database connection"""
        print("Database connected successfully")
    
    @Slot()
    def on_database_error(self, error_message: str):
        """Handle database error"""
        self.error_occurred.emit(f"Database error: {error_message}")
    
    @Slot(str, dict)
    def on_chain_triggered(self, module_name: str, results: dict):
        """Handle module chaining trigger"""
        self.chain_suggested.emit(module_name, [module_name])
    
    def setup_periodic_tasks(self):
        """Setup periodic maintenance tasks"""
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.perform_maintenance)
        self.cleanup_timer.start(3600000)  # Every hour
    
    def perform_maintenance(self):
        """Perform periodic maintenance"""
        try:
            # Clean old scan history (keep last 1000)
            cursor = self.database_manager.connection.cursor()
            cursor.execute('''
                DELETE FROM scan_history 
                WHERE id NOT IN (
                    SELECT id FROM scan_history 
                    ORDER BY start_time DESC 
                    LIMIT 1000
                )
            ''')
            self.database_manager.connection.commit()
            
        except Exception as e:
            self.error_occurred.emit(f"Maintenance failed: {str(e)}")
    
    def get_module_parameters(self, module_name: str) -> Dict:
        """Get parameters for module including stealth settings"""
        base_params = {}
        
        # Add stealth parameters
        stealth_params = {
            'user_agent': self.stealth_config.get_random_user_agent(),
            'delay': self.stealth_config.get_delay(),
            'proxy': self.stealth_config.get_proxy_config()
        }
        
        base_params.update(stealth_params)
        return base_params
    
    def execute_module_chain(self, module_name: str, target: str, parameters: Dict) -> Dict:
        """Execute module with chaining logic"""
        # Get enhanced parameters
        enhanced_params = self.get_module_parameters(module_name)
        enhanced_params.update(parameters)
        
        # Execute module (this would be handled by module manager)
        self.scan_started.emit(module_name, target)
        
        # Return enhanced parameters for module execution
        return enhanced_params
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        stats = self.database_manager.get_statistics()
        
        # Add real-time data
        dashboard_data = {
            'statistics': stats,
            'recent_scans': self.database_manager.get_scan_history(limit=10),
            'targets': self.database_manager.get_targets(),
            'vulnerabilities': self.database_manager.get_vulnerabilities(),
            'admin_status': self.is_admin,
            'stealth_level': self.stealth_config.current_delay
        }
        
        return dashboard_data
    
    def generate_report_data(self, target_ids: List[int] = None) -> Dict:
        """Generate data for report generation"""
        if target_ids:
            vulnerabilities = []
            for target_id in target_ids:
                vulnerabilities.extend(self.database_manager.get_vulnerabilities(target_id))
        else:
            vulnerabilities = self.database_manager.get_vulnerabilities()
        
        scan_history = self.database_manager.get_scan_history(limit=100)
        
        return {
            'vulnerabilities': vulnerabilities,
            'scan_history': scan_history,
            'statistics': self.database_manager.get_statistics(),
            'generation_time': datetime.now().isoformat()
        }
