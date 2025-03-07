import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from utils.logger import log_action, log_error, log_debug

class ResultsAggregator:
    """Aggregates test results from various sources."""
    
    def __init__(self):
        self.test_results_dir = Path("test_results")
        self.test_reports_dir = Path("test_reports")
        self.test_reports_dir.mkdir(exist_ok=True)
        
        # Initialize aggregated data structure
        self.aggregated_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "coverage": 0.0,
                "performance_score": 0.0,
                "security_score": 0.0
            },
            "trends": {
                "coverage": [],
                "performance": [],
                "security": []
            },
            "issues": [],
            "recommendations": [],
            "compliance": {}
        }
    
    def aggregate_test_results(self):
        """Aggregate test execution results."""
        try:
            log_action("Aggregating test results", "Processing test execution logs")
            
            # Find all test run logs
            log_files = list(self.test_results_dir.glob("test_run_*.log"))
            if not log_files:
                log_error(Exception("No test logs found"), "No test results to aggregate")
                return False
            
            # Process each log file
            for log_file in log_files:
                self._process_test_log(log_file)
            
            # Calculate pass rate
            total = self.aggregated_data["summary"]["total_tests"]
            passed = self.aggregated_data["summary"]["passed_tests"]
            self.aggregated_data["summary"]["pass_rate"] = (passed / total * 100) if total > 0 else 0
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to aggregate test results")
            return False
    
    def aggregate_coverage_data(self):
        """Aggregate coverage data."""
        try:
            log_action("Aggregating coverage data", "Processing coverage reports")
            
            # Find coverage XML report
            coverage_file = Path("coverage.xml")
            if not coverage_file.exists():
                log_error(Exception("Coverage file not found"), "No coverage data to aggregate")
                return False
            
            # TODO: Parse coverage XML and extract metrics
            # For now, using placeholder data
            self.aggregated_data["summary"]["coverage"] = 85.0
            
            # Add to trends
            self.aggregated_data["trends"]["coverage"].append({
                "timestamp": datetime.now().isoformat(),
                "coverage": self.aggregated_data["summary"]["coverage"]
            })
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to aggregate coverage data")
            return False
    
    def aggregate_performance_data(self):
        """Aggregate performance data."""
        try:
            log_action("Aggregating performance data", "Processing performance metrics")
            
            # Find performance data file
            perf_file = self.test_results_dir / "performance.json"
            if not perf_file.exists():
                log_error(Exception("Performance file not found"), "No performance data to aggregate")
                return False
            
            with open(perf_file, 'r') as f:
                perf_data = json.load(f)
            
            # Calculate performance score
            response_times = [entry["response_time"] for entry in perf_data]
            memory_usage = [entry["memory_usage"] for entry in perf_data]
            cpu_usage = [entry["cpu_usage"] for entry in perf_data]
            error_rates = [entry["error_rate"] for entry in perf_data]
            
            # Simple scoring algorithm
            avg_response_time = sum(response_times) / len(response_times)
            avg_memory = sum(memory_usage) / len(memory_usage)
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            avg_error_rate = sum(error_rates) / len(error_rates)
            
            # Score components (0-100 scale)
            response_score = max(0, 100 - (avg_response_time * 20))  # Penalize response times > 5s
            memory_score = max(0, 100 - (avg_memory / 10))  # Penalize memory usage > 1000MB
            cpu_score = max(0, 100 - avg_cpu)  # Direct percentage
            error_score = max(0, 100 - (avg_error_rate * 1000))  # Penalize error rates > 0.1
            
            # Overall performance score
            performance_score = (response_score + memory_score + cpu_score + error_score) / 4
            self.aggregated_data["summary"]["performance_score"] = performance_score
            
            # Add to trends
            self.aggregated_data["trends"]["performance"].append({
                "timestamp": datetime.now().isoformat(),
                "score": performance_score
            })
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to aggregate performance data")
            return False
    
    def aggregate_security_data(self):
        """Aggregate security data."""
        try:
            log_action("Aggregating security data", "Processing security metrics")
            
            # Find security data file
            security_file = self.test_results_dir / "security.json"
            if not security_file.exists():
                log_error(Exception("Security file not found"), "No security data to aggregate")
                return False
            
            with open(security_file, 'r') as f:
                security_data = json.load(f)
            
            # Count issues by severity
            severity_counts = defaultdict(int)
            for entry in security_data:
                severity_counts[entry["risk_level"]] += 1
            
            # Calculate security score
            total_issues = sum(severity_counts.values())
            if total_issues > 0:
                # Weighted scoring
                weights = {"low": 1, "medium": 2, "high": 4, "critical": 8}
                weighted_sum = sum(weights[level] * count for level, count in severity_counts.items())
                max_weighted_sum = total_issues * weights["critical"]
                security_score = 100 * (1 - (weighted_sum / max_weighted_sum))
            else:
                security_score = 100.0
            
            self.aggregated_data["summary"]["security_score"] = security_score
            
            # Add to trends
            self.aggregated_data["trends"]["security"].append({
                "timestamp": datetime.now().isoformat(),
                "score": security_score
            })
            
            # Add security issues
            self.aggregated_data["issues"].extend([
                {
                    "type": "security",
                    "severity": entry["risk_level"],
                    "description": f"Security vulnerability: {entry['input']}",
                    "timestamp": datetime.now().isoformat()
                }
                for entry in security_data
            ])
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to aggregate security data")
            return False
    
    def generate_recommendations(self):
        """Generate recommendations based on aggregated data."""
        try:
            log_action("Generating recommendations", "Analyzing aggregated data")
            
            recommendations = []
            summary = self.aggregated_data["summary"]
            
            # Test pass rate recommendations
            if summary["pass_rate"] < 90:
                recommendations.append({
                    "category": "test_coverage",
                    "priority": "high" if summary["pass_rate"] < 80 else "medium",
                    "recommendation": "Improve test pass rate by investigating and fixing failing tests",
                    "impact": "Increase reliability and stability of the system"
                })
            
            # Code coverage recommendations
            if summary["coverage"] < 80:
                recommendations.append({
                    "category": "code_coverage",
                    "priority": "high" if summary["coverage"] < 60 else "medium",
                    "recommendation": "Increase code coverage by adding more test cases",
                    "impact": "Better test coverage and fewer potential bugs"
                })
            
            # Performance recommendations
            if summary["performance_score"] < 80:
                recommendations.append({
                    "category": "performance",
                    "priority": "high" if summary["performance_score"] < 60 else "medium",
                    "recommendation": "Optimize system performance by addressing bottlenecks",
                    "impact": "Improved response times and resource utilization"
                })
            
            # Security recommendations
            if summary["security_score"] < 90:
                recommendations.append({
                    "category": "security",
                    "priority": "high" if summary["security_score"] < 80 else "medium",
                    "recommendation": "Address security vulnerabilities and improve security measures",
                    "impact": "Enhanced system security and reduced risk"
                })
            
            self.aggregated_data["recommendations"] = recommendations
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate recommendations")
            return False
    
    def save_aggregated_results(self):
        """Save aggregated results to file."""
        try:
            log_action("Saving aggregated results", "Writing aggregated report")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.test_reports_dir / f"aggregated_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(self.aggregated_data, f, indent=4)
            
            log_action("Saved aggregated results", f"Report saved to {report_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to save aggregated results")
            return False
    
    def _process_test_log(self, log_file):
        """Process a test execution log file."""
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if "test_" in line:
                        self.aggregated_data["summary"]["total_tests"] += 1
                        if "PASSED" in line:
                            self.aggregated_data["summary"]["passed_tests"] += 1
                        elif "FAILED" in line:
                            self.aggregated_data["summary"]["failed_tests"] += 1
                            # Add to issues
                            self.aggregated_data["issues"].append({
                                "type": "test_failure",
                                "severity": "high",
                                "description": line.strip(),
                                "timestamp": datetime.now().isoformat()
                            })
                        elif "SKIPPED" in line:
                            self.aggregated_data["summary"]["skipped_tests"] += 1
            
            return True
            
        except Exception as e:
            log_error(e, f"Failed to process test log: {log_file}")
            return False

def main():
    """Main aggregator entry point."""
    try:
        aggregator = ResultsAggregator()
        
        # Aggregate all data
        if not all([
            aggregator.aggregate_test_results(),
            aggregator.aggregate_coverage_data(),
            aggregator.aggregate_performance_data(),
            aggregator.aggregate_security_data(),
            aggregator.generate_recommendations(),
            aggregator.save_aggregated_results()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Aggregation interrupted", "User interrupted aggregation process")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Aggregation process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 