"""
Advanced Reporting Module for X-Shield Framework
Generates professional HTML reports with Tailwind CSS and interactive charts
"""

import json
import os
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Signal, QObject
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Template


class ReportGenerator(QObject):
    """Generates professional pentesting reports"""
    
    report_generated = Signal(str)  # report_path
    
    def __init__(self):
        super().__init__()
        self.reports_dir = Path("data/reports")
        self.templates_dir = Path("reports/templates")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default template if not exists
        self.create_default_template()
    
    def create_default_template(self):
        """Create default HTML report template"""
        template_path = self.templates_dir / "default_report.html"
        if not template_path.exists():
            template_content = self.get_default_template()
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
    
    def get_default_template(self):
        """Get the default HTML template with Tailwind CSS"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X-Shield Pentesting Report - {{ report_title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .glass-effect {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .severity-critical { border-left: 4px solid #dc2626; }
        .severity-high { border-left: 4px solid #ea580c; }
        .severity-medium { border-left: 4px solid #ca8a04; }
        .severity-low { border-left: 4px solid #16a34a; }
        .severity-info { border-left: 4px solid #3b82f6; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100">
    <!-- Header -->
    <header class="gradient-bg shadow-2xl">
        <div class="container mx-auto px-6 py-8">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="bg-white rounded-lg p-3">
                        <i class="fas fa-shield-alt text-3xl text-purple-600"></i>
                    </div>
                    <div>
                        <h1 class="text-3xl font-bold text-white">X-Shield</h1>
                        <p class="text-purple-100">Professional Pentesting Framework</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-purple-100 font-semibold">{{ report_title }}</p>
                    <p class="text-purple-200 text-sm">Generated: {{ generation_date }}</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
        <!-- Executive Summary -->
        <section class="mb-12">
            <div class="bg-gray-800 rounded-xl shadow-xl p-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-chart-line mr-3 text-purple-400"></i>
                    Executive Summary
                </h2>
                
                <!-- Risk Score Card -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-gradient-to-br from-red-600 to-red-800 rounded-lg p-6 text-center">
                        <div class="text-4xl font-bold">{{ risk_score }}</div>
                        <div class="text-red-100">Risk Score</div>
                    </div>
                    <div class="bg-gradient-to-br from-orange-600 to-orange-800 rounded-lg p-6 text-center">
                        <div class="text-4xl font-bold">{{ total_vulnerabilities }}</div>
                        <div class="text-orange-100">Total Vulnerabilities</div>
                    </div>
                    <div class="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 text-center">
                        <div class="text-4xl font-bold">{{ modules_run }}</div>
                        <div class="text-blue-100">Modules Executed</div>
                    </div>
                    <div class="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6 text-center">
                        <div class="text-4xl font-bold">{{ scan_duration }}</div>
                        <div class="text-green-100">Duration (min)</div>
                    </div>
                </div>

                <!-- Risk Assessment Chart -->
                <div class="bg-gray-700 rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4">Vulnerability Distribution</h3>
                    <div id="riskChart"></div>
                </div>
            </div>
        </section>

        <!-- Target Information -->
        <section class="mb-12">
            <div class="bg-gray-800 rounded-xl shadow-xl p-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-bullseye mr-3 text-purple-400"></i>
                    Target Information
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-700 rounded-lg p-6">
                        <h3 class="text-lg font-semibold mb-4 text-purple-300">Primary Target</h3>
                        <p class="text-2xl font-mono text-green-400">{{ primary_target }}</p>
                        <p class="text-gray-400 mt-2">{{ target_description }}</p>
                    </div>
                    <div class="bg-gray-700 rounded-lg p-6">
                        <h3 class="text-lg font-semibold mb-4 text-purple-300">Scan Scope</h3>
                        <ul class="space-y-2">
                            {% for scope_item in scan_scope %}
                            <li class="flex items-center text-gray-300">
                                <i class="fas fa-check-circle text-green-400 mr-2"></i>
                                {{ scope_item }}
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- Module Results -->
        <section class="mb-12">
            <div class="bg-gray-800 rounded-xl shadow-xl p-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-cogs mr-3 text-purple-400"></i>
                    Module Execution Results
                </h2>
                
                {% for module in modules %}
                <div class="bg-gray-700 rounded-lg p-6 mb-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-semibold text-purple-300">{{ module.name }}</h3>
                        <span class="px-3 py-1 rounded-full text-sm font-medium
                            {% if module.status == 'completed' %}bg-green-600 text-green-100
                            {% elif module.status == 'failed' %}bg-red-600 text-red-100
                            {% else %}bg-yellow-600 text-yellow-100{% endif %}">
                            {{ module.status.upper() }}
                        </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                            <span class="text-gray-400 text-sm">Duration:</span>
                            <span class="ml-2 font-mono">{{ module.duration }}s</span>
                        </div>
                        <div>
                            <span class="text-gray-400 text-sm">Items Scanned:</span>
                            <span class="ml-2 font-mono">{{ module.items_scanned }}</span>
                        </div>
                        <div>
                            <span class="text-gray-400 text-sm">Issues Found:</span>
                            <span class="ml-2 font-mono text-red-400">{{ module.issues_found }}</span>
                        </div>
                    </div>
                    
                    {% if module.summary %}
                    <p class="text-gray-300">{{ module.summary }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- Vulnerabilities -->
        <section class="mb-12">
            <div class="bg-gray-800 rounded-xl shadow-xl p-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-exclamation-triangle mr-3 text-purple-400"></i>
                    Vulnerabilities Found
                </h2>
                
                {% if vulnerabilities %}
                {% for vuln in vulnerabilities %}
                <div class="bg-gray-700 rounded-lg p-6 mb-6 severity-{{ vuln.severity }}">
                    <div class="flex items-start justify-between mb-4">
                        <div>
                            <h3 class="text-xl font-semibold text-white">{{ vuln.title }}</h3>
                            <p class="text-gray-400 mt-1">{{ vuln.target }}</p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-sm font-bold uppercase
                            {% if vuln.severity == 'critical' %}bg-red-600 text-white
                            {% elif vuln.severity == 'high' %}bg-orange-600 text-white
                            {% elif vuln.severity == 'medium' %}bg-yellow-600 text-black
                            {% elif vuln.severity == 'low' %}bg-green-600 text-white
                            {% else %}bg-blue-600 text-white{% endif %}">
                            {{ vuln.severity }}
                        </span>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="font-semibold text-purple-300 mb-2">Description</h4>
                        <p class="text-gray-300">{{ vuln.description }}</p>
                    </div>
                    
                    {% if vuln.technical_details %}
                    <div class="mb-4">
                        <h4 class="font-semibold text-purple-300 mb-2">Technical Details</h4>
                        <pre class="bg-gray-800 rounded p-4 text-sm text-gray-300 overflow-x-auto">{{ vuln.technical_details }}</pre>
                    </div>
                    {% endif %}
                    
                    {% if vuln.recommendation %}
                    <div>
                        <h4 class="font-semibold text-purple-300 mb-2">Recommendation</h4>
                        <p class="text-gray-300">{{ vuln.recommendation }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
                {% else %}
                <div class="bg-gray-700 rounded-lg p-8 text-center">
                    <i class="fas fa-check-circle text-6xl text-green-400 mb-4"></i>
                    <p class="text-xl text-gray-300">No vulnerabilities found!</p>
                    <p class="text-gray-400 mt-2">The target appears to be secure based on the scans performed.</p>
                </div>
                {% endif %}
            </div>
        </section>

        <!-- Timeline -->
        <section class="mb-12">
            <div class="bg-gray-800 rounded-xl shadow-xl p-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-clock mr-3 text-purple-400"></i>
                    Execution Timeline
                </h2>
                <div id="timelineChart"></div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 border-t border-gray-700 mt-12">
        <div class="container mx-auto px-6 py-8">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="flex items-center space-x-4 mb-4 md:mb-0">
                    <i class="fas fa-shield-alt text-2xl text-purple-400"></i>
                    <div>
                        <p class="font-semibold">X-Shield Pentesting Framework</p>
                        <p class="text-gray-400 text-sm">Professional Security Assessment Tool</p>
                    </div>
                </div>
                <div class="text-center md:text-right">
                    <p class="text-gray-400">Report generated on {{ generation_date }}</p>
                    <p class="text-gray-500 text-sm">This report contains confidential security information</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript for Charts -->
    <script>
        // Risk Distribution Chart
        const riskData = {{ risk_chart_data | safe }};
        const riskLayout = {
            title: '',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            xaxis: { 
                gridcolor: '#374151',
                tickcolor: '#9ca3af'
            },
            yaxis: { 
                gridcolor: '#374151',
                tickcolor: '#9ca3af'
            }
        };
        Plotly.newPlot('riskChart', riskData, riskLayout);

        // Timeline Chart
        const timelineData = {{ timeline_chart_data | safe }};
        const timelineLayout = {
            title: '',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            xaxis: { 
                title: 'Time',
                gridcolor: '#374151',
                tickcolor: '#9ca3af'
            },
            yaxis: { 
                title: 'Module',
                gridcolor: '#374151',
                tickcolor: '#9ca3af'
            }
        };
        Plotly.newPlot('timelineChart', timelineData, timelineLayout);
    </script>
</body>
</html>
        """
    
    def generate_report(self, scan_data, report_title=None):
        """Generate comprehensive HTML report"""
        try:
            # Prepare report data
            report_data = self.prepare_report_data(scan_data, report_title)
            
            # Load template
            template_path = self.templates_dir / "default_report.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            # Generate HTML
            html_content = template.render(**report_data)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"xshield_report_{timestamp}.html"
            report_path = self.reports_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate JSON summary
            self.generate_json_summary(report_data, report_path.with_suffix('.json'))
            
            self.report_generated.emit(str(report_path))
            return report_path
            
        except Exception as e:
            raise Exception(f"Report generation failed: {str(e)}")
    
    def prepare_report_data(self, scan_data, report_title=None):
        """Prepare data for report template"""
        if not report_title:
            report_title = f"Pentesting Report - {scan_data.get('primary_target', 'Unknown Target')}"
        
        # Calculate metrics
        vulnerabilities = scan_data.get('vulnerabilities', [])
        modules = scan_data.get('modules', [])
        
        # Risk score calculation (simplified CVSS-like)
        risk_score = self.calculate_risk_score(vulnerabilities)
        
        # Prepare chart data
        risk_chart_data = self.create_risk_chart_data(vulnerabilities)
        timeline_chart_data = self.create_timeline_chart_data(modules)
        
        # Calculate scan duration
        total_duration = sum(m.get('duration', 0) for m in modules)
        
        return {
            'report_title': report_title,
            'generation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'risk_score': risk_score,
            'total_vulnerabilities': len(vulnerabilities),
            'modules_run': len(modules),
            'scan_duration': round(total_duration / 60, 1),
            'primary_target': scan_data.get('primary_target', 'N/A'),
            'target_description': scan_data.get('target_description', 'No description available'),
            'scan_scope': scan_data.get('scan_scope', ['Network Scan', 'Web Application Scan', 'Security Assessment']),
            'modules': self.format_module_data(modules),
            'vulnerabilities': self.format_vulnerability_data(vulnerabilities),
            'risk_chart_data': json.dumps(risk_chart_data),
            'timeline_chart_data': json.dumps(timeline_chart_data)
        }
    
    def calculate_risk_score(self, vulnerabilities):
        """Calculate overall risk score (0-100)"""
        if not vulnerabilities:
            return 0
        
        severity_weights = {
            'critical': 10,
            'high': 7,
            'medium': 4,
            'low': 2,
            'info': 1
        }
        
        total_score = sum(severity_weights.get(v.get('severity', 'low'), 1) for v in vulnerabilities)
        max_possible_score = len(vulnerabilities) * 10
        
        return min(100, round((total_score / max_possible_score) * 100))
    
    def create_risk_chart_data(self, vulnerabilities):
        """Create data for risk distribution chart"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return [{
            'x': list(severity_counts.keys()),
            'y': list(severity_counts.values()),
            'type': 'bar',
            'marker': {
                'color': ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#3b82f6']
            }
        }]
    
    def create_timeline_chart_data(self, modules):
        """Create data for timeline chart"""
        if not modules:
            return []
        
        module_names = []
        durations = []
        
        for module in modules:
            module_names.append(module.get('name', 'Unknown'))
            durations.append(module.get('duration', 0))
        
        return [{
            'x': durations,
            'y': module_names,
            'type': 'bar',
            'orientation': 'h',
            'marker': {'color': '#8b5cf6'}
        }]
    
    def format_module_data(self, modules):
        """Format module data for template"""
        formatted_modules = []
        
        for module in modules:
            formatted_modules.append({
                'name': module.get('name', 'Unknown Module'),
                'status': module.get('status', 'unknown'),
                'duration': round(module.get('duration', 0), 2),
                'items_scanned': module.get('items_scanned', 0),
                'issues_found': module.get('issues_found', 0),
                'summary': module.get('summary', '')
            })
        
        return formatted_modules
    
    def format_vulnerability_data(self, vulnerabilities):
        """Format vulnerability data for template"""
        formatted_vulns = []
        
        for vuln in vulnerabilities:
            formatted_vulns.append({
                'title': vuln.get('title', 'Unknown Vulnerability'),
                'severity': vuln.get('severity', 'low'),
                'target': vuln.get('target', 'Unknown Target'),
                'description': vuln.get('description', 'No description available'),
                'technical_details': vuln.get('technical_details', ''),
                'recommendation': vuln.get('recommendation', 'No recommendation available')
            })
        
        return formatted_vulns
    
    def generate_json_summary(self, report_data, json_path):
        """Generate JSON summary of the report"""
        try:
            summary = {
                'metadata': {
                    'report_title': report_data['report_title'],
                    'generation_date': report_data['generation_date'],
                    'risk_score': report_data['risk_score']
                },
                'summary': {
                    'total_vulnerabilities': report_data['total_vulnerabilities'],
                    'modules_run': report_data['modules_run'],
                    'scan_duration_minutes': report_data['scan_duration']
                },
                'target': {
                    'primary_target': report_data['primary_target'],
                    'description': report_data['target_description']
                },
                'vulnerabilities': report_data['vulnerabilities'],
                'modules': report_data['modules']
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Failed to generate JSON summary: {str(e)}")
    
    def get_report_list(self):
        """Get list of generated reports"""
        reports = []
        
        for report_file in self.reports_dir.glob("*.html"):
            stat = report_file.stat()
            reports.append({
                'name': report_file.name,
                'path': str(report_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return sorted(reports, key=lambda x: x['created'], reverse=True)
