import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from utils.logger import log_action, log_error, log_debug

class TestResultAnalyzer:
    """Analyzes test results and generates reports."""
    
    def __init__(self):
        self.results_dir = Path("test_results")
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.test_durations = defaultdict(float)
        self.error_types = defaultdict(int)
        
    def analyze_log_file(self, log_file):
        """Analyze a single test log file."""
        try:
            log_action("Analyzing log file", f"Processing {log_file}")
            
            with open(log_file, 'r') as f:
                for line in f:
                    if "test_" in line:
                        self.total_tests += 1
                        if "PASSED" in line:
                            self.passed_tests += 1
                        elif "FAILED" in line:
                            self.failed_tests += 1
                        elif "SKIPPED" in line:
                            self.skipped_tests += 1
                    
                    if "duration" in line:
                        try:
                            duration = float(line.split("duration=")[1].split()[0])
                            test_name = line.split("test_")[1].split()[0]
                            self.test_durations[test_name] = duration
                        except (ValueError, IndexError):
                            continue
                    
                    if "ERROR" in line:
                        error_type = line.split("ERROR")[1].split()[0]
                        self.error_types[error_type] += 1
            
            return True
            
        except Exception as e:
            log_error(e, f"Failed to analyze log file: {log_file}")
            return False
    
    def generate_report(self):
        """Generate a test results report."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"test_report_{timestamp}.json"
            
            report = {
                "timestamp": timestamp,
                "summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "skipped_tests": self.skipped_tests,
                    "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
                },
                "performance": {
                    "average_duration": sum(self.test_durations.values()) / len(self.test_durations) if self.test_durations else 0,
                    "slowest_tests": sorted(self.test_durations.items(), key=lambda x: x[1], reverse=True)[:5]
                },
                "errors": dict(self.error_types)
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=4)
            
            log_action("Generated test report", f"Report saved to {report_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate test report")
            return False
    
    def analyze_all_results(self):
        """Analyze all test results."""
        try:
            log_action("Starting results analysis", "Processing all test logs")
            
            # Find all log files
            log_files = list(self.results_dir.glob("test_run_*.log"))
            
            if not log_files:
                log_error(Exception("No log files found"), "No test results to analyze")
                return False
            
            # Analyze each log file
            for log_file in log_files:
                if not self.analyze_log_file(log_file):
                    return False
            
            # Generate report
            if not self.generate_report():
                return False
            
            # Print summary
            print("\nTest Results Summary:")
            print(f"Total Tests: {self.total_tests}")
            print(f"Passed: {self.passed_tests}")
            print(f"Failed: {self.failed_tests}")
            print(f"Skipped: {self.skipped_tests}")
            print(f"Success Rate: {(self.passed_tests / self.total_tests * 100):.2f}%")
            
            if self.failed_tests > 0:
                print("\nError Types:")
                for error_type, count in self.error_types.items():
                    print(f"- {error_type}: {count}")
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to analyze test results")
            return False

def main():
    """Main analyzer entry point."""
    try:
        analyzer = TestResultAnalyzer()
        
        if not analyzer.analyze_all_results():
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Analysis interrupted", "User interrupted analysis process")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Analysis process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 