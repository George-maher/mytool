"""
Reporting Engine for X-Shield
Generates security reports from scan findings
"""

import json
import os
import datetime
from typing import List, Dict, Any
from .logger import Logger

class ReportingEngine:
    """Core reporting engine for X-Shield findings"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.logger = Logger("ReportingEngine")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_json_report(self, target_data: Dict[str, Any], filename: str = None) -> str:
        """Generate a detailed JSON report for a target"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            target_val = target_data.get('value', 'unknown').replace('.', '_')
            filename = f"report_{target_val}_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        report_content = {
            "report_metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "scanner_version": "2.0.0-PRO",
                "classification": "CONFIDENTIAL"
            },
            "target_info": {
                "id": target_data.get('id'),
                "address": target_data.get('value'),
                "type": target_data.get('type'),
                "status": target_data.get('status')
            },
            "findings": target_data.get('scan_results', {})
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(report_content, f, indent=4)
            self.logger.info(f"JSON report generated: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return ""

    def generate_summary_text(self, target_data: Dict[str, Any]) -> str:
        """Generate a human-readable summary of findings"""
        findings = target_data.get('scan_results', {})
        vulnerabilities = findings.get('vulnerabilities', [])
        ports = findings.get('ports', [])

        summary = [
            f"X-SHIELD SECURITY AUDIT SUMMARY",
            f"===============================",
            f"TARGET: {target_data.get('value')}",
            f"DATE:   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"STATUS: {target_data.get('status', 'COMPLETED')}",
            f"",
            f"PORT SCAN RESULTS:",
            f"------------------"
        ]

        if ports:
            for p in ports:
                summary.append(f"  [+] Port {p.get('port')}/{p.get('protocol')} - {p.get('service')} ({p.get('state')})")
        else:
            summary.append("  No open ports discovered.")

        summary.append(f"")
        summary.append(f"VULNERABILITY FINDINGS:")
        summary.append(f"-----------------------")

        if vulnerabilities:
            for v in vulnerabilities:
                severity = v.get('severity', 'INFO').upper()
                summary.append(f"  [{severity}] {v.get('name')}")
                if v.get('description'):
                    summary.append(f"      Desc: {v.get('description')}")
        else:
            summary.append("  No high-risk vulnerabilities detected.")

        summary.append(f"")
        summary.append(f"--- END OF REPORT ---")

        return "\n".join(summary)

    def export_report(self, target_data: Dict[str, Any], format: str = "json") -> str:
        """Export report in specified format"""
        if format.lower() == "json":
            return self.generate_json_report(target_data)
        elif format.lower() == "text":
            content = self.generate_summary_text(target_data)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            target_val = target_data.get('value', 'unknown').replace('.', '_')
            filename = f"report_{target_val}_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w') as f:
                f.write(content)
            return filepath

        return ""
