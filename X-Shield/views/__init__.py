"""
Views Package for X-Shield Framework
UI layer implementing MVC pattern
"""

from .base_view import BaseView
from .dashboard_view import DashboardView
from .target_view import TargetView
from .scanner_view import ScannerView
from .report_view import ReportView
from .settings_view import SettingsView
from .console_view import ConsoleView

__all__ = [
    'BaseView', 'DashboardView', 'TargetView', 'ScannerView',
    'ReportView', 'SettingsView', 'ConsoleView'
]
