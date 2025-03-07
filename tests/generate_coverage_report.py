import subprocess
import sys
from pathlib import Path
from datetime import datetime
from utils.logger import log_action, log_error, log_debug

class CoverageReportGenerator:
    """Generates test coverage reports."""
    
    def __init__(self):
        self.coverage_dir = Path("coverage_html")
        self.coverage_dir.mkdir(exist_ok=True)
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_html_report(self):
        """Generate HTML coverage report."""
        try:
            log_action("Generating HTML coverage report", "Creating HTML report")
            
            # Run pytest with coverage
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_scenarios.py",
                "--cov=src",
                "--cov-report=html",
                "--cov-config=tests/.coveragerc"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                log_error(Exception("Coverage report generation failed"), result.stderr)
                return False
            
            log_action("HTML coverage report generated", f"Report available in {self.coverage_dir}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate HTML coverage report")
            return False
    
    def generate_xml_report(self):
        """Generate XML coverage report."""
        try:
            log_action("Generating XML coverage report", "Creating XML report")
            
            # Run pytest with coverage
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_scenarios.py",
                "--cov=src",
                "--cov-report=xml",
                "--cov-config=tests/.coveragerc"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                log_error(Exception("Coverage report generation failed"), result.stderr)
                return False
            
            log_action("XML coverage report generated", "Report available in coverage.xml")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate XML coverage report")
            return False
    
    def generate_terminal_report(self):
        """Generate terminal coverage report."""
        try:
            log_action("Generating terminal coverage report", "Creating terminal report")
            
            # Run pytest with coverage
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_scenarios.py",
                "--cov=src",
                "--cov-report=term",
                "--cov-config=tests/.coveragerc"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                log_error(Exception("Coverage report generation failed"), result.stderr)
                return False
            
            # Save terminal output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"coverage_terminal_{timestamp}.txt"
            
            with open(report_file, 'w') as f:
                f.write(result.stdout)
            
            log_action("Terminal coverage report generated", f"Report saved to {report_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate terminal coverage report")
            return False
    
    def analyze_coverage(self):
        """Analyze coverage results."""
        try:
            log_action("Analyzing coverage results", "Processing coverage data")
            
            # Read coverage.xml
            if not (Path("coverage.xml")).exists():
                log_error(Exception("Coverage XML file not found"), "coverage.xml not found")
                return False
            
            # TODO: Add coverage analysis logic here
            # This could include:
            # - Calculating overall coverage percentage
            # - Identifying uncovered lines
            # - Analyzing branch coverage
            # - Generating coverage trends
            
            log_action("Coverage analysis completed", "Analysis results processed")
            return True
            
        except Exception as e:
            log_error(e, "Failed to analyze coverage results")
            return False
    
    def generate_all_reports(self):
        """Generate all coverage reports."""
        try:
            log_action("Starting coverage report generation", "Generating all reports")
            
            # Generate all report types
            if not all([
                self.generate_html_report(),
                self.generate_xml_report(),
                self.generate_terminal_report(),
                self.analyze_coverage()
            ]):
                return False
            
            log_action("All coverage reports generated", "Reports available in respective directories")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate coverage reports")
            return False

def main():
    """Main generator entry point."""
    try:
        generator = CoverageReportGenerator()
        
        if not generator.generate_all_reports():
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Report generation interrupted", "User interrupted report generation")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Report generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 