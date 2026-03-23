"""
Report Model for X-Shield Framework
MVC Model for report generation and management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from mvc.base import BaseModel
from mvc.events import EventBus, EventTypes


class ReportModel(BaseModel):
    """Model for managing security reports"""
    
    def __init__(self, storage_path: str = "data/reports.json", output_dir: str = "data/reports"):
        super().__init__()
        self.storage_path = storage_path
        self.output_dir = output_dir
        self._data = {
            'reports': {},
            'templates': [
                'Comprehensive Security Report',
                'Vulnerability Summary',
                'Network Scan Report',
                'Web Application Report',
                'Executive Summary'
            ],
            'formats': ['HTML', 'PDF', 'JSON', 'CSV'],
            'last_updated': None
        }
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_report(self, report_type: str, scan_ids: List[str], 
                     template: str = None, format_type: str = 'HTML',
                     options: Dict[str, Any] = None) -> str:
        """Create a new report"""
        report_id = str(uuid4())
        
        report = {
            'id': report_id,
            'type': report_type,
            'scan_ids': scan_ids,
            'template': template or 'Comprehensive Security Report',
            'format': format_type,
            'options': options or {},
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'generated_at': None,
            'file_path': None,
            'file_size': 0,
            'metadata': {
                'title': f'{report_type} Report',
                'description': f'Generated report for {len(scan_ids)} scans',
                'author': 'X-Shield Framework',
                'version': '1.0'
            }
        }
        
        self._data['reports'][report_id] = report
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        return report_id
    
    def generate_report(self, report_id: str, scan_data: List[Dict[str, Any]]) -> bool:
        """Generate report file"""
        if report_id not in self._data['reports']:
            return False
        
        report = self._data['reports'][report_id]
        report['status'] = 'generating'
        
        try:
            # Generate report content
            content = self._generate_report_content(report, scan_data)
            
            # Save to file
            file_path = self._save_report_file(report, content)
            
            # Update report metadata
            report['status'] = 'completed'
            report['generated_at'] = datetime.now().isoformat()
            report['file_path'] = file_path
            report['file_size'] = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            self._data['last_updated'] = datetime.now().isoformat()
            self.set_data(self._data)
            
            # Emit event
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.REPORT_GENERATED, report, 'ReportModel')
            
            return True
            
        except Exception as e:
            report['status'] = 'failed'
            report['error'] = str(e)
            
            self._data['last_updated'] = datetime.now().isoformat()
            self.set_data(self._data)
            
            # Emit error event
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.publish_sync(EventTypes.REPORT_ERROR, report, 'ReportModel')
            
            return False
    
    def _generate_report_content(self, report: Dict[str, Any], scan_data: List[Dict[str, Any]]) -> str:
        """Generate report content based on format"""
        format_type = report['format'].lower()
        
        if format_type == 'html':
            return self._generate_html_report(report, scan_data)
        elif format_type == 'json':
            return self._generate_json_report(report, scan_data)
        elif format_type == 'csv':
            return self._generate_csv_report(report, scan_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_html_report(self, report: Dict[str, Any], scan_data: List[Dict[str, Any]]) -> str:
        """Generate HTML report"""
        # Aggregate data from all scans
        all_vulnerabilities = []
        all_findings = []
        scan_statistics = {}
        
        for scan in scan_data:
            results = scan.get('results', {})
            all_vulnerabilities.extend(results.get('vulnerabilities', []))
            all_findings.extend(results.get('findings', []))
        
        # Sort vulnerabilities by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
        all_vulnerabilities.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 4))
        
        # Generate HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report['metadata']['title']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .risk-critical {{ background-color: #dc2626; }}
        .risk-high {{ background-color: #ea580c; }}
        .risk-medium {{ background-color: #d97706; }}
        .risk-low {{ background-color: #65a30d; }}
        .risk-info {{ background-color: #0891b2; }}
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-center mb-4">{report['metadata']['title']}</h1>
            <div class="text-center text-gray-400">
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Scans analyzed: {len(scan_data)}</p>
            </div>
        </header>

        <!-- Executive Summary -->
        <section class="mb-12">
            <h2 class="text-2xl font-bold mb-6">Executive Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">Total Vulnerabilities</h3>
                    <p class="text-3xl font-bold text-red-400">{len(all_vulnerabilities)}</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">Critical Issues</h3>
                    <p class="text-3xl font-bold text-red-600">
                        {len([v for v in all_vulnerabilities if v.get('severity') == 'Critical'])}
                    </p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">High Risk</h3>
                    <p class="text-3xl font-bold text-orange-500">
                        {len([v for v in all_vulnerabilities if v.get('severity') == 'High'])}
                    </p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2">Total Findings</h3>
                    <p class="text-3xl font-bold text-blue-400">{len(all_findings)}</p>
                </div>
            </div>
        </section>

        <!-- Risk Dashboard -->
        <section class="mb-12">
            <h2 class="text-2xl font-bold mb-6">Risk Dashboard</h2>
            <div id="riskChart" style="height: 400px;"></div>
        </section>

        <!-- Vulnerabilities -->
        <section class="mb-12">
            <h2 class="text-2xl font-bold mb-6">Vulnerabilities ({len(all_vulnerabilities)})</h2>
            <div class="space-y-4">
        """
        
        # Add vulnerabilities to HTML
        for vuln in all_vulnerabilities:
            severity = vuln.get('severity', 'Info').lower()
            html_content += f"""
                <div class="bg-gray-800 p-6 rounded-lg border-l-4 border-{severity}-500">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-semibold">{vuln.get('title', 'Unknown')}</h3>
                        <span class="px-3 py-1 rounded text-sm font-semibold risk-{severity}">
                            {vuln.get('severity', 'Info')}
                        </span>
                    </div>
                    <p class="text-gray-300 mb-2">{vuln.get('description', 'No description')}</p>
                    <p class="text-sm text-gray-400">
                        Target: {vuln.get('target', 'Unknown')} | 
                        CVSS: {vuln.get('cvss_score', 'N/A')}
                    </p>
                </div>
            """
        
        html_content += """
            </div>
        </section>

        <!-- Findings -->
        <section class="mb-12">
            <h2 class="text-2xl font-bold mb-6">Additional Findings</h2>
            <div class="space-y-4">
        """
        
        # Add findings to HTML
        for finding in all_findings:
            html_content += f"""
                <div class="bg-gray-800 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">{finding.get('title', 'Unknown')}</h3>
                    <p class="text-gray-300 text-sm">{finding.get('description', 'No description')}</p>
                </div>
            """
        
        html_content += f"""
            </div>
        </section>

        <!-- Footer -->
        <footer class="mt-12 pt-8 border-t border-gray-700 text-center text-gray-400">
            <p>Report generated by {report['metadata']['author']} v{report['metadata']['version']}</p>
            <p>This report contains sensitive information - handle with care</p>
        </footer>
    </div>

    <script>
        // Risk Chart
        const severityData = {{
            'Critical': {len([v for v in all_vulnerabilities if v.get('severity') == 'Critical'])},
            'High': {len([v for v in all_vulnerabilities if v.get('severity') == 'High'])},
            'Medium': {len([v for v in all_vulnerabilities if v.get('severity') == 'Medium'])},
            'Low': {len([v for v in all_vulnerabilities if v.get('severity') == 'Low'])},
            'Info': {len([v for v in all_vulnerabilities if v.get('severity') == 'Info'])}
        }};

        const data = [{{
            x: Object.keys(severityData),
            y: Object.values(severityData),
            type: 'bar',
            marker: {{
                color: ['#dc2626', '#ea580c', '#d97706', '#65a30d', '#0891b2']
            }}
        }}];

        const layout = {{
            title: 'Vulnerability Severity Distribution',
            paper_bgcolor: '#1f2937',
            plot_bgcolor: '#111827',
            font: {{ color: '#ffffff' }},
            xaxis: {{ title: 'Severity', tickcolor: '#ffffff' }},
            yaxis: {{ title: 'Count', tickcolor: '#ffffff' }}
        }};

        Plotly.newPlot('riskChart', data, layout);
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _generate_json_report(self, report: Dict[str, Any], scan_data: List[Dict[str, Any]]) -> str:
        """Generate JSON report"""
        report_data = {
            'metadata': report['metadata'],
            'generated_at': datetime.now().isoformat(),
            'report_config': {
                'type': report['type'],
                'template': report['template'],
                'format': report['format'],
                'scan_count': len(scan_data)
            },
            'scans': scan_data,
            'summary': self._generate_summary(scan_data)
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
    
    def _generate_csv_report(self, report: Dict[str, Any], scan_data: List[Dict[str, Any]]) -> str:
        """Generate CSV report"""
        import csv
        import io
        
        output = io.StringIO()
        
        # Collect all vulnerabilities
        all_vulnerabilities = []
        for scan in scan_data:
            results = scan.get('results', {})
            for vuln in results.get('vulnerabilities', []):
                vuln_copy = vuln.copy()
                vuln_copy['scan_id'] = scan.get('id')
                vuln_copy['scan_target'] = scan.get('target')
                all_vulnerabilities.append(vuln_copy)
        
        if not all_vulnerabilities:
            return "No vulnerabilities found"
        
        # Write CSV
        fieldnames = ['scan_id', 'scan_target', 'title', 'severity', 'description', 'target', 'cvss_score']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for vuln in all_vulnerabilities:
            row = {field: vuln.get(field, '') for field in fieldnames}
            writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_summary(self, scan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report summary"""
        all_vulnerabilities = []
        all_findings = []
        
        for scan in scan_data:
            results = scan.get('results', {})
            all_vulnerabilities.extend(results.get('vulnerabilities', []))
            all_findings.extend(results.get('findings', []))
        
        # Count by severity
        severity_counts = {}
        for vuln in all_vulnerabilities:
            severity = vuln.get('severity', 'Info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_vulnerabilities': len(all_vulnerabilities),
            'total_findings': len(all_findings),
            'severity_distribution': severity_counts,
            'scan_count': len(scan_data),
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_report_file(self, report: Dict[str, Any], content: str) -> str:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{report['id']}_{timestamp}.{report['format'].lower()}"
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report by ID"""
        return self._data['reports'].get(report_id)
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Get all reports"""
        return list(self._data['reports'].values())
    
    def get_reports_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get reports by status"""
        return [r for r in self.get_all_reports() if r['status'] == status]
    
    def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reports"""
        all_reports = self.get_all_reports()
        all_reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return all_reports[:limit]
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a report"""
        if report_id not in self._data['reports']:
            return False
        
        report = self._data['reports'][report_id]
        
        # Delete file if exists
        if report.get('file_path') and os.path.exists(report['file_path']):
            try:
                os.remove(report['file_path'])
            except Exception:
                pass  # Continue even if file deletion fails
        
        # Remove from data
        del self._data['reports'][report_id]
        self._data['last_updated'] = datetime.now().isoformat()
        self.set_data(self._data)
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get report statistics"""
        all_reports = self.get_all_reports()
        
        stats = {
            'total_reports': len(all_reports),
            'by_status': {},
            'by_type': {},
            'by_format': {},
            'total_file_size': 0,
            'recent_reports': len([r for r in all_reports 
                                if (datetime.now() - datetime.fromisoformat(r['created_at'])).days <= 30])
        }
        
        for report in all_reports:
            status = report['status']
            report_type = report['type']
            format_type = report['format']
            
            if status not in stats['by_status']:
                stats['by_status'][status] = 0
            stats['by_status'][status] += 1
            
            if report_type not in stats['by_type']:
                stats['by_type'][report_type] = 0
            stats['by_type'][report_type] += 1
            
            if format_type not in stats['by_format']:
                stats['by_format'][format_type] = 0
            stats['by_format'][format_type] += 1
            
            stats['total_file_size'] += report.get('file_size', 0)
        
        return stats
    
    # Base model implementation
    def _persist_data(self) -> bool:
        """Save reports to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._errors.append(f"Save failed: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """Load reports from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                if isinstance(loaded_data, dict):
                    self._data = loaded_data
                    # Ensure required keys
                    if 'reports' not in self._data:
                        self._data['reports'] = {}
                    return True
            return False
        except Exception as e:
            self._errors.append(f"Load failed: {str(e)}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate report data"""
        self._errors.clear()
        
        if not isinstance(self._data, dict):
            self._errors.append("Data must be a dictionary")
            return False
        
        if 'reports' not in self._data:
            self._errors.append("Missing reports key")
            return False
        
        if not isinstance(self._data['reports'], dict):
            self._errors.append("Reports must be a dictionary")
            return False
        
        # Validate each report
        for report_id, report in self._data['reports'].items():
            if not isinstance(report, dict):
                self._errors.append(f"Report {report_id} must be a dictionary")
                continue
            
            required_fields = ['id', 'type', 'scan_ids', 'format', 'status']
            for field in required_fields:
                if field not in report:
                    self._errors.append(f"Report {report_id} missing required field: {field}")
        
        return len(self._errors) == 0
    
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for model events"""
        self._event_bus = event_bus
