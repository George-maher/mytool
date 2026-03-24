# X-Shield Pentesting Framework

A professional, modular pentesting framework built with Python 3.10+ and PySide6, featuring a modern dark-themed GUI and comprehensive security assessment capabilities.

## Features

### Core Capabilities
- **Modular Architecture**: Strictly separated modules for different pentesting tasks
- **Modern GUI**: PySide6-based interface with modern minimal design
- **Asynchronous Execution**: Non-blocking GUI with multi-threaded module execution
- **Real-time Logging**: Centralized logging system with terminal-like display
- **Professional Reporting**: HTML reports with modern styling and interactive charts

### Pentesting Modules

#### Network Scanner
- ARP discovery for host identification
- TCP port scanning with service detection
- Comprehensive network mapping
- MAC address vendor identification

#### Web Scanner
- XSS vulnerability detection
- SQL injection testing
- CSRF vulnerability assessment
- Security header analysis
- Directory discovery

#### OSINT (Open Source Intelligence)
- Shodan integration
- WHOIS lookups
- Subdomain enumeration
- Metadata extraction
- Email harvesting

#### Brute Force
- Multi-threaded password cracking
- Support for various wordlist formats
- Web form authentication testing

#### Attack Stress Testing
- Load testing capabilities
- Performance assessment
- Traffic generation

#### Threat Intelligence
- CVE database access
- Live threat feeds
- Security advisory aggregation

## Installation

### Prerequisites
- Python 3.10 or higher
- Administrative privileges (for network operations)

### Setup
```bash
# Clone repository
git clone <repository-url>
cd X-Shield

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Dependencies
- **PySide6**: Modern GUI framework
- **Scapy**: Packet manipulation and network scanning
- **Requests**: HTTP library for web scanning
- **BeautifulSoup4**: HTML parsing
- **python-nmap**: Network scanning capabilities
- **Additional libraries**: See requirements.txt

## Usage

### Quick Start
1. Launch X-Shield using `python main.py`
2. Navigate through modules using the sidebar
3. Configure target and parameters in each module
4. Click "Start" to begin scanning
5. Monitor real-time progress in terminal
6. View results in the terminal output
7. Generate reports from the Reports page

### Module Configuration
Each module has specific parameters:
- **Target**: IP address, domain, or URL to scan
- **Scan Type**: Choose from available scan methods
- **Timeouts**: Configure request timeouts
- **Threads**: Adjust concurrent operations
- **Custom Parameters**: Module-specific settings

### Available Modules
- **Dashboard**: Overview of system status and recent activity
- **Target Manager**: Centralized target management and enrollment
- **Network Scanner**: ARP, TCP, and comprehensive network scanning
- **Web Scanner**: Web application vulnerability assessment
- **OSINT**: Open source intelligence gathering
- **Reports**: Professional report generation and management
- **Settings**: Application configuration and preferences

## Architecture

### Project Structure
```
X-Shield/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── core/                   # Core framework components
│   ├── target_manager.py  # Target management system
│   ├── module_manager.py  # Module execution manager
│   ├── logger_new.py      # Centralized logging system
│   └── base_module.py     # Base class for all modules
├── modules/               # Pentesting modules
│   ├── network_scanner/   # Network discovery and scanning
│   ├── web_scanner/       # Web application testing
│   ├── osint/            # Open source intelligence
│   ├── brute_force/       # Password cracking tools
│   ├── attack_stress/    # Stress testing tools
│   └── threat_intel/     # Threat intelligence
├── ui/                    # User interface components
│   ├── app_main.py       # Main application window
│   ├── components/       # UI components
│   │   ├── sidebar.py
│   │   ├── stacked_content.py
│   │   └── styles.py
│   └── pages/           # Page implementations
│       ├── dashboard_page.py
│       ├── target_manager_page.py
│       ├── network_scanner_page.py
│       ├── web_scanner_page.py
│       ├── osint_page.py
│       ├── reports_page_new.py
│       └── settings_page_new.py
├── models/               # Data models
├── views/               # View components
├── reports/               # Report generation
│   └── advanced_report_generator.py
├── config/               # Configuration files
├── data/                 # Data storage
└── logs/                 # Application logs
```

### Module Development
Create new modules by inheriting from `BaseModule` or `NetworkModule`:

```python
from core.base_module import NetworkModule

class CustomModule(NetworkModule):
    NAME = "Custom Module"
    DESCRIPTION = "Description of your module"
    VERSION = "1.0.0"
    AUTHOR = "Your Name"
    CATEGORY = "Custom"
    
    PARAMETERS = {
        'param1': {
            'type': 'string',
            'label': 'Parameter 1',
            'default': 'default_value',
            'description': 'Parameter description'
        }
    }
    
    def execute(self, target, parameters):
        # Module implementation
        self.add_finding("Custom finding", {"details": "Finding details"})
        return self.results
```

## Security Considerations

### Legal Usage
- **Authorized Testing Only**: Use only on systems you have permission to test
- **Compliance**: Ensure compliance with local laws and regulations
- **Documentation**: Maintain proper documentation of all tests

### Best Practices
- Use isolated testing environments
- Implement proper network segmentation
- Monitor for unintended consequences
- Maintain audit trails of all activities

## Contributing

### Development Guidelines
- Follow PEP 8 coding standards
- Implement proper error handling
- Add comprehensive logging
- Include module documentation
- Test thoroughly before submission

### Module Submission
1. Create module in appropriate directory
2. Inherit from `BaseModule` or specialized base class
3. Implement required methods
4. Add comprehensive documentation
5. Test with various targets
6. Submit pull request

## Support

### Documentation
- Module-specific documentation in each module directory
- API documentation in code comments
- Configuration examples in config directory

### Troubleshooting
- Check terminal output for error messages
- Verify target accessibility
- Ensure proper permissions
- Review module configuration

## Current Status

### Working Modules
- **Network Scanner**: ARP, TCP, and comprehensive scanning
- **Web Scanner**: XSS, SQLi, CSRF, and directory scanning
- **OSINT**: WHOIS, DNS, subdomain enumeration
- **Attack Stress**: Load testing capabilities
- **Brute Force**: Password cracking tools
- **Threat Intelligence**: CVE and threat data

### Known Issues
- Some OSINT APIs may require API keys for full functionality
- Network scanning requires administrative privileges for ARP operations
- Web scanner results may vary based on target security measures

## License

This project is licensed under MIT License - see LICENSE file for details.

## Disclaimer

**X-Shield is designed for authorized security testing only.** Users are responsible for ensuring compliance with all applicable laws and regulations. The authors are not responsible for misuse of this software.

---

**Warning**: Pentesting tools can cause network disruption and may be illegal if used without proper authorization. Always obtain written permission before conducting security assessments.
