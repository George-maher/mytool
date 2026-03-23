"""
Modern Dashboard UI for X-Shield Framework
Professional Material Design with qt-material integration
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QLabel, QPushButton, QScrollArea, QSplitter, QToolBar,
    QMenuBar, QStatusBar, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap
from ui.styles import Colors, Spacing, Typography, get_main_stylesheet

# Import dashboard components
from .sidebar import Sidebar
from .target_manager import TargetManager
from .scanner_page import ScannerPage
from .reports_page import ReportsPage
from .settings_page import SettingsPage
from .output_console import OutputConsole
from .dashboard_overview import DashboardOverview

# Import core components
from core.target_store import TargetStore


class DashboardUI(QMainWindow):
    """Modern Dashboard UI with Material Design"""
    
    # Signals
    target_added = Signal(str, str, str)  # name, type, value
    target_selected = Signal(str)  # target value
    scanner_started = Signal(str, str)  # scanner, target
    report_generated = Signal(str)  # report path
    
    def __init__(self, main_core, module_manager, report_generator, logger):
        super().__init__()
        
        # Core components
        self.main_core = main_core
        self.module_manager = module_manager
        self.report_generator = report_generator
        self.logger = logger
        
        # Target store for global target management
        self.target_store = TargetStore()
        
        # Initialize UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Apply qt-material theme
        self.apply_material_theme()
        
        # Setup timers
        self.setup_timers()
        
        self.logger.info("Dashboard UI initialized with Material Design")
    
    def setup_ui(self):
        """Setup main dashboard UI"""
        self.setWindowTitle("X-Shield - Professional Pentesting Framework")
        self.setGeometry(100, 100, 1000, 1000)
        self.setMinimumSize(1000, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create sidebar (fixed width)
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setMaximumWidth(280)
        self.main_splitter.addWidget(self.sidebar)
        
        # Create main content area
        self.main_content = self.create_main_content()
        self.main_splitter.addWidget(self.main_content)
        
        # Set splitter sizes (280px sidebar, rest for content)
        self.main_splitter.setSizes([280, 1320])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
    
    def create_main_content(self):
        """Create main content area with stacked widget"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for page switching
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.dashboard_overview = DashboardOverview(self.target_store)
        self.target_manager = TargetManager(self.target_store)
        self.scanner_page = ScannerPage(self.module_manager, self.target_store)
        self.reports_page = ReportsPage(self.report_generator)
        self.settings_page = SettingsPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_overview)  # Index 0
        self.stacked_widget.addWidget(self.target_manager)      # Index 1
        self.stacked_widget.addWidget(self.scanner_page)        # Index 2
        self.stacked_widget.addWidget(self.reports_page)        # Index 3
        self.stacked_widget.addWidget(self.settings_page)       # Index 4
        
        content_layout.addWidget(self.stacked_widget)
        
        # Create output console at bottom
        self.output_console = OutputConsole()
        self.output_console.setMaximumHeight(200)
        self.output_console.setMinimumHeight(150)
        content_layout.addWidget(self.output_console)
        
        return content_widget
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_project_action = QAction("New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        save_project_action = QAction("Save Project", self)
        save_project_action.setShortcut("Ctrl+S")
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        generate_report_action = QAction("Generate Report", self)
        generate_report_action.setShortcut("Ctrl+R")
        generate_report_action.triggered.connect(self.generate_report)
        tools_menu.addAction(generate_report_action)
        
        tools_menu.addSeparator()
        
        clear_console_action = QAction("Clear Console", self)
        clear_console_action.setShortcut("Ctrl+L")
        clear_console_action.triggered.connect(self.output_console.clear)
        tools_menu.addAction(clear_console_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        toggle_console_action = QAction("Toggle Console", self)
        toggle_console_action.setShortcut("Ctrl+`")
        toggle_console_action.setCheckable(True)
        toggle_console_action.setChecked(True)
        toggle_console_action.triggered.connect(self.toggle_console)
        view_menu.addAction(toggle_console_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About X-Shield", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Target count
        self.target_count_label = QLabel("Targets: 0")
        self.status_bar.addPermanentWidget(self.target_count_label)
        
        # Scanner status
        self.scanner_status_label = QLabel("No scanner running")
        self.status_bar.addPermanentWidget(self.scanner_status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Sidebar navigation
        self.sidebar.page_changed.connect(self.switch_page)
        
        # Target manager
        self.target_manager.target_added.connect(self.on_target_added)
        self.target_manager.target_removed.connect(self.on_target_removed)
        self.target_manager.scan_requested.connect(self.on_scan_requested)
        
        # Scanner page
        self.scanner_page.scanner_started.connect(self.on_scanner_started)
        self.scanner_page.scanner_finished.connect(self.on_scanner_finished)
        self.scanner_page.scanner_error.connect(self.on_scanner_error)
        
        # Reports page
        self.reports_page.report_generated.connect(self.on_report_generated)
        
        # Settings page
        self.settings_page.settings_changed.connect(self.on_settings_changed)
        
        # Target store
        self.target_store.targets_updated.connect(self.on_targets_updated)
    
    def apply_material_theme(self):
        """Apply modern minimal design system"""
        try:
            self.setStyleSheet(get_main_stylesheet())
        except Exception as e:
            self.logger.warning(f"Failed to apply theme: {e}")
            self.setStyleSheet(f"QMainWindow {{ background-color: {Colors.BACKGROUND}; color: white; }}")
    
    def setup_timers(self):
        """Setup update timers"""
        # Update dashboard stats every 5 seconds
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.update_dashboard_stats)
        self.dashboard_timer.start(5000)
        
        # Update target count
        self.update_target_count()
    
    @Slot(int)
    def switch_page(self, page_index):
        """Switch between pages"""
        self.stacked_widget.setCurrentIndex(page_index)
        
        # Update status bar with current page
        page_names = ["Dashboard", "Target Manager", "Scanners", "Reports", "Settings"]
        self.status_label.setText(f"Current: {page_names[page_index]}")
        
        # Refresh page-specific data
        if page_index == 0:  # Dashboard
            self.dashboard_overview.refresh_stats()
        elif page_index == 1:  # Target Manager
            self.target_manager.refresh_targets()
        elif page_index == 3:  # Reports
            self.reports_page.refresh_reports()
    
    @Slot(str, str, str)
    def on_target_added(self, name, target_type, value):
        """Handle target addition"""
        self.target_store.add_target(name, target_type, value)
        self.output_console.log_info(f"Target added: {name} ({target_type})")
        self.update_target_count()
    
    @Slot(str)
    def on_target_removed(self, target_value):
        """Handle target removal"""
        self.target_store.remove_target(target_value)
        self.output_console.log_info(f"Target removed: {target_value}")
        self.update_target_count()
    
    @Slot(str, str)
    def on_scan_requested(self, scanner_type, target_value):
        """Handle scan request"""
        self.switch_page(2)  # Switch to scanners page
        self.scanner_page.start_scanner(scanner_type, target_value)
    
    @Slot(str, str)
    def on_scanner_started(self, scanner_type, target_value):
        """Handle scanner start"""
        self.scanner_status_label.setText(f"Running: {scanner_type}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.output_console.log_info(f"Started {scanner_type} scan on {target_value}")
    
    @Slot(str, dict)
    def on_scanner_finished(self, scanner_type, results):
        """Handle scanner completion"""
        self.scanner_status_label.setText("No scanner running")
        self.progress_bar.setVisible(False)
        self.output_console.log_success(f"Completed {scanner_type} scan")
        
        # Update dashboard with results
        self.dashboard_overview.add_scan_result(scanner_type, results)
    
    @Slot(str, str)
    def on_scanner_error(self, scanner_type, error_message):
        """Handle scanner error"""
        self.scanner_status_label.setText("Scanner error")
        self.progress_bar.setVisible(False)
        self.output_console.log_error(f"Scanner error: {error_message}")
    
    @Slot(str)
    def on_report_generated(self, report_path):
        """Handle report generation"""
        self.output_console.log_success(f"Report generated: {report_path}")
        self.report_generated.emit(report_path)
    
    @Slot(dict)
    def on_settings_changed(self, settings):
        """Handle settings changes"""
        self.output_console.log_info("Settings updated")
        # Apply theme changes if needed
        if 'theme' in settings:
            self.apply_material_theme()
    
    @Slot()
    def on_targets_updated(self):
        """Handle targets list update"""
        self.update_target_count()
        self.dashboard_overview.refresh_stats()
    
    def update_target_count(self):
        """Update target count in status bar"""
        count = len(self.target_store.get_all_targets())
        self.target_count_label.setText(f"Targets: {count}")
    
    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        if self.stacked_widget.currentIndex() == 0:  # Dashboard is visible
            self.dashboard_overview.refresh_stats()
    
    def toggle_console(self, visible):
        """Toggle output console visibility"""
        self.output_console.setVisible(visible)
    
    def new_project(self):
        """Create new project"""
        self.target_store.clear_all_targets()
        self.output_console.log_info("New project created")
        self.switch_page(0)
    
    def open_project(self):
        """Open existing project"""
        self.output_console.log_info("Open project - feature coming soon")
    
    def save_project(self):
        """Save current project"""
        self.output_console.log_info("Save project - feature coming soon")
    
    def generate_report(self):
        """Generate report from current results"""
        self.switch_page(3)  # Switch to reports page
        self.reports_page.generate_report()
    
    def show_documentation(self):
        """Show documentation"""
        self.output_console.log_info("Documentation - feature coming soon")
    
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        about_text = """
        <h2>X-Shield Pentesting Framework</h2>
        <p>Version: 2.0.0</p>
        <p>Professional modular pentesting framework with Material Design</p>
        <p><b>Features:</b></p>
        <ul>
            <li>🎯 Target Management</li>
            <li>🔍 Network Scanning</li>
            <li>🌐 Web Application Testing</li>
            <li>💻 Brute Force Attacks</li>
            <li>🔍 OSINT Gathering</li>
            <li>🚨 MITM & Sniffing</li>
            <li>⚡ DoS Testing</li>
            <li>🛡️ Threat Intelligence</li>
            <li>📊 Professional Reporting</li>
        </ul>
        <p><strong>Warning:</strong> For authorized security testing only!</p>
        """
        
        QMessageBox.about(self, "About X-Shield", about_text)
    
    def closeEvent(self, event):
        """Handle application close"""
        # Stop any running scanners
        self.scanner_page.stop_all_scanners()
        
        # Save settings
        self.settings_page.save_settings()
        
        self.logger.info("Dashboard UI closing")
        event.accept()
