from PySide6.QtCore import QThread, Signal

class WebScannerWorker(QThread):
    """Background worker for web scanning"""

    # Signals
    progress = Signal(int, int)
    status = Signal(str)
    result = Signal(dict)
    error = Signal(str)
    finished = Signal()

    def __init__(self, target, parameters=None):
        super().__init__()
        self.target = target
        self.parameters = parameters or {}
        self.is_running = False
        self.should_stop = False

    def run(self):
        """Run the web scan in background"""
        self.is_running = True
        self.should_stop = False

        try:
            self.status.emit(f"Starting web scan on {self.target}")

            # Simulate web scan phases
            phases = [
                ("HTTP Headers", 15),
                ("Directory Discovery", 25),
                ("Technology Identification", 20),
                ("Security Headers", 20),
                ("Common Vulnerabilities", 20)
            ]

            results = {
                'target': self.target,
                'scan_type': 'web',
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

                # Simulate work
                phase_steps = 8
                for step in range(phase_steps):
                    if self.should_stop:
                        break

                    self.msleep(300)
                    phase_progress = (step + 1) / phase_steps
                    current_progress = total_progress + (phase_progress * phase_weight)
                    self.progress.emit(int(current_progress), 100)

                total_progress += phase_weight

                # Add mock findings
                if phase_name == "HTTP Headers":
                    results['findings'].append({
                        'type': 'server_header',
                        'details': f"Server: Apache/2.4.41"
                    })
                elif phase_name == "Directory Discovery":
                    dirs = ["/admin", "/backup", "/config"]
                    for directory in dirs:
                        results['findings'].append({
                            'type': 'directory',
                            'details': f"Found directory: {directory}"
                        })
                elif phase_name == "Technology Identification":
                    results['findings'].append({
                        'type': 'technology',
                        'details': "Technologies: PHP, MySQL, jQuery"
                    })
                elif phase_name == "Security Headers":
                    results['findings'].append({
                        'type': 'security_header',
                        'details': "Missing X-Frame-Options header"
                    })
                elif phase_name == "Common Vulnerabilities":
                    results['vulnerabilities'] = [
                        {
                            'severity': 'High',
                            'title': 'SQL Injection',
                            'description': 'Potential SQL injection in search parameter'
                        },
                        {
                            'severity': 'Medium',
                            'title': 'XSS Vulnerability',
                            'description': 'Cross-site scripting in comment field'
                        }
                    ]

            if not self.should_stop:
                results['summary'] = f"Web scan completed for {self.target}. Found {len(results['findings'])} findings and {len(results['vulnerabilities'])} vulnerabilities."
                self.result.emit(results)

        except Exception as e:
            self.error.emit(f"Scan error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()

    def stop(self):
        """Stop the scan"""
        self.should_stop = True
