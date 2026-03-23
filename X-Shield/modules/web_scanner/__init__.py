"""
Web Scanner Module for X-Shield Framework
Performs XSS, SQLi, and CSRF vulnerability scanning with User-Agent switching
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_module import NetworkModule
import requests
import re
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtCore import Signal, Slot
from concurrent.futures import ThreadPoolExecutor, as_completed


class Module(NetworkModule):
    """Web Scanner Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "Web Scanner"
    DESCRIPTION = "Advanced web vulnerability scanner with XSS, SQLi, and CSRF detection"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Web"
    
    # Signals
    scan_progress = Signal(int, int)  # current, total
    scan_status = Signal(str)  # status message
    vulnerability_found = Signal(dict)  # vulnerability info
    url_scanned = Signal(dict)  # URL scan info
    form_discovered = Signal(dict)  # form info
    scan_complete = Signal(dict)  # final results
    
    PARAMETERS = {
        'target_url': {
            'type': 'string',
            'label': 'Target URL',
            'default': 'https://example.com',
            'description': 'Target URL to scan'
        },
        'scan_types': {
            'type': 'multichoice',
            'label': 'Scan Types',
            'default': ['xss', 'sqli', 'csrf', 'directory'],
            'choices': ['xss', 'sqli', 'csrf', 'directory', 'headers', 'technologies'],
            'description': 'Types of vulnerability scans to perform'
        },
        'depth': {
            'type': 'integer',
            'label': 'Scan Depth',
            'default': 3,
            'min': 1,
            'max': 10,
            'description': 'Maximum depth for directory and link scanning'
        },
        'threads': {
            'type': 'integer',
            'label': 'Threads',
            'default': 10,
            'min': 1,
            'max': 50,
            'description': 'Number of concurrent threads'
        },
        'delay': {
            'type': 'float',
            'label': 'Request Delay (seconds)',
            'default': 0.5,
            'min': 0.1,
            'max': 10.0,
            'description': 'Delay between requests for stealth'
        },
        'user_agent': {
            'type': 'choice',
            'label': 'User Agent',
            'default': 'random',
            'choices': ['random', 'chrome', 'firefox', 'safari', 'edge', 'custom'],
            'description': 'User-Agent string to use'
        },
        'timeout': {
            'type': 'integer',
            'label': 'Request Timeout (seconds)',
            'default': 10,
            'min': 5,
            'max': 30,
            'description': 'Timeout for HTTP requests'
        },
        'custom_headers': {
            'type': 'text',
            'label': 'Custom Headers',
            'default': '',
            'description': 'Additional HTTP headers (JSON format)'
        },
        'proxy': {
            'type': 'string',
            'label': 'Proxy',
            'default': '',
            'description': 'Proxy server (http://host:port)'
        }
    }
    
    def __init__(self, logger):
        super().__init__(logger)
        self._stop_requested = False
        self._is_running = False
        
        # User agents for stealth
        self.user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        }
        
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
        """Execute web vulnerability scan"""
        try:
            self._start_execution(target, parameters)
            
            scan_types = parameters.get('scan_types', ['xss', 'sqli', 'csrf'])
            depth = parameters.get('depth', 3)
            threads = parameters.get('threads', 10)
            delay = parameters.get('delay', 0.5)
            timeout = parameters.get('timeout', 10)
            
            # Setup session with user agent and proxy
            session = self._setup_session(parameters)
            
            # Normalize target URL
            target_url = self._normalize_url(target)
            
            # Discover forms and links first
            self.scan_status.emit("Discovering web application structure...")
            discovered_urls = self._discover_urls(target_url, session, depth, threads, delay, timeout)
            
            vulnerabilities = []
            
            # Perform different scan types
            for scan_type in scan_types:
                if self._stop_requested:
                    break
                
                if scan_type == 'xss':
                    vulns = self._scan_xss(discovered_urls, session, threads, delay, timeout)
                    vulnerabilities.extend(vulns)
                    
                elif scan_type == 'sqli':
                    vulns = self._scan_sql_injection(discovered_urls, session, threads, delay, timeout)
                    vulnerabilities.extend(vulns)
                    
                elif scan_type == 'csrf':
                    vulns = self._scan_csrf(discovered_urls, session, threads, delay, timeout)
                    vulnerabilities.extend(vulns)
                    
                elif scan_type == 'directory':
                    vulns = self._scan_directories(target_url, session, depth, threads, delay, timeout)
                    vulnerabilities.extend(vulns)
                    
                elif scan_type == 'headers':
                    vulns = self._scan_headers(target_url, session)
                    vulnerabilities.extend(vulns)
                    
                elif scan_type == 'technologies':
                    techs = self._identify_technologies(target_url, session)
                    # Add as findings rather than vulnerabilities
                    for tech in techs:
                        self.add_finding('technology_detected', tech)
                
                self.scan_status.emit(f"Completed {scan_type} scan")
            
            self._finish_execution()
            self.scan_complete.emit(self.results)
            return self.results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _setup_session(self, parameters: dict):
        """Setup requests session with user agent and proxy"""
        session = requests.Session()
        
        # Set user agent
        user_agent_choice = parameters.get('user_agent', 'random')
        if user_agent_choice == 'random':
            session.headers['User-Agent'] = self._get_random_user_agent()
        elif user_agent_choice in self.user_agents:
            session.headers['User-Agent'] = self.user_agents[user_agent_choice]
        
        # Set custom headers
        custom_headers = parameters.get('custom_headers', '')
        if custom_headers:
            try:
                import json
                headers = json.loads(custom_headers)
                session.headers.update(headers)
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid custom headers JSON: {custom_headers}")
        
        # Set proxy
        proxy = parameters.get('proxy', '')
        if proxy:
            session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
        return session
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        additional_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.1 Safari/605.1.15'
        ]
        return random.choice(additional_agents)
    
    def _normalize_url(self, url: str) -> str:
        """Normalize and validate URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        return url
    
    def _discover_urls(self, base_url: str, session, depth: int, threads: int, delay: float, timeout: int) -> list:
        """Discover URLs and forms through crawling"""
        discovered_urls = set([base_url])
        visited_urls = set()
        forms_found = []
        
        def scan_page(url):
            if self._stop_requested or url in visited_urls:
                return []
            
            try:
                response = session.get(url, timeout=timeout)
                visited_urls.add(url)
                
                if response.status_code == 200:
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find forms
                    forms = soup.find_all('form')
                    for form in forms:
                        form_info = {
                            'url': url,
                            'method': form.get('method', 'GET').upper(),
                            'action': form.get('action', ''),
                            'inputs': []
                        }
                        
                        # Extract form inputs
                        inputs = form.find_all(['input', 'textarea', 'select'])
                        for inp in inputs:
                            input_info = {
                                'name': inp.get('name', ''),
                                'type': inp.get('type', 'text'),
                                'id': inp.get('id', '')
                            }
                            form_info['inputs'].append(input_info)
                        
                        forms_found.append(form_info)
                        self.form_discovered.emit(form_info)
                    
                    # Find links
                    links = soup.find_all('a', href=True)
                    page_urls = []
                    
                    for link in links:
                        href = link['href']
                        if href.startswith(('http://', 'https://')):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = urljoin(base_url, href)
                        else:
                            continue
                        
                        # Only add URLs from the same domain
                        if urlparse(full_url).netloc == urlparse(base_url).netloc:
                            page_urls.append(full_url)
                    
                    self.url_scanned.emit({'url': url, 'status_code': response.status_code})
                    return page_urls
                    
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Error scanning {url}: {str(e)}")
                return []
        
        # Multi-threaded crawling
        current_level_urls = [base_url]
        
        for level in range(depth):
            if self._stop_requested:
                break
            
            next_level_urls = []
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = {executor.submit(scan_page, url): url for url in current_level_urls}
                
                for future in as_completed(futures):
                    urls = future.result()
                    next_level_urls.extend(urls)
                    discovered_urls.update(urls)
            
            current_level_urls = list(set(next_level_urls) - visited_urls)
        
        # Store forms as findings
        for form in forms_found:
            self.add_finding('form_discovered', form)
        
        return list(discovered_urls)
    
    def _scan_xss(self, urls: list, session, threads: int, delay: float, timeout: int) -> list:
        """Scan for Cross-Site Scripting vulnerabilities"""
        vulnerabilities = []
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "'\"><script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        def test_url_xss(url):
            if self._stop_requested:
                return []
            
            try:
                # Test URL parameters for XSS
                parsed = urlparse(url)
                if not parsed.query:
                    return []
                
                # Extract parameters
                params = parsed.query.split('&')
                url_vulns = []
                
                for param in params:
                    param_name = param.split('=')[0] if '=' in param else param
                    
                    for payload in xss_payloads:
                        test_url = url.replace(param, f"{param_name}={payload}")
                        
                        try:
                            response = session.get(test_url, timeout=timeout)
                            
                            if payload in response.text:
                                vulnerability = {
                                    'title': 'Cross-Site Scripting (XSS)',
                                    'severity': 'high',
                                    'description': f'XSS vulnerability found in parameter: {param_name}',
                                    'target': test_url,
                                    'payload': payload,
                                    'recommendation': 'Implement proper input validation and output encoding'
                                }
                                url_vulns.append(vulnerability)
                                self.vulnerability_found.emit(vulnerability)
                                
                        except Exception as e:
                            continue
                        
                        time.sleep(delay)
                
                return url_vulns
                
            except Exception as e:
                self.logger.error(f"XSS scan error for {url}: {str(e)}")
                return []
        
        # Test URLs concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(test_url_xss, url): url for url in urls}
            
            for future in as_completed(futures):
                vulns = future.result()
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    def _scan_sql_injection(self, urls: list, session, threads: int, delay: float, timeout: int) -> list:
        """Scan for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        # SQLi payloads
        sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' OR 1=1#",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--"
        ]
        
        # SQLi error patterns
        sql_errors = [
            'SQL syntax',
            'mysql_fetch',
            'ORA-01756',
            'Microsoft OLE DB Provider',
            'Warning: mysql_',
            'PostgreSQL query failed',
            'SQLServer JDBC Driver'
        ]
        
        def test_url_sqli(url):
            if self._stop_requested:
                return []
            
            try:
                parsed = urlparse(url)
                if not parsed.query:
                    return []
                
                # Extract parameters
                params = parsed.query.split('&')
                url_vulns = []
                
                for param in params:
                    if '=' not in param:
                        continue
                    
                    param_name = param.split('=')[0]
                    
                    for payload in sqli_payloads:
                        test_url = url.replace(param, f"{param_name}={payload}")
                        
                        try:
                            response = session.get(test_url, timeout=timeout)
                            
                            # Check for SQL errors in response
                            for error_pattern in sql_errors:
                                if error_pattern.lower() in response.text.lower():
                                    vulnerability = {
                                        'title': 'SQL Injection',
                                        'severity': 'critical',
                                        'description': f'SQL injection vulnerability in parameter: {param_name}',
                                        'target': test_url,
                                        'payload': payload,
                                        'error_pattern': error_pattern,
                                        'recommendation': 'Use parameterized queries and input validation'
                                    }
                                    url_vulns.append(vulnerability)
                                    self.vulnerability_found.emit(vulnerability)
                                    break
                                    
                        except Exception as e:
                            continue
                        
                        time.sleep(delay)
                
                return url_vulns
                
            except Exception as e:
                self.logger.error(f"SQLi scan error for {url}: {str(e)}")
                return []
        
        # Test URLs concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(test_url_sqli, url): url for url in urls}
            
            for future in as_completed(futures):
                vulns = future.result()
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    def _scan_csrf(self, urls: list, session, threads: int, delay: float, timeout: int) -> list:
        """Scan for CSRF vulnerabilities"""
        vulnerabilities = []
        
        def test_form_csrf(url, form_info):
            if self._stop_requested:
                return None
            
            try:
                # Check for CSRF tokens
                form_action = form_info.get('action', url)
                form_method = form_info.get('method', 'GET')
                form_inputs = form_info.get('inputs', [])
                
                # Look for anti-CSRF tokens
                has_csrf_token = False
                token_fields = ['csrf_token', 'authenticity_token', '_token', 'nonce', 'state']
                
                for inp in form_inputs:
                    input_name = inp.get('name', '').lower()
                    if any(token in input_name for token in token_fields):
                        has_csrf_token = True
                        break
                
                if not has_csrf_token and form_method in ['POST', 'PUT', 'DELETE']:
                    # Check if form performs state-changing action
                    state_changing_indicators = ['password', 'delete', 'update', 'create', 'submit']
                    
                    for inp in form_inputs:
                        input_name = inp.get('name', '').lower()
                        input_type = inp.get('type', '').lower()
                        
                        if (any(indicator in input_name for indicator in state_changing_indicators) or
                            input_type in ['password', 'hidden']):
                            # This might be a state-changing form without CSRF protection
                            vulnerability = {
                                'title': 'Cross-Site Request Forgery (CSRF)',
                                'severity': 'medium',
                                'description': f'Form at {url} may be vulnerable to CSRF',
                                'target': form_action,
                                'form_method': form_method,
                                'recommendation': 'Implement CSRF tokens and SameSite cookie attributes'
                            }
                            vulnerabilities.append(vulnerability)
                            self.vulnerability_found.emit(vulnerability)
                            break
                
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"CSRF scan error for {url}: {str(e)}")
            
            return None
        
        # Get forms from findings
        forms = [f.get('details', {}) for f in self.results['findings'] 
                 if f.get('type') == 'form_discovered']
        
        # Test forms concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(test_form_csrf, form.get('url', ''), form): form for form in forms}
            
            for future in as_completed(futures):
                future.result()
        
        return vulnerabilities
    
    def _scan_directories(self, base_url: str, session, depth: int, threads: int, delay: float, timeout: int) -> list:
        """Scan for exposed directories and files"""
        vulnerabilities = []
        
        # Common directory and file names
        wordlists = {
            'directories': [
                'admin', 'administrator', 'backup', 'config', 'database', 'db',
                'files', 'images', 'include', 'lib', 'logs', 'mail', 'tmp',
                'test', 'uploads', 'web', 'www', 'api', 'docs', 'private'
            ],
            'files': [
                'config.php', 'database.sql', 'backup.zip', 'dump.sql',
                'web.config', '.env', 'settings.py', 'connection.php',
                'admin.php', 'login.php', 'index.php.bak', 'robots.txt',
                '.htaccess', 'sitemap.xml', 'crossdomain.xml'
            ]
        }
        
        def test_directory(url):
            if self._stop_requested:
                return []
            
            dir_vulns = []
            
            for directory in wordlists['directories']:
                test_url = f"{url}/{directory}/"
                
                try:
                    response = session.get(test_url, timeout=timeout)
                    
                    if response.status_code in [200, 201, 202, 203]:
                        vulnerability = {
                            'title': 'Exposed Directory',
                            'severity': 'medium',
                            'description': f'Directory listing accessible: {directory}',
                            'target': test_url,
                            'status_code': response.status_code,
                            'recommendation': 'Restrict directory access with proper authentication'
                        }
                        dir_vulns.append(vulnerability)
                        self.vulnerability_found.emit(vulnerability)
                        
                except Exception as e:
                    continue
                
                time.sleep(delay)
            
            for file_name in wordlists['files']:
                test_url = f"{url}/{file_name}"
                
                try:
                    response = session.get(test_url, timeout=timeout)
                    
                    if response.status_code == 200:
                        vulnerability = {
                            'title': 'Exposed Sensitive File',
                            'severity': 'high',
                            'description': f'Sensitive file exposed: {file_name}',
                            'target': test_url,
                            'status_code': response.status_code,
                            'recommendation': 'Remove or restrict access to sensitive files'
                        }
                        dir_vulns.append(vulnerability)
                        self.vulnerability_found.emit(vulnerability)
                        
                except Exception as e:
                    continue
                
                time.sleep(delay)
            
            return dir_vulns
        
        # Test base URL
        return test_directory(base_url)
    
    def _scan_headers(self, url: str, session) -> list:
        """Scan HTTP headers for security issues"""
        vulnerabilities = []
        
        try:
            response = session.get(url, timeout=10)
            
            # Check security headers
            security_headers = {
                'X-Frame-Options': 'Clickjacking protection',
                'X-XSS-Protection': 'XSS protection',
                'Strict-Transport-Security': 'HTTPS enforcement',
                'Content-Security-Policy': 'Content Security Policy',
                'X-Content-Type-Options': 'MIME type sniffing protection'
            }
            
            missing_headers = []
            for header, description in security_headers.items():
                if header not in response.headers:
                    missing_headers.append({
                        'header': header,
                        'description': description
                    })
            
            if missing_headers:
                vulnerability = {
                    'title': 'Missing Security Headers',
                    'severity': 'low',
                    'description': f'Missing security headers: {", ".join([h["header"] for h in missing_headers])}',
                    'target': url,
                    'missing_headers': missing_headers,
                    'recommendation': 'Implement security headers for better protection'
                }
                vulnerabilities.append(vulnerability)
                self.vulnerability_found.emit(vulnerability)
            
            # Check for information disclosure
            server = response.headers.get('Server', '')
            if server:
                if any(info in server.lower() for info in ['apache', 'nginx', 'iis', 'php']):
                    vulnerability = {
                        'title': 'Information Disclosure - Server Version',
                        'severity': 'low',
                        'description': f'Server version exposed: {server}',
                        'target': url,
                        'server': server,
                        'recommendation': 'Hide or obscure server version information'
                    }
                    vulnerabilities.append(vulnerability)
                    self.vulnerability_found.emit(vulnerability)
            
        except Exception as e:
            self.logger.error(f"Header scan error for {url}: {str(e)}")
        
        return vulnerabilities
    
    def _identify_technologies(self, url: str, session) -> list:
        """Identify web technologies"""
        technologies = []
        
        try:
            response = session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for common technologies
            tech_indicators = {
                'WordPress': ['wp-content', 'wp-includes', 'wp-json'],
                'Joomla': ['/administrator/', 'com_content'],
                'Drupal': ['sites/default/files', 'drupal'],
                'Bootstrap': ['bootstrap.min.css', 'bootstrap'],
                'jQuery': ['jquery', 'jQuery'],
                'React': ['react', 'ReactDOM'],
                'Angular': ['ng-app', 'angular'],
                'Vue.js': ['vue', 'Vuex']
            }
            
            # Check HTML content
            content = response.text.lower()
            
            for tech, indicators in tech_indicators.items():
                if any(indicator in content for indicator in indicators):
                    technologies.append({
                        'name': tech,
                        'source': 'content_analysis',
                        'confidence': 'medium'
                    })
            
            # Check headers
            headers = response.headers
            if 'x-powered-by' in headers:
                technologies.append({
                    'name': headers['x-powered-by'],
                    'source': 'http_header',
                    'confidence': 'high'
                })
            
            # Check meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                content = meta.get('content', '').lower()
                
                if 'generator' in name and content:
                    technologies.append({
                        'name': content,
                        'source': 'meta_tag',
                        'confidence': 'high'
                    })
            
        except Exception as e:
            self.logger.error(f"Technology detection error for {url}: {str(e)}")
        
        return technologies
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.scan_status.emit("Scan stopped by user")
