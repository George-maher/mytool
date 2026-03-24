from PySide6.QtCore import QThread, Signal

class OSINTWorker(QThread):
    """Background worker for OSINT operations"""

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
        """Run OSINT gathering in background"""
        self.is_running = True
        self.should_stop = False

        try:
            self.status.emit(f"Starting OSINT on {self.target}")

            # Simulate OSINT phases
            phases = [
                ("Domain Information", 25),
                ("DNS Records", 20),
                ("Subdomain Discovery", 25),
                ("Email Harvesting", 15),
                ("Social Media Search", 15)
            ]

            results = {
                'target': self.target,
                'scan_type': 'osint',
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
                phase_steps = 6
                for step in range(phase_steps):
                    if self.should_stop:
                        break

                    self.msleep(400)
                    phase_progress = (step + 1) / phase_steps
                    current_progress = total_progress + (phase_progress * phase_weight)
                    self.progress.emit(int(current_progress), 100)

                total_progress += phase_weight

                # Add mock findings
                if phase_name == "Domain Information":
                    results['findings'].append({
                        'type': 'domain_info',
                        'details': f"Domain registered: 2019-01-15, Expires: 2024-01-15"
                    })
                elif phase_name == "DNS Records":
                    results['findings'].append({
                        'type': 'dns_record',
                        'details': "A: 192.168.1.1, MX: mail.example.com"
                    })
                elif phase_name == "Subdomain Discovery":
                    subdomains = ["api.example.com", "blog.example.com", "dev.example.com"]
                    for subdomain in subdomains:
                        results['findings'].append({
                            'type': 'subdomain',
                            'details': f"Found subdomain: {subdomain}"
                        })
                elif phase_name == "Email Harvesting":
                    results['findings'].append({
                        'type': 'email',
                        'details': "Found emails: admin@example.com, support@example.com"
                    })
                elif phase_name == "Social Media Search":
                    results['findings'].append({
                        'type': 'social_media',
                        'details': "LinkedIn: Example Corp, Twitter: @examplecorp"
                    })

            if not self.should_stop:
                results['summary'] = f"OSINT completed for {self.target}. Found {len(results['findings'])} pieces of information."
                self.result.emit(results)

        except Exception as e:
            self.error.emit(f"OSINT error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()

    def stop(self):
        """Stop the OSINT operation"""
        self.should_stop = True
