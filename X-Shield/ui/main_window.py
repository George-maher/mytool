"""
Main GUI Window for X-Shield Framework
Professional dark-themed interface with modular design
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QTextEdit, QMenuBar, QStatusBar, QMessageBox,
    QProgressBar, QLabel, QToolBar, QDockWidget, QListWidget,
    QListWidgetItem, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QThread, Slot
from PySide6.QtGui import QIcon, QFont, QAction, QPalette, QColor
from .terminal_widget import TerminalWidget
from .module_widget import ModuleWidget
from .dashboard_widget import DashboardWidget
from core.worker import ModuleWorker, ThreadManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, main_core, module_manager, report_generator, logger):
        super().__init__()
        self.main_core = main_core
        self.module_manager = module_manager
        self.report_generator = report_generator
        self.logger = logger
        self.thread_manager = ThreadManager()
        
        # Window properties
        self.setWindowTitle("X-Shield Pentesting Framework")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize UI components
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_dock_widgets()
        
        # Connect signals
        self.setup_connections()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        self.logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for flexible layout
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Left panel - Module selection
        self.left_panel = self.create_left_panel()
        self.main_splitter.addWidget(self.left_panel)
        
        # Center panel - Main content area
        self.center_panel = self.create_center_panel()
        self.main_splitter.addWidget(self.center_panel)
        
        # Right panel - Terminal and logs
        self.right_panel = self.create_right_panel()
        self.main_splitter.addWidget(self.right_panel)
        
        # Set splitter sizes (30% - 50% - 20%)
        self.main_splitter.setSizes([420, 700, 280])
    
    def create_left_panel(self):
        """Create left panel with module selection"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Module list header
        header_label = QLabel("Pentesting Modules")
        header_label.setFont(QFont("Inter", 14, QFont.Bold))
        header_label.setStyleSheet("color: #8b5cf6; padding: 10px;")
        left_layout.addWidget(header_label)
        
        # Module list
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                margin: 2px 0;
                border-radius: 6px;
                background-color: #374151;
                color: #e5e7eb;
            }
            QListWidget::item:hover {
                background-color: #4b5563;
            }
            QListWidget::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
        """)
        
        # Populate modules
        self.populate_module_list()
        left_layout.addWidget(self.module_list)
        
        # Quick actions
        actions_frame = QFrame()
        actions_layout = QVBoxLayout(actions_frame)
        
        self.run_module_btn = QPushButton("Run Selected Module")
        self.run_module_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:disabled {
                background-color: #4b5563;
                color: #9ca3af;
            }
        """)
        self.run_module_btn.setEnabled(False)
        actions_layout.addWidget(self.run_module_btn)
        
        self.stop_module_btn = QPushButton("Stop Module")
        self.stop_module_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #4b5563;
                color: #9ca3af;
            }
        """)
        self.stop_module_btn.setEnabled(False)
        actions_layout.addWidget(self.stop_module_btn)
        
        left_layout.addWidget(actions_frame)
        
        return left_widget
    
    def create_center_panel(self):
        """Create center panel with tabbed interface"""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #374151;
                background-color: #1f2937;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #374151;
                color: #e5e7eb;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #8b5cf6;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #4b5563;
            }
        """)
        
        # Dashboard tab
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        
        # Module configuration tab
        self.module_widget = ModuleWidget()
        self.tab_widget.addTab(self.module_widget, "Module Config")
        
        # Results tab
        self.results_widget = QTextEdit()
        self.results_widget.setReadOnly(True)
        self.results_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.tab_widget.addTab(self.results_widget, "Results")
        
        center_layout.addWidget(self.tab_widget)
        
        return center_widget
    
    def create_right_panel(self):
        """Create right panel with terminal and logs"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Terminal header
        terminal_header = QLabel("Terminal & Logs")
        terminal_header.setFont(QFont("Inter", 12, QFont.Bold))
        terminal_header.setStyleSheet("color: #8b5cf6; padding: 5px;")
        right_layout.addWidget(terminal_header)
        
        # Terminal widget
        self.terminal_widget = TerminalWidget()
        right_layout.addWidget(self.terminal_widget)
        
        return right_widget
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_scan_action = QAction("New Scan", self)
        new_scan_action.setShortcut("Ctrl+N")
        new_scan_action.triggered.connect(self.new_scan)
        file_menu.addAction(new_scan_action)
        
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
        
        clear_results_action = QAction("Clear Results", self)
        clear_results_action.triggered.connect(self.clear_results)
        tools_menu.addAction(clear_results_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
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
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Module status
        self.module_status_label = QLabel("No module running")
        self.status_bar.addPermanentWidget(self.module_status_label)
    
    def setup_dock_widgets(self):
        """Setup dock widgets"""
        # Target information dock
        target_dock = QDockWidget("Target Information", self)
        target_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        target_widget = QWidget()
        target_layout = QVBoxLayout(target_widget)
        
        self.target_info = QTextEdit()
        self.target_info.setMaximumHeight(150)
        self.target_info.setReadOnly(True)
        self.target_info.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.target_info.setText("No target configured")
        
        target_layout.addWidget(self.target_info)
        target_dock.setWidget(target_widget)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, target_dock)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Module list selection
        self.module_list.itemSelectionChanged.connect(self.on_module_selected)
        
        # Module buttons
        self.run_module_btn.clicked.connect(self.run_selected_module)
        self.stop_module_btn.clicked.connect(self.stop_current_module)
    
    def apply_dark_theme(self):
        """Apply dark theme to the window"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #111827;
                color: #e5e7eb;
            }
            QWidget {
                background-color: #111827;
                color: #e5e7eb;
            }
        """)
    
    def populate_module_list(self):
        """Populate module list with available modules"""
        modules = self.module_manager.get_available_modules()
        
        for module_name in modules:
            module_info = self.module_manager.get_module_info(module_name)
            if module_info:
                item = QListWidgetItem(f"{module_name}\n{module_info['description']}")
                item.setData(Qt.UserRole, module_name)
                self.module_list.addItem(item)
    
    @Slot()
    def on_module_selected(self):
        """Handle module selection"""
        selected_items = self.module_list.selectedItems()
        if selected_items:
            module_name = selected_items[0].data(Qt.UserRole)
            module_info = self.module_manager.get_module_info(module_name)
            
            if module_info:
                self.module_widget.display_module_config(module_name, module_info)
                self.run_module_btn.setEnabled(True)
    
    @Slot()
    def run_selected_module(self):
        """Run the selected module using worker pattern"""
        selected_items = self.module_list.selectedItems()
        if not selected_items:
            return
        
        module_name = selected_items[0].data(Qt.UserRole)
        target = self.module_widget.get_target()
        parameters = self.module_widget.get_parameters()
        
        # Validate target
        module_class = self.module_manager.loaded_modules.get(module_name)
        if not module_class:
            QMessageBox.critical(self, "Error", f"Module {module_name} not found")
            return
        
        # Create module instance
        module_instance = module_class(self.logger)
        
        if not module_instance.validate_target(target):
            QMessageBox.warning(self, "Invalid Target", f"Target '{target}' is not valid for {module_name}")
            return
        
        # Create worker
        worker = ModuleWorker(module_instance, target, parameters)
        
        # Connect worker signals to slots
        worker.finished.connect(self.on_module_finished)
        worker.error.connect(self.on_module_error)
        worker.progress.connect(self.on_progress_updated)
        worker.status.connect(self.on_status_updated)
        
        # Start worker
        worker_id = f"{module_name}_{target}"
        if self.thread_manager.start_worker(worker_id, worker):
            self.run_module_btn.setEnabled(False)
            self.stop_module_btn.setEnabled(True)
            self.status_label.setText(f"Running {module_name} on {target}")
            self.module_status_label.setText(f"Running: {module_name}")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Update target info
            self.target_info.setText(f"Target: {target}\nModule: {module_name}\nStatus: Running")
        else:
            QMessageBox.warning(self, "Error", "Failed to start module - another module is running")
    
    @Slot()
    def stop_current_module(self):
        """Stop the currently running module"""
        self.thread_manager.stop_all_workers()
        self.status_label.setText("Stopping module...")
    
    @Slot(dict)
    def on_module_finished(self, results):
        """Handle module completion"""
        self.status_label.setText(f"Completed {results.get('module_name', 'Unknown')}")
        self.module_status_label.setText("No module running")
        self.progress_bar.setVisible(False)
        self.run_module_btn.setEnabled(True)
        self.stop_module_btn.setEnabled(False)
        
        # Display results
        self.display_results(results)
        
        # Update target info
        self.target_info.setText(f"Target: {results.get('target', 'N/A')}\nModule: {results.get('module_name', 'N/A')}\nStatus: Completed")
    
    @Slot(str)
    def on_module_error(self, error):
        """Handle module error"""
        self.status_label.setText("Module error")
        self.module_status_label.setText("No module running")
        self.progress_bar.setVisible(False)
        self.run_module_btn.setEnabled(True)
        self.stop_module_btn.setEnabled(False)
        
        QMessageBox.critical(self, "Module Error", f"Module failed:\n{error}")
    
    @Slot(int, int)
    def on_progress_updated(self, current, total):
        """Handle progress updates"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
            self.status_label.setText(f"Progress: {current}/{total} ({percentage}%)")
    
    @Slot(str)
    def on_status_updated(self, status):
        """Handle status updates"""
        self.status_label.setText(status)
    
    def display_results(self, results):
        """Display module results"""
        self.results_widget.clear()
        
        # Format results for display
        result_text = f"=== {results.get('module_name', 'UNKNOWN').upper()} RESULTS ===\n\n"
        result_text += f"Target: {results.get('target', 'N/A')}\n"
        result_text += f"Execution Time: {results.get('execution_time', 0):.2f}s\n\n"
        
        if 'findings' in results and results['findings']:
            result_text += "FINDINGS:\n"
            for finding in results['findings']:
                result_text += f"- {finding['type']}: {finding['details']}\n"
        
        if 'vulnerabilities' in results and results['vulnerabilities']:
            result_text += f"\nVULNERABILITIES FOUND: {len(results['vulnerabilities'])}\n"
            for vuln in results['vulnerabilities']:
                result_text += f"  - {vuln.get('title', 'Unknown')}: {vuln.get('severity', 'Unknown')}\n"
        
        result_text += f"\nSUMMARY: {results.get('summary', 'No summary available')}"
        
        self.results_widget.setText(result_text)
        self.tab_widget.setCurrentIndex(2)  # Switch to results tab
    
    def new_scan(self):
        """Start a new scan"""
        self.clear_results()
        self.logger.info("New scan initiated")
    
    def clear_results(self):
        """Clear all results"""
        self.results_widget.clear()
        self.module_manager.clear_results()
        self.dashboard_widget.reset()
        self.logger.info("Results cleared")
    
    def generate_report(self):
        """Generate report from current results"""
        try:
            # Collect data from all modules
            scan_data = {
                'primary_target': self.module_widget.get_target() or "Unknown Target",
                'target_description': "Security assessment performed with X-Shield framework",
                'modules': [],
                'vulnerabilities': []
            }
            
            # Get module results
            module_results = self.module_manager.get_module_results()
            for module_name, results in module_results.items():
                scan_data['modules'].append({
                    'name': module_name,
                    'status': 'completed',
                    'duration': results.get('execution_time', 0),
                    'items_scanned': results.get('items_scanned', 0),
                    'issues_found': len(results.get('vulnerabilities', [])),
                    'summary': results.get('summary', '')
                })
                
                # Add vulnerabilities
                for vuln in results.get('vulnerabilities', []):
                    vuln['target'] = results.get('target', 'Unknown')
                    scan_data['vulnerabilities'].append(vuln)
            
            # Generate report
            report_path = self.report_generator.generate_report(scan_data)
            QMessageBox.information(self, "Report Generated", f"Report saved to:\n{report_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Report Error", f"Failed to generate report:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>X-Shield Pentesting Framework</h2>
        <p>Version: 1.0.0</p>
        <p>Professional modular pentesting framework with:</p>
        <ul>
            <li>Network Scanning</li>
            <li>Web Application Testing</li>
            <li>Brute Force Attacks</li>
            <li>Exploitation Tools</li>
            <li>OSINT Gathering</li>
            <li>MITM & Sniffing</li>
            <li>DoS Testing</li>
            <li>Threat Intelligence</li>
        </ul>
        <p><strong>Warning:</strong> For authorized security testing only!</p>
        """
        
        QMessageBox.about(self, "About X-Shield", about_text)
    
    def show_chain_suggestions(self, module_name, suggestions):
        """Show module chaining suggestions"""
        suggestion_text = f"Module {module_name} suggests running:\n\n"
        for suggestion in suggestions:
            suggestion_text += f"• {suggestion}\n"
        
        reply = QMessageBox.question(
            self, "Module Chaining", suggestion_text,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Auto-run suggested modules
            for suggestion in suggestions:
                self.logger.info(f"Auto-running suggested module: {suggestion}")
    
    def show_error_message(self, error_message):
        """Show error message to user"""
        QMessageBox.critical(self, "Error", error_message)
    
    def show_report_generated(self, report_path):
        """Show report generation success"""
        QMessageBox.information(
            self, "Report Generated", 
            f"Report successfully generated:\n{report_path}"
        )
