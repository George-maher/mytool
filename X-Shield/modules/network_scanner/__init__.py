"""
Network Scanner Module for X-Shield Framework
Performs ARP and TCP scanning using Scapy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PySide6.QtCore import Signal, Slot
from core.base_module import NetworkModule
from scapy.all import ARP, Ether, srp, IP, TCP, sr1
import ipaddress
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class Module(NetworkModule):
    """Network Scanner Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "Network Scanner"
    DESCRIPTION = "Advanced network scanning with ARP discovery and TCP port scanning"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Network"
    
    # Signals
    scan_progress = Signal(int, int)  # current, total
    scan_status = Signal(str)  # status message
    host_discovered = Signal(str, str)  # ip, mac
    port_open = Signal(str, int)  # ip, port
    vulnerability_found = Signal(dict)  # vulnerability info
    scan_finished = Signal(dict)  # scan results
    
    PARAMETERS = {
        'scan_type': {
            'type': 'choice',
            'label': 'Scan Type',
            'default': 'arp',
            'choices': ['arp', 'tcp', 'comprehensive'],
            'description': 'Type of scan to perform'
        },
        'port_range': {
            'type': 'string',
            'label': 'Port Range',
            'default': '1-1000',
            'description': 'Port range for TCP scanning (e.g., 1-1000, 22,80,443)'
        },
        'timeout': {
            'type': 'integer',
            'label': 'Timeout (seconds)',
            'default': 2,
            'min': 1,
            'max': 10,
            'description': 'Timeout for network requests'
        },
        'threads': {
            'type': 'integer',
            'label': 'Threads',
            'default': 50,
            'min': 1,
            'max': 200,
            'description': 'Number of concurrent threads'
        },
        'arp_timeout': {
            'type': 'integer',
            'label': 'ARP Timeout (seconds)',
            'default': 3,
            'min': 1,
            'max': 10,
            'description': 'Timeout for ARP requests'
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
        """Execute network scan"""
        try:
            self._start_execution(target, parameters)
            
            scan_type = parameters.get('scan_type', 'arp')
            
            if scan_type == 'arp':
                results = self._arp_scan(target, parameters)
            elif scan_type == 'tcp':
                results = self._tcp_scan(target, parameters)
            elif scan_type == 'comprehensive':
                results = self._comprehensive_scan(target, parameters)
            else:
                raise ValueError(f"Unknown scan type: {scan_type}")
            
            self._finish_execution()
            self.scan_complete.emit(results)
            return results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _arp_scan(self, target: str, parameters: dict) -> dict:
        """Perform ARP scan to discover hosts on network"""
        self.scan_status.emit(f"Starting ARP scan for target: {target}")
        
        # Determine if target is IP or network
        try:
            network = ipaddress.ip_network(target, strict=False)
            if network.prefixlen < 24:
                self.scan_status.emit("Large network detected, limiting to /24 subnet")
                network = ipaddress.ip_network(f"{network.network_address}/24", strict=False)
        except ValueError:
            # Single IP address
            network = ipaddress.ip_network(f"{target}/32", strict=False)
        
        # Create ARP request
        arp_request = ARP(pdst=str(network))
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        
        # Send ARP requests
        timeout = parameters.get('arp_timeout', 3)
        answered_list, unanswered_list = srp(arp_request_broadcast, timeout=timeout, verbose=False)
        
        # Process results
        hosts_discovered = []
        total_ips = network.num_addresses
        
        for i, (sent, received) in enumerate(answered_list):
            if self._stop_requested:
                break
            
            host_info = {
                'ip': received.psrc,
                'mac': received.hwsrc,
                'vendor': self._get_mac_vendor(received.hwsrc)
            }
            hosts_discovered.append(host_info)
            
            self.add_finding('host_discovered', host_info)
            self.host_discovered.emit(host_info)
            self.scan_progress.emit(i + 1, total_ips)
            self.increment_items_scanned()
        
        self.set_summary(f"ARP scan completed. Discovered {len(hosts_discovered)} hosts on network {target}")
        return self.results
    
    def _tcp_scan(self, target: str, parameters: dict) -> dict:
        """Perform TCP port scan"""
        self.scan_status.emit(f"Starting TCP port scan for target: {target}")
        
        port_range = parameters.get('port_range', '1-1000')
        ports = self._parse_port_range(port_range)
        timeout = parameters.get('timeout', 2)
        threads = parameters.get('threads', 50)
        
        open_ports = []
        closed_ports = []
        filtered_ports = []
        
        def scan_port(port):
            if self._stop_requested:
                return None
            
            try:
                # Create TCP SYN packet
                syn_packet = IP(dst=target) / TCP(dport=port, flags="S")
                response = sr1(syn_packet, timeout=timeout, verbose=False)
                
                if response is None:
                    result = {'port': port, 'state': 'filtered'}
                elif response.haslayer(TCP):
                    tcp_layer = response.getlayer(TCP)
                    if tcp_layer.flags == 0x12:  # SYN-ACK
                        # Send RST to close connection
                        rst_packet = IP(dst=target) / TCP(dport=port, flags="R")
                        sr1(rst_packet, timeout=timeout, verbose=False)
                        result = {'port': port, 'state': 'open', 'service': self._get_service_name(port)}
                    elif tcp_layer.flags == 0x14:  # RST-ACK
                        result = {'port': port, 'state': 'closed'}
                    else:
                        result = {'port': port, 'state': 'unknown'}
                else:
                    result = {'port': port, 'state': 'filtered'}
                
                self.port_scanned.emit(result)
                return result
                
            except Exception as e:
                return {'port': port, 'state': 'error', 'error': str(e)}
        
        # Scan ports concurrently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(scan_port, port): port for port in ports}
            
            for i, future in enumerate(as_completed(futures)):
                if self._stop_requested:
                    break
                
                result = future.result()
                if result:
                    if result['state'] == 'open':
                        open_ports.append(result)
                        self.add_finding('open_port', result)
                    elif result['state'] == 'closed':
                        closed_ports.append(result)
                    elif result['state'] == 'filtered':
                        filtered_ports.append(result)
                
                self.scan_progress.emit(i + 1, len(ports))
                self.increment_items_scanned()
        
        # Check for common vulnerabilities
        self._check_port_vulnerabilities(open_ports, target)
        
        self.set_summary(f"TCP scan completed. {len(open_ports)} open ports, {len(closed_ports)} closed, {len(filtered_ports)} filtered")
        return self.results
    
    def _comprehensive_scan(self, target: str, parameters: dict) -> dict:
        """Perform comprehensive scan (ARP + TCP)"""
        self.scan_status.emit(f"Starting comprehensive scan for target: {target}")
        
        # First, determine if target is a network or single host
        try:
            network = ipaddress.ip_network(target, strict=False)
            if network.prefixlen < 30:  # Likely a network
                # Perform ARP scan first
                arp_results = self._arp_scan(target, parameters)
                
                # Then scan each discovered host
                all_hosts = []
                for finding in arp_results['findings']:
                    if finding['type'] == 'host_discovered':
                        all_hosts.append(finding['details']['ip'])
                
                for host in all_hosts:
                    if self._stop_requested:
                        break
                    self._tcp_scan(host, parameters)
                
                self.set_summary(f"Comprehensive scan completed for {target}")
            else:
                # Single host, just TCP scan
                self._tcp_scan(target, parameters)
                self.set_summary(f"Comprehensive scan completed for {target}")
                
        except ValueError:
            # Not a valid network, treat as single host
            self._tcp_scan(target, parameters)
            self.set_summary(f"Comprehensive scan completed for {target}")
        
        return self.results
    
    def _parse_port_range(self, port_range: str) -> list:
        """Parse port range string into list of ports"""
        ports = []
        
        for part in port_range.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(part))
        
        return sorted(set(ports))
    
    def _get_service_name(self, port: int) -> str:
        """Get common service name for port"""
        common_ports = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
            6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
        }
        return common_ports.get(port, 'Unknown')
    
    def _get_mac_vendor(self, mac_address: str) -> str:
        """Get vendor from MAC address (simplified)"""
        # This is a simplified version - in production, use a proper OUI database
        oui = mac_address[:8].upper()
        
        vendor_map = {
            '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox',
            '52:54:00': 'QEMU/KVM',
            '00:0C:29': 'VMware',
            '00:1C:42': 'Parallels',
            '00:03:FF': 'Microsoft Hyper-V',
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi'
        }
        
        return vendor_map.get(oui, 'Unknown')
    
    def _check_port_vulnerabilities(self, open_ports: list, target: str):
        """Check for common port-based vulnerabilities"""
        for port_info in open_ports:
            port = port_info['port']
            
            # Check for common vulnerable services
            if port == 21 and port_info.get('service') == 'FTP':
                vulnerability = {
                    'title': 'FTP Service Detected',
                    'severity': 'medium',
                    'description': 'FTP service is running. Consider using SFTP instead.',
                    'target': f"{target}:{port}",
                    'recommendation': 'Disable FTP if not needed, or use secure alternatives like SFTP.'
                }
                self.add_vulnerability(vulnerability)
                self.vulnerability_found.emit(vulnerability)
            
            elif port == 23 and port_info.get('service') == 'Telnet':
                vulnerability = {
                    'title': 'Telnet Service Detected',
                    'severity': 'high',
                    'description': 'Telnet service is running with unencrypted communication.',
                    'target': f"{target}:{port}",
                    'recommendation': 'Disable Telnet and use SSH for secure remote access.'
                }
                self.add_vulnerability(vulnerability)
                self.vulnerability_found.emit(vulnerability)
            
            elif port == 3389 and port_info.get('service') == 'RDP':
                vulnerability = {
                    'title': 'RDP Service Detected',
                    'severity': 'medium',
                    'description': 'Remote Desktop Protocol is enabled.',
                    'target': f"{target}:{port}",
                    'recommendation': 'Ensure RDP is properly secured with strong passwords and network restrictions.'
                }
                self.add_vulnerability(vulnerability)
                self.vulnerability_found.emit(vulnerability)
            
            elif port in [3306, 5432, 1433]:
                vulnerability = {
                    'title': 'Database Service Exposed',
                    'severity': 'high',
                    'description': f'Database service is exposed to network.',
                    'target': f"{target}:{port}",
                    'recommendation': 'Restrict database access to trusted networks only.'
                }
                self.add_vulnerability(vulnerability)
                self.vulnerability_found.emit(vulnerability)
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.scan_status.emit("Scan stopped by user")
