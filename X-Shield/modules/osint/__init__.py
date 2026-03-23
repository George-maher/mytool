"""
OSINT Module for X-Shield Framework
Open Source Intelligence gathering with API integrations and metadata extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_module import NetworkModule
import requests
import json
import re
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import Signal, Slot


class Module(NetworkModule):
    """OSINT Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "OSINT"
    DESCRIPTION = "Open Source Intelligence gathering with API integrations and metadata extraction"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Intelligence"
    
    # Signals
    osint_progress = Signal(int, int)  # current, total
    osint_status = Signal(str)  # status message
    data_found = Signal(dict)  # OSINT data found
    api_queried = Signal(str, dict)  # API name, results
    osint_complete = Signal(dict)  # final results
    
    PARAMETERS = {
        'target': {
            'type': 'string',
            'label': 'Target',
            'default': 'example.com',
            'description': 'Target domain, IP, or email address'
        },
        'modules': {
            'type': 'multichoice',
            'label': 'OSINT Modules',
            'default': ['whois', 'dns', 'shodan', 'subdomain', 'email'],
            'choices': ['whois', 'dns', 'shodan', 'subdomain', 'email', 'social', 'metadata'],
            'description': 'OSINT modules to run'
        },
        'shodan_api_key': {
            'type': 'string',
            'label': 'Shodan API Key',
            'default': '',
            'description': 'Shodan API key for enhanced OSINT'
        },
        'virustotal_api_key': {
            'type': 'string',
            'label': 'VirusTotal API Key',
            'default': '',
            'description': 'VirusTotal API key for malware analysis'
        },
        'threads': {
            'type': 'integer',
            'label': 'Threads',
            'default': 5,
            'min': 1,
            'max': 20,
            'description': 'Number of concurrent threads'
        },
        'delay': {
            'type': 'float',
            'label': 'Request Delay (seconds)',
            'default': 1.0,
            'min': 0.1,
            'max': 10.0,
            'description': 'Delay between API requests'
        },
        'max_subdomains': {
            'type': 'integer',
            'label': 'Max Subdomains',
            'default': 100,
            'min': 10,
            'max': 1000,
            'description': 'Maximum subdomains to discover'
        },
        'email_format': {
            'type': 'string',
            'label': 'Email Format',
            'default': '{first}.{last}@{domain}',
            'description': 'Email format for email enumeration'
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
        """Execute OSINT gathering"""
        try:
            self._start_execution(target, parameters)
            
            modules = parameters.get('modules', ['whois', 'dns', 'shodan', 'subdomain', 'email'])
            threads = parameters.get('threads', 5)
            delay = parameters.get('delay', 1.0)
            
            osint_data = {}
            
            # Run different OSINT modules
            for module in modules:
                if self._stop_requested:
                    break
                
                if module == 'whois':
                    data = self._whois_lookup(target, delay)
                    osint_data['whois'] = data
                    
                elif module == 'dns':
                    data = self._dns_enumeration(target, threads, delay)
                    osint_data['dns'] = data
                    
                elif module == 'shodan':
                    data = self._shodan_search(target, parameters, delay)
                    osint_data['shodan'] = data
                    
                elif module == 'subdomain':
                    data = self._subdomain_enumeration(target, parameters, threads, delay)
                    osint_data['subdomains'] = data
                    
                elif module == 'email':
                    data = self._email_enumeration(target, parameters, threads, delay)
                    osint_data['emails'] = data
                    
                elif module == 'social':
                    data = self._social_media_search(target, threads, delay)
                    osint_data['social'] = data
                    
                elif module == 'metadata':
                    data = self._metadata_extraction(target, delay)
                    osint_data['metadata'] = data
                
                self.osint_status.emit(f"Completed {module} OSINT")
            
            self._finish_execution()
            self.osint_complete.emit(self.results)
            return self.results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _whois_lookup(self, target: str, delay: float) -> dict:
        """Perform WHOIS lookup"""
        self.osint_status.emit(f"Performing WHOIS lookup for {target}")
        
        try:
            # Remove protocol if present
            clean_target = target.replace('http://', '').replace('https://', '').split('/')[0]
            
            response = requests.get(f"https://whois.whoisxml.com/whois.xml/whois.xml?domain={clean_target}&outputFormat=JSON", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                whois_data = {
                    'domain': clean_target,
                    'registrar': data.get('registrant', {}).get('name', 'Unknown'),
                    'creation_date': data.get('registrant', {}).get('createdDate', 'Unknown'),
                    'expiration_date': data.get('registrant', {}).get('expiresDate', 'Unknown'),
                    'name_servers': data.get('nameServers', {}).get('hostNames', []),
                    'status': data.get('registrant', {}).get('status', 'Unknown')
                }
                
                self.add_finding('whois_info', whois_data)
                self.data_found.emit(whois_data)
                
                time.sleep(delay)
                return whois_data
                
            else:
                self.osint_status.emit(f"WHOIS lookup failed for {target}")
                return {}
                
        except Exception as e:
            self.logger.error(f"WHOIS lookup error: {str(e)}")
            return {}
    
    def _dns_enumeration(self, target: str, threads: int, delay: float) -> dict:
        """Perform DNS enumeration"""
        self.osint_status.emit(f"Performing DNS enumeration for {target}")
        
        dns_records = {}
        
        # DNS record types to query
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        def query_dns_record(record_type):
            if self._stop_requested:
                return None
            
            try:
                # Use Google DNS over HTTPS (more reliable)
                url = f"https://dns.google/resolve?name={target}&type={record_type}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'Answer' in data:
                        dns_records[record_type] = data['Answer']
                
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"DNS query error for {record_type}: {str(e)}")
            
            return None
        
        # Query DNS records concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(query_dns_record, record_type): record_type for record_type in record_types}
            
            for future in as_completed(futures):
                future.result()
        
        if dns_records:
            self.add_finding('dns_records', dns_records)
            self.data_found.emit(dns_records)
        
        return dns_records
    
    def _shodan_search(self, target: str, parameters: dict, delay: float) -> dict:
        """Search Shodan for target information"""
        api_key = parameters.get('shodan_api_key', '')
        
        if not api_key:
            self.osint_status.emit("Shodan API key not provided")
            return {}
        
        self.osint_status.emit(f"Searching Shodan for {target}")
        
        try:
            # Clean target
            clean_target = target.replace('http://', '').replace('https://', '').split('/')[0]
            
            # Shodan API endpoints
            shodan_endpoints = {
                'host': f"https://api.shodan.io/host/{clean_target}?key={api_key}",
                'dns': f"https://api.shodan.io/dns/resolve?hostnames={clean_target}&key={api_key}",
                'ports': f"https://api.shodan.io/host/{clean_target}?key={api_key}",
                'vulnerabilities': f"https://api.shodan.io/host/{clean_target}?key={api_key}"
            }
            
            shodan_data = {}
            
            for endpoint_name, endpoint_url in shodan_endpoints.items():
                if self._stop_requested:
                    break
                
                try:
                    response = requests.get(endpoint_url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        shodan_data[endpoint_name] = data
                        
                        # Extract relevant information
                        if endpoint_name == 'host':
                            self.add_finding('shodan_host_info', {
                                'country': data.get('country_name', 'Unknown'),
                                'city': data.get('city', 'Unknown'),
                                'organization': data.get('org', 'Unknown'),
                                'asn': data.get('asn', 'Unknown'),
                                'last_update': data.get('last_update', 'Unknown')
                            })
                        
                        elif endpoint_name == 'ports':
                            ports = data.get('ports', [])
                            if ports:
                                self.add_finding('shodan_ports', {
                                    'total_ports': len(ports),
                                    'open_ports': [p for p in ports if p.get('transport') == 'tcp']
                                })
                    
                    self.api_queried.emit('shodan', {endpoint_name: data})
                    time.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"Shodan API error for {endpoint_name}: {str(e)}")
            
            if shodan_data:
                self.data_found.emit(shodan_data)
            
            return shodan_data
            
        except Exception as e:
            self.logger.error(f"Shodan search error: {str(e)}")
            return {}
    
    def _subdomain_enumeration(self, target: str, parameters: dict, threads: int, delay: float) -> dict:
        """Enumerate subdomains"""
        self.osint_status.emit(f"Enumerating subdomains for {target}")
        
        max_subdomains = parameters.get('max_subdomains', 100)
        
        # Subdomain sources
        sources = [
            f"https://crt.sh/{target}",
            f"https://dns.bufferover.run/dns?q=.{target}",
            f"https://riddler.io/search/{target}",
            f"https://subdomainfinder.c99.nl/scans/{target}"
        ]
        
        subdomains = set()
        
        def query_source(source_url):
            if self._stop_requested:
                return []
            
            try:
                response = requests.get(source_url, timeout=30)
                
                found_subdomains = []
                
                if 'crt.sh' in source_url:
                    # Parse CRT.sh results
                    data = response.json()
                    for cert in data.get('certificates', []):
                        name_value = cert.get('name_value', '')
                        if name_value and target in name_value:
                            # Extract subdomains
                            parts = name_value.split('.')
                            for i in range(len(parts)):
                                subdomain = '.'.join(parts[i:])
                                if subdomain != target and subdomain not in [target]:
                                    found_subdomains.append(subdomain)
                
                elif 'dns.bufferover.run' in source_url:
                    # Parse DNS bufferover
                    data = response.json()
                    for record in data.get('FDNS_A', []):
                        subdomain = record.get('host', '')
                        if subdomain and subdomain != target:
                            found_subdomains.append(subdomain)
                
                elif 'riddler.io' in source_url:
                    # Parse Riddler results
                    data = response.json()
                    for subdomain in data.get('subdomains', []):
                        if subdomain and subdomain != target:
                            found_subdomains.append(subdomain)
                
                elif 'subdomainfinder.c99.nl' in source_url:
                    # Parse SubdomainFinder results
                    data = response.json()
                    found_subdomains.extend(data.get('subdomains', []))
                
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Subdomain enumeration error for {source_url}: {str(e)}")
            
            return found_subdomains
        
        # Query sources concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(query_source, source): source for source in sources}
            
            for future in as_completed(futures):
                found = future.result()
                subdomains.update(found)
        
        # Limit results
        subdomain_list = list(subdomains)[:max_subdomains]
        
        if subdomain_list:
            self.add_finding('subdomains', {
                'total_found': len(subdomain_list),
                'subdomains': subdomain_list
            })
            self.data_found.emit({'subdomains': subdomain_list})
        
        return {'subdomains': subdomain_list}
    
    def _email_enumeration(self, target: str, parameters: dict, threads: int, delay: float) -> dict:
        """Enumerate email addresses"""
        self.osint_status.emit(f"Enumerating emails for {target}")
        
        email_format = parameters.get('email_format', '{first}.{last}@{domain}')
        max_subdomains = parameters.get('max_subdomains', 100)
        
        # Common first and last names
        first_names = [
            'admin', 'info', 'support', 'service', 'contact', 'webmaster', 'postmaster',
            'john', 'jane', 'david', 'michael', 'sarah', 'robert', 'lisa',
            'mark', 'jennifer', 'william', 'linda', 'james', 'mary', 'richard'
        ]
        
        last_names = [
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson'
        ]
        
        # Get subdomains first
        subdomain_data = self._subdomain_enumeration(target, parameters, threads, delay)
        subdomains = subdomain_data.get('subdomains', [target])
        
        emails = set()
        
        def generate_emails(domain):
            if self._stop_requested:
                return []
            
            domain_emails = []
            
            for first in first_names:
                for last in last_names:
                    email = email_format.format(first=first, last=last, domain=domain)
                    domain_emails.append(email)
            
            time.sleep(delay)
            return domain_emails
        
        # Generate emails for each subdomain
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(generate_emails, subdomain): subdomain for subdomain in subdomains[:max_subdomains]}
            
            for future in as_completed(futures):
                found_emails = future.result()
                emails.update(found_emails)
        
        email_list = list(emails)
        
        if email_list:
            self.add_finding('emails', {
                'total_found': len(email_list),
                'emails': email_list
            })
            self.data_found.emit({'emails': email_list})
        
        return {'emails': email_list}
    
    def _social_media_search(self, target: str, threads: int, delay: float) -> dict:
        """Search social media for target"""
        self.osint_status.emit(f"Searching social media for {target}")
        
        # Social media platforms
        platforms = {
            'linkedin': f"https://www.linkedin.com/search/results/all/?keywords={target}",
            'twitter': f"https://twitter.com/search?q={target}&f=users",
            'facebook': f"https://www.facebook.com/search/top/?q={target}",
            'instagram': f"https://www.instagram.com/{target}",
            'github': f"https://github.com/search?q={target}&type=users"
        }
        
        social_data = {}
        
        def search_platform(platform_name, search_url):
            if self._stop_requested:
                return None
            
            try:
                response = requests.get(search_url, timeout=30)
                
                # Simple check - in real implementation, you'd parse the HTML
                if response.status_code == 200:
                    social_data[platform_name] = {
                        'found': True,
                        'url': search_url,
                        'response_length': len(response.text)
                    }
                else:
                    social_data[platform_name] = {
                        'found': False,
                        'url': search_url
                    }
                
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Social search error for {platform_name}: {str(e)}")
            
            return None
        
        # Search platforms concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(search_platform, platform, url): (platform, url) for platform, url in platforms.items()}
            
            for future in as_completed(futures):
                future.result()
        
        if social_data:
            self.add_finding('social_media', social_data)
            self.data_found.emit(social_data)
        
        return social_data
    
    def _metadata_extraction(self, target: str, delay: float) -> dict:
        """Extract metadata from target"""
        self.osint_status.emit(f"Extracting metadata from {target}")
        
        metadata = {}
        
        try:
            # Ensure URL has protocol
            if not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            
            response = requests.get(target, timeout=30)
            
            # Extract HTTP headers
            headers = dict(response.headers)
            metadata['http_headers'] = headers
            
            # Extract server information
            if 'server' in headers:
                metadata['server_info'] = headers['server']
            
            # Extract powered by information
            if 'x-powered-by' in headers:
                metadata['powered_by'] = headers['x-powered-by']
            
            # Extract cookies
            if 'set-cookie' in headers:
                metadata['cookies'] = headers['set-cookie']
            
            # Extract security headers
            security_headers = [
                'x-frame-options', 'x-xss-protection', 'strict-transport-security',
                'content-security-policy', 'x-content-type-options'
            ]
            
            missing_security_headers = []
            for header in security_headers:
                if header not in headers:
                    missing_security_headers.append(header)
            
            if missing_security_headers:
                metadata['missing_security_headers'] = missing_security_headers
            
            # Extract HTML content
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract meta tags
                meta_tags = soup.find_all('meta')
                meta_info = []
                
                for meta in meta_tags:
                    meta_dict = {
                        'name': meta.get('name', ''),
                        'content': meta.get('content', ''),
                        'property': meta.get('property', '')
                    }
                    meta_info.append(meta_dict)
                
                if meta_info:
                    metadata['meta_tags'] = meta_info
                
                # Extract scripts and technologies
                scripts = soup.find_all('script')
                script_sources = [script.get('src', '') for script in scripts if script.get('src')]
                
                if script_sources:
                    metadata['scripts'] = script_sources
                
                # Extract links
                links = soup.find_all('link')
                link_info = []
                
                for link in links:
                    link_dict = {
                        'href': link.get('href', ''),
                        'rel': link.get('rel', ''),
                        'type': link.get('type', '')
                    }
                    link_info.append(link_dict)
                
                if link_info:
                    metadata['links'] = link_info
            
            time.sleep(delay)
            
        except Exception as e:
            self.logger.error(f"Metadata extraction error: {str(e)}")
        
        if metadata:
            self.add_finding('metadata', metadata)
            self.data_found.emit(metadata)
        
        return metadata
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.osint_status.emit("OSINT stopped by user")
