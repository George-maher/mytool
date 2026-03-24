from PySide6.QtCore import QThread, Signal

class NetworkScannerWorker(QThread):
    """Background worker for network scanning"""

    # Signals
    progress = Signal(int, int)  # current, total
    status = Signal(str)        # status message
    result = Signal(dict)       # scan result
    error = Signal(str)         # error message
    finished = Signal()         # scan finished

    def __init__(self, target, parameters=None):
        super().__init__()
        self.target = target
        self.parameters = parameters or {}
        self.is_running = False
        self.should_stop = False

    def run(self):
        """Run the network scan in background"""
        self.is_running = True
        self.should_stop = False

        try:
            self.status.emit(f"Starting network scan on {self.target}")

            # Simulate network scan with different phases
            phases = [
                ("Host Discovery", 20),
                ("Port Scanning", 40),
                ("Service Detection", 30),
                ("OS Fingerprinting", 10)
            ]

            results = {
                'target': self.target,
                'scan_type': 'network',
                'timestamp': None,
                'findings': [],
                'vulnerabilities': [],
                'summary': ''
            }

            total_progress = 0
            for phase_name, phase_weight in phases:
                if self.should_stop:
                    break

                self.status.emit(f"Phase: {phase_name}")

                # Simulate work with progress updates
                phase_steps = 10
                for step in range(phase_steps):
                    if self.should_stop:
                        break

                    # Simulate scanning work
                    self.msleep(200)  # 200ms delay

                    # Emit progress
                    phase_progress = (step + 1) / phase_steps
                    current_progress = total_progress + (phase_progress * phase_weight)
                    self.progress.emit(int(current_progress), 100)

                total_progress += phase_weight

                # Add mock findings
                if phase_name == "Host Discovery":
                    results['findings'].append({
                        'type': 'host_alive',
                        'details': f"Host {self.target} is responding to ping"
                    })
                elif phase_name == "Port Scanning":
                    open_ports = [22, 80, 443, 8080]
                    for port in open_ports:
                        results['findings'].append({
                            'type': 'open_port',
                            'details': f"Port {port} is open"
                        })
                elif phase_name == "Service Detection":
                    services = {
                        22: "SSH",
                        80: "HTTP",
                        443: "HTTPS",
                        8080: "HTTP-Alt"
                    }
                    for port, service in services.items():
                        results['findings'].append({
                            'type': 'service',
                            'details': f"Port {port}: {service}"
                        })
                elif phase_name == "OS Fingerprinting":
                    results['findings'].append({
                        'type': 'os_info',
                        'details': "OS fingerprint: Linux (likely Ubuntu)"
                    })

            # Add mock vulnerabilities
            if not self.should_stop:
                results['vulnerabilities'] = [
                    {
                        'severity': 'Medium',
                        'title': 'SSH Version 7.4',
                        'description': 'SSH server version may have known vulnerabilities'
                    },
                    {
                        'severity': 'Low',
                        'title': 'HTTP Server Header',
                        'description': 'Server header exposes server information'
                    }
                ]

                results['summary'] = f"Network scan completed for {self.target}. Found {len(results['findings'])} findings and {len(results['vulnerabilities'])} potential vulnerabilities."

            if not self.should_stop:
                self.result.emit(results)

        except Exception as e:
            self.error.emit(f"Scan error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()

    def stop(self):
        """Stop the scan"""
        self.should_stop = True
