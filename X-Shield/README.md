# X-Shield Pentesting Framework

A professional, modular pentesting framework built with Python 3.10+ and PySide6, featuring a modern dark-themed GUI and comprehensive security assessment capabilities.

## Features

### Core Capabilities
- **Modular Architecture**: Strictly separated modules for different pentesting tasks
- **Modern GUI**: PySide6-based interface with dark mode support
- **Asynchronous Execution**: Non-blocking GUI with multi-threaded module execution
- **Real-time Logging**: Centralized logging system with terminal-like display
- **Professional Reporting**: HTML reports with Tailwind CSS and interactive charts

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

#### Brute Force
- Multi-threaded password cracking
- Support for various wordlist formats
- Web form authentication testing
- File-based brute force attacks

#### Exploitation
- Payload execution framework
- Exploit template system
- Post-exploitation tools
- Custom payload support

#### OSINT (Open Source Intelligence)
- Shodan integration
- WHOIS lookups
- Metadata extraction
- Social media reconnaissance

#### MITM & Sniffing
- ARP spoofing capabilities
- Packet capture and analysis
- Network traffic monitoring
- Protocol analysis

#### DoS/DDoS Testing
- Stress testing tools (authorized only)
- Traffic generation
- Load testing capabilities
- Performance assessment

#### Threat Intelligence
- OWASP Top 10 integration
- CVE database access
- Live threat feeds
- Security advisory aggregation

## Installation

### Prerequisites
- Python 3.10 or higher
- Administrative privileges (for network operations)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd X-Shield

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies
- **PySide6**: Modern GUI framework
- **Scapy**: Packet manipulation and network scanning
- **Requests**: HTTP library for web scanning
- **BeautifulSoup4**: HTML parsing
- **Plotly**: Interactive charts for reports
- **Jinja2**: Template engine for reports
- **Additional libraries**: See requirements.txt

## Usage

### Quick Start
1. Launch X-Shield using `python main.py`
2. Select a pentesting module from the left panel
3. Configure target and parameters in the Module Config tab
4. Click "Run Selected Module" to start the scan
5. Monitor real-time progress in the terminal
6. View results in the Results tab
7. Generate professional HTML reports

### Module Configuration
Each module has specific parameters:
- **Target**: IP address, domain, or URL to scan
- **Scan Type**: Choose from available scan methods
- **Timeouts**: Configure request timeouts
- **Threads**: Adjust concurrent operations
- **Custom Parameters**: Module-specific settings

### Reporting
- Automatic HTML report generation
- Interactive charts and visualizations
- CVSS-like risk scoring
- Vulnerability categorization
- Executive summary and technical details
- Export to multiple formats

## Architecture

### Project Structure
```
X-Shield/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── core/                   # Core framework components
│   ├── logger.py          # Centralized logging system
│   ├── module_manager.py  # Module execution manager
│   └── base_module.py     # Base class for all modules
├── modules/               # Pentesting modules
│   ├── network_scanner/   # Network discovery and scanning
│   ├── web_scanner/       # Web application testing
│   ├── brute_force/       # Password cracking tools
│   ├── exploitation/      # Exploitation framework
│   ├── osint/            # Open source intelligence
│   ├── mitm_sniffing/    # MITM and packet analysis
│   ├── dos/              # Stress testing tools
│   └── threat_intel/     # Threat intelligence
├── ui/                    # User interface components
│   ├── main_window.py    # Main application window
│   ├── terminal_widget.py # Real-time log display
│   ├── module_widget.py  # Module configuration interface
│   └── dashboard_widget.py # Overview and statistics
├── reports/               # Report generation
│   ├── report_generator.py # HTML report engine
│   └── templates/         # Report templates
├── utils/                 # Utility functions
├── config/               # Configuration files
└── data/                # Data storage
    ├── wordlists/       # Password wordlists
    └── reports/         # Generated reports
```

### Module Development
Create new modules by inheriting from `BaseModule`:

```python
from core.base_module import BaseModule

class CustomModule(BaseModule):
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
    
    def run(self, target, parameters):
        # Module implementation
        pass
    
    def validate_target(self, target):
        # Target validation
        return True
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**X-Shield is designed for authorized security testing only.** Users are responsible for ensuring compliance with all applicable laws and regulations. The authors are not responsible for misuse of this software.

---

**Warning**: Pentesting tools can cause network disruption and may be illegal if used without proper authorization. Always obtain written permission before conducting security assessments.
