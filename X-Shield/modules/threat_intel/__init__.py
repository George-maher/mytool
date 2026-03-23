"""
Threat Intelligence Module for X-Shield Framework
Live feed fetching OWASP Top 10 and latest CVEs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_module import NetworkModule
import requests
import json
import time
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import Signal, QTimer, Slot


class Module(NetworkModule):
    """Threat Intelligence Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "Threat Intelligence"
    DESCRIPTION = "Live threat intelligence feed fetching OWASP Top 10 and latest CVEs"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Intelligence"
    
    # Signals
    intel_progress = Signal(int, int)  # current, total
    intel_status = Signal(str)  # status message
    threat_found = Signal(dict)  # threat info
    feed_updated = Signal(str, int)  # feed_name, items_count
    intel_complete = Signal(dict)  # final results
    
    PARAMETERS = {
        'feeds': {
            'type': 'multichoice',
            'label': 'Threat Feeds',
            'default': ['owasp', 'cve', 'exploitdb', 'malware', 'phishing'],
            'choices': ['owasp', 'cve', 'exploitdb', 'malware', 'phishing', 'ransomware'],
            'description': 'Threat intelligence feeds to fetch'
        },
        'days_back': {
            'type': 'integer',
            'label': 'Days Back',
            'default': 30,
            'min': 1,
            'max': 365,
            'description': 'Number of days to look back for threats'
        },
        'severity_filter': {
            'type': 'multichoice',
            'label': 'Severity Filter',
            'default': ['critical', 'high', 'medium', 'low'],
            'choices': ['critical', 'high', 'medium', 'low', 'info'],
            'description': 'Filter threats by severity'
        },
        'cve_api_key': {
            'type': 'string',
            'label': 'CVE API Key',
            'default': '',
            'description': 'API key for CVE database access'
        },
        'auto_refresh': {
            'type': 'boolean',
            'label': 'Auto Refresh',
            'default': True,
            'description': 'Automatically refresh threat feeds'
        },
        'refresh_interval': {
            'type': 'integer',
            'label': 'Refresh Interval (minutes)',
            'default': 60,
            'min': 15,
            'max': 1440,
            'description': 'Auto refresh interval in minutes'
        },
        'max_items': {
            'type': 'integer',
            'label': 'Max Items per Feed',
            'default': 100,
            'min': 10,
            'max': 1000,
            'description': 'Maximum items to fetch per feed'
        }
    }
    
    def __init__(self, logger):
        super().__init__(logger)
        self._stop_requested = False
        self._is_running = False
        self._auto_refresh_timer = None
        
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
        
        # OWASP Top 10 2021 data (static)
        self.owasp_top10 = {
            'A01': {
                'name': 'Broken Access Control',
                'description': 'Access control is only effective if enforced in trusted server-side code or server-less API, where the attacker cannot modify the access control check or metadata.',
                'examples': [
                    'Insecure Direct Object References',
                    'Broken Function Level Authorization',
                    'Missing Function Level Access Control'
                ],
                'impact': 'Severe',
                'prevalence': 'Common'
            },
            'A02': {
                'name': 'Cryptographic Failures',
                'description': 'Failures related to cryptography often lead to the exposure of sensitive data or spoofing.',
                'examples': [
                    'Use of weak algorithms',
                    'Improper key management',
                    'Missing encryption'
                ],
                'impact': 'Severe',
                'prevalence': 'Common'
            },
            'A03': {
                'name': 'Injection',
                'description': 'An attacker can supply untrusted data to a program, which is then executed as part of a command or query.',
                'examples': [
                    'SQL Injection',
                    'NoSQL Injection',
                    'OS Command Injection',
                    'LDAP Injection'
                ],
                'impact': 'Severe',
                'prevalence': 'Common'
            },
            'A04': {
                'name': 'Insecure Design',
                'description': 'Flaws in design and architecture that lead to security vulnerabilities.',
                'examples': [
                    'Lack of security controls',
                    'Insecure business logic',
                    'Poor threat modeling'
                ],
                'impact': 'High',
                'prevalence': 'Widespread'
            },
            'A05': {
                'name': 'Security Misconfiguration',
                'description': 'Failure to implement all the security controls for a server or web application.',
                'examples': [
                    'Missing security headers',
                    'Default credentials',
                    'Verbose error messages'
                ],
                'impact': 'High',
                'prevalence': 'Very Common'
            },
            'A06': {
                'name': 'Vulnerable and Outdated Components',
                'description': 'Using components with known vulnerabilities.',
                'examples': [
                    'Outdated libraries',
                    'Known CVEs in dependencies',
                    'Unpatched software'
                ],
                'impact': 'High',
                'prevalence': 'Common'
            },
            'A07': {
                'name': 'Identification and Authentication Failures',
                'description': 'Incorrectly implemented authentication and session management.',
                'examples': [
                    'Weak passwords',
                    'Session fixation',
                    'Credential stuffing'
                ],
                'impact': 'Severe',
                'prevalence': 'Common'
            },
            'A08': {
                'name': 'Software and Data Integrity Failures',
                'description': 'Code and infrastructure not protected against integrity violations.',
                'examples': [
                    'Insecure CI/CD pipeline',
                    'Unsigned updates',
                    'Insecure deserialization'
                ],
                'impact': 'High',
                'prevalence': 'Common'
            },
            'A09': {
                'name': 'Security Logging and Monitoring Failures',
                'description': 'Insufficient logging and monitoring of security events.',
                'examples': [
                    'No audit trails',
                    'Missing alerts',
                    'Poor log retention'
                ],
                'impact': 'Medium',
                'prevalence': 'Widespread'
            },
            'A10': {
                'name': 'Server-Side Request Forgery (SSRF)',
                'description': 'Server-side application can be induced to make requests to unintended locations.',
                'examples': [
                    'Internal network access',
                    'Cloud metadata access',
                    'File system access'
                ],
                'impact': 'High',
                'prevalence': 'Common'
            }
        }
    
    def execute(self, target: str, parameters: dict) -> dict:
        """Execute threat intelligence gathering"""
        try:
            self._start_execution(target, parameters)
            
            feeds = parameters.get('feeds', ['owasp', 'cve', 'exploitdb'])
            days_back = parameters.get('days_back', 30)
            severity_filter = parameters.get('severity_filter', ['critical', 'high', 'medium', 'low'])
            max_items = parameters.get('max_items', 100)
            auto_refresh = parameters.get('auto_refresh', True)
            refresh_interval = parameters.get('refresh_interval', 60)
            
            threat_data = {}
            total_feeds = len(feeds)
            feeds_processed = 0
            
            # Process each feed
            for feed in feeds:
                if self._stop_requested:
                    break
                
                if feed == 'owasp':
                    data = self._fetch_owasp_data(severity_filter)
                    threat_data['owasp'] = data
                    
                elif feed == 'cve':
                    data = self._fetch_cve_data(days_back, severity_filter, max_items, parameters)
                    threat_data['cve'] = data
                    
                elif feed == 'exploitdb':
                    data = self._fetch_exploitdb_data(days_back, severity_filter, max_items)
                    threat_data['exploitdb'] = data
                    
                elif feed == 'malware':
                    data = self._fetch_malware_data(days_back, severity_filter, max_items)
                    threat_data['malware'] = data
                    
                elif feed == 'phishing':
                    data = self._fetch_phishing_data(days_back, max_items)
                    threat_data['phishing'] = data
                    
                elif feed == 'ransomware':
                    data = self._fetch_ransomware_data(days_back, severity_filter, max_items)
                    threat_data['ransomware'] = data
                
                feeds_processed += 1
                self.intel_progress.emit(feeds_processed, total_feeds)
                self.intel_status.emit(f"Processed {feed} feed")
            
            # Setup auto refresh if enabled
            if auto_refresh:
                self._setup_auto_refresh(refresh_interval, parameters)
            
            self._finish_execution()
            self.intel_complete.emit(self.results)
            return self.results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _fetch_owasp_data(self, severity_filter: list) -> dict:
        """Fetch OWASP Top 10 data"""
        self.intel_status.emit("Fetching OWASP Top 10 data")
        
        owasp_data = {
            'version': '2021',
            'updated': datetime.now().isoformat(),
            'categories': []
        }
        
        for category_id, category_data in self.owasp_top10.items():
            category = {
                'id': category_id,
                'name': category_data['name'],
                'description': category_data['description'],
                'examples': category_data['examples'],
                'impact': category_data['impact'],
                'prevalence': category_data['prevalence'],
                'severity': self._impact_to_severity(category_data['impact'])
            }
            
            if category['severity'] in severity_filter:
                owasp_data['categories'].append(category)
                
                # Add as finding
                self.add_finding('owasp_category', category)
                self.threat_found.emit(category)
        
        self.feed_updated.emit('OWASP Top 10', len(owasp_data['categories']))
        return owasp_data
    
    def _fetch_cve_data(self, days_back: int, severity_filter: list, max_items: int, parameters: dict) -> dict:
        """Fetch CVE data from NIST NVD"""
        self.intel_status.emit("Fetching CVE data from NIST NVD")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # NIST NVD API
            base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            
            # Build query parameters
            params = {
                'cvssV3Severity': ','.join(severity_filter),
                'pubStartDate': start_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'resultsPerPage': min(max_items, 2000)
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                cve_data = {
                    'source': 'NIST NVD',
                    'updated': datetime.now().isoformat(),
                    'total_count': data.get('totalResults', 0),
                    'vulnerabilities': []
                }
                
                for cve_item in data.get('vulnerabilities', [])[:max_items]:
                    cve = cve_item.get('cve', {})
                    cve_id = cve.get('id', '')
                    
                    # Extract CVSS score
                    cvss_score = 0
                    severity = 'unknown'
                    
                    if 'metrics' in cve:
                        cvss_metrics = cve['metrics']
                        if 'cvssMetricV31' in cvss_metrics:
                            cvss_data = cvss_metrics['cvssMetricV31'][0]
                            cvss_score = cvss_data.get('cvssData', {}).get('baseScore', 0)
                            severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'unknown').lower()
                        elif 'cvssMetricV30' in cvss_metrics:
                            cvss_data = cvss_metrics['cvssMetricV30'][0]
                            cvss_score = cvss_data.get('cvssData', {}).get('baseScore', 0)
                            severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'unknown').lower()
                        elif 'cvssMetricV2' in cvss_metrics:
                            cvss_data = cvss_metrics['cvssMetricV2'][0]
                            cvss_score = cvss_data.get('cvssData', {}).get('baseScore', 0)
                            severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'unknown').lower()
                    
                    # Extract description
                    description = ''
                    if 'descriptions' in cve:
                        for desc in cve['descriptions']:
                            if desc.get('lang') == 'en':
                                description = desc.get('value', '')
                                break
                    
                    # Extract published date
                    published_date = cve.get('published', '')
                    
                    vulnerability = {
                        'cve_id': cve_id,
                        'description': description,
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'published_date': published_date,
                        'source': 'NIST NVD'
                    }
                    
                    if severity in severity_filter:
                        cve_data['vulnerabilities'].append(vulnerability)
                        
                        # Add as finding
                        self.add_finding('cve_vulnerability', vulnerability)
                        self.threat_found.emit(vulnerability)
                
                self.feed_updated.emit('CVE Database', len(cve_data['vulnerabilities']))
                return cve_data
                
            else:
                self.intel_status.emit(f"CVE API request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching CVE data: {str(e)}")
            return {}
    
    def _fetch_exploitdb_data(self, days_back: int, severity_filter: list, max_items: int) -> dict:
        """Fetch exploit data from ExploitDB"""
        self.intel_status.emit("Fetching exploit data from ExploitDB")
        
        try:
            # ExploitDB RSS feed
            url = "https://www.exploit-db.com/rss.xml"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                
                root = ET.fromstring(response.content)
                
                exploit_data = {
                    'source': 'ExploitDB',
                    'updated': datetime.now().isoformat(),
                    'exploits': []
                }
                
                for item in root.findall('.//item')[:max_items]:
                    title = item.find('title').text if item.find('title') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    # Extract severity from title/description
                    severity = 'medium'  # Default
                    if 'critical' in title.lower() or 'critical' in description.lower():
                        severity = 'critical'
                    elif 'high' in title.lower() or 'high' in description.lower():
                        severity = 'high'
                    elif 'low' in title.lower() or 'low' in description.lower():
                        severity = 'low'
                    
                    exploit = {
                        'title': title,
                        'description': description,
                        'link': link,
                        'published_date': pub_date,
                        'severity': severity,
                        'source': 'ExploitDB'
                    }
                    
                    if severity in severity_filter:
                        exploit_data['exploits'].append(exploit)
                        
                        # Add as finding
                        self.add_finding('exploit', exploit)
                        self.threat_found.emit(exploit)
                
                self.feed_updated.emit('ExploitDB', len(exploit_data['exploits']))
                return exploit_data
                
            else:
                self.intel_status.emit(f"ExploitDB request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching ExploitDB data: {str(e)}")
            return {}
    
    def _fetch_malware_data(self, days_back: int, severity_filter: list, max_items: int) -> dict:
        """Fetch malware data from various sources"""
        self.intel_status.emit("Fetching malware data")
        
        # This is a simplified version - in production, you'd use specific malware intelligence APIs
        malware_data = {
            'source': 'Multiple Sources',
            'updated': datetime.now().isoformat(),
            'malware_samples': []
        }
        
        # Sample malware families (in production, fetch from real APIs)
        malware_families = [
            {
                'name': 'Emotet',
                'type': 'Banking Trojan',
                'severity': 'high',
                'description': 'Modular banking Trojan that steals financial information',
                'first_seen': '2024-01-15',
                'indicators': ['emotet.exe', 'malware.exe']
            },
            {
                'name': 'TrickBot',
                'type': 'Banking Trojan',
                'severity': 'high',
                'description': 'Banking Trojan with modular architecture',
                'first_seen': '2024-02-20',
                'indicators': ['trickbot.dll', 'infected.exe']
            },
            {
                'name': 'WannaCry',
                'type': 'Ransomware',
                'severity': 'critical',
                'description': 'Worm-like ransomware that spreads via EternalBlue',
                'first_seen': '2024-03-10',
                'indicators': ['wannacry.exe', 'decrypt.html']
            }
        ]
        
        for malware in malware_families[:max_items]:
            if malware['severity'] in severity_filter:
                malware_data['malware_samples'].append(malware)
                
                # Add as finding
                self.add_finding('malware', malware)
                self.threat_found.emit(malware)
        
        self.feed_updated.emit('Malware Intelligence', len(malware_data['malware_samples']))
        return malware_data
    
    def _fetch_phishing_data(self, days_back: int, max_items: int) -> dict:
        """Fetch phishing data from PhishTank"""
        self.intel_status.emit("Fetching phishing data from PhishTank")
        
        try:
            # PhishTank API
            url = "https://data.phishtank.com/data/online-valid.json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                phishing_data = {
                    'source': 'PhishTank',
                    'updated': datetime.now().isoformat(),
                    'phishing_sites': []
                }
                
                for site in data.get('results', [])[:max_items]:
                    phishing_site = {
                        'url': site.get('url', ''),
                        'target': site.get('target', ''),
                        'verified': site.get('verified', False),
                        'submission_date': site.get('submission_date', ''),
                        'source': 'PhishTank'
                    }
                    
                    phishing_data['phishing_sites'].append(phishing_site)
                    
                    # Add as finding
                    self.add_finding('phishing_site', phishing_site)
                    self.threat_found.emit(phishing_site)
                
                self.feed_updated.emit('Phishing Intelligence', len(phishing_data['phishing_sites']))
                return phishing_data
                
            else:
                self.intel_status.emit(f"PhishTank request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching phishing data: {str(e)}")
            return {}
    
    def _fetch_ransomware_data(self, days_back: int, severity_filter: list, max_items: int) -> dict:
        """Fetch ransomware data"""
        self.intel_status.emit("Fetching ransomware data")
        
        # Sample ransomware families (in production, fetch from real APIs)
        ransomware_data = {
            'source': 'Ransomware Intelligence',
            'updated': datetime.now().isoformat(),
            'ransomware_families': []
        }
        
        ransomware_families = [
            {
                'name': 'LockBit',
                'type': 'Ransomware-as-a-Service',
                'severity': 'critical',
                'description': 'RaaS platform with double extortion tactics',
                'first_seen': '2024-01-01',
                'extensions': ['.lockbit', '.encrypted'],
                'ransom_note': 'restore_files.txt'
            },
            {
                'name': 'Conti',
                'type': 'Ransomware',
                'severity': 'critical',
                'description': 'Targeted ransomware with data theft capabilities',
                'first_seen': '2024-02-15',
                'extensions': ['.conti', '.locked'],
                'ransom_note': 'CONTI_README.txt'
            }
        ]
        
        for ransomware in ransomware_families[:max_items]:
            if ransomware['severity'] in severity_filter:
                ransomware_data['ransomware_families'].append(ransomware)
                
                # Add as finding
                self.add_finding('ransomware', ransomware)
                self.threat_found.emit(ransomware)
        
        self.feed_updated.emit('Ransomware Intelligence', len(ransomware_data['ransomware_families']))
        return ransomware_data
    
    def _impact_to_severity(self, impact: str) -> str:
        """Convert OWASP impact to severity"""
        impact_mapping = {
            'Severe': 'critical',
            'High': 'high',
            'Medium': 'medium',
            'Low': 'low'
        }
        return impact_mapping.get(impact, 'medium')
    
    def _setup_auto_refresh(self, interval_minutes: int, parameters: dict):
        """Setup auto refresh timer"""
        if self._auto_refresh_timer:
            self._auto_refresh_timer.stop()
        
        self._auto_refresh_timer = QTimer()
        self._auto_refresh_timer.timeout.connect(
            lambda: self.execute('auto_refresh', parameters)
        )
        self._auto_refresh_timer.start(interval_minutes * 60 * 1000)  # Convert to milliseconds
        
        self.intel_status.emit(f"Auto refresh enabled (every {interval_minutes} minutes)")
    
    def get_threat_summary(self) -> dict:
        """Get summary of current threats"""
        total_threats = 0
        threats_by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for finding in self.results['findings']:
            total_threats += 1
            severity = finding.get('details', {}).get('severity', 'medium')
            if severity in threats_by_severity:
                threats_by_severity[severity] += 1
        
        return {
            'total_threats': total_threats,
            'threats_by_severity': threats_by_severity,
            'last_updated': datetime.now().isoformat()
        }
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        
        # Stop auto refresh timer
        if self._auto_refresh_timer:
            self._auto_refresh_timer.stop()
        
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.intel_status.emit("Threat intelligence stopped by user")
