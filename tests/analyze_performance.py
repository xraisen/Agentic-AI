import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from statistics import mean, median, stdev
from utils.logger import log_action, log_error, log_debug

class PerformanceAnalyzer:
    """Analyzes test performance metrics."""
    
    def __init__(self):
        self.test_data_dir = Path("tests/test_data")
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Performance metrics
        self.metrics = {
            "response_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "concurrent_requests": [],
            "error_rates": [],
            "test_durations": defaultdict(list)
        }
    
    def load_performance_data(self):
        """Load performance test data."""
        try:
            log_action("Loading performance data", "Reading test data files")
            
            performance_file = self.test_data_dir / "performance.json"
            if not performance_file.exists():
                log_error(Exception("Performance data file not found"), "performance.json not found")
                return False
            
            with open(performance_file, 'r') as f:
                data = json.load(f)
            
            # Extract metrics
            for entry in data:
                self.metrics["response_times"].append(entry["response_time"])
                self.metrics["memory_usage"].append(entry["memory_usage"])
                self.metrics["cpu_usage"].append(entry["cpu_usage"])
                self.metrics["concurrent_requests"].append(entry["concurrent_requests"])
                self.metrics["error_rates"].append(entry["error_rate"])
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load performance data")
            return False
    
    def analyze_metrics(self):
        """Analyze performance metrics."""
        try:
            log_action("Analyzing performance metrics", "Calculating statistics")
            
            analysis = {}
            
            # Response time analysis
            if self.metrics["response_times"]:
                analysis["response_time"] = {
                    "mean": mean(self.metrics["response_times"]),
                    "median": median(self.metrics["response_times"]),
                    "std_dev": stdev(self.metrics["response_times"]) if len(self.metrics["response_times"]) > 1 else 0,
                    "min": min(self.metrics["response_times"]),
                    "max": max(self.metrics["response_times"])
                }
            
            # Memory usage analysis
            if self.metrics["memory_usage"]:
                analysis["memory_usage"] = {
                    "mean": mean(self.metrics["memory_usage"]),
                    "median": median(self.metrics["memory_usage"]),
                    "std_dev": stdev(self.metrics["memory_usage"]) if len(self.metrics["memory_usage"]) > 1 else 0,
                    "min": min(self.metrics["memory_usage"]),
                    "max": max(self.metrics["memory_usage"])
                }
            
            # CPU usage analysis
            if self.metrics["cpu_usage"]:
                analysis["cpu_usage"] = {
                    "mean": mean(self.metrics["cpu_usage"]),
                    "median": median(self.metrics["cpu_usage"]),
                    "std_dev": stdev(self.metrics["cpu_usage"]) if len(self.metrics["cpu_usage"]) > 1 else 0,
                    "min": min(self.metrics["cpu_usage"]),
                    "max": max(self.metrics["cpu_usage"])
                }
            
            # Concurrent requests analysis
            if self.metrics["concurrent_requests"]:
                analysis["concurrent_requests"] = {
                    "mean": mean(self.metrics["concurrent_requests"]),
                    "median": median(self.metrics["concurrent_requests"]),
                    "std_dev": stdev(self.metrics["concurrent_requests"]) if len(self.metrics["concurrent_requests"]) > 1 else 0,
                    "min": min(self.metrics["concurrent_requests"]),
                    "max": max(self.metrics["concurrent_requests"])
                }
            
            # Error rate analysis
            if self.metrics["error_rates"]:
                analysis["error_rate"] = {
                    "mean": mean(self.metrics["error_rates"]),
                    "median": median(self.metrics["error_rates"]),
                    "std_dev": stdev(self.metrics["error_rates"]) if len(self.metrics["error_rates"]) > 1 else 0,
                    "min": min(self.metrics["error_rates"]),
                    "max": max(self.metrics["error_rates"])
                }
            
            self.analysis = analysis
            return True
            
        except Exception as e:
            log_error(e, "Failed to analyze performance metrics")
            return False
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks."""
        try:
            log_action("Identifying bottlenecks", "Analyzing performance issues")
            
            bottlenecks = []
            
            # Response time bottlenecks
            if self.metrics["response_times"]:
                avg_response_time = mean(self.metrics["response_times"])
                if avg_response_time > 2.0:  # Threshold: 2 seconds
                    bottlenecks.append({
                        "type": "response_time",
                        "severity": "high" if avg_response_time > 5.0 else "medium",
                        "description": f"High average response time: {avg_response_time:.2f}s",
                        "recommendation": "Optimize API calls and database queries"
                    })
            
            # Memory bottlenecks
            if self.metrics["memory_usage"]:
                avg_memory = mean(self.metrics["memory_usage"])
                if avg_memory > 500:  # Threshold: 500MB
                    bottlenecks.append({
                        "type": "memory",
                        "severity": "high" if avg_memory > 1000 else "medium",
                        "description": f"High memory usage: {avg_memory:.2f}MB",
                        "recommendation": "Implement memory management and garbage collection"
                    })
            
            # CPU bottlenecks
            if self.metrics["cpu_usage"]:
                avg_cpu = mean(self.metrics["cpu_usage"])
                if avg_cpu > 80:  # Threshold: 80%
                    bottlenecks.append({
                        "type": "cpu",
                        "severity": "high" if avg_cpu > 90 else "medium",
                        "description": f"High CPU usage: {avg_cpu:.2f}%",
                        "recommendation": "Optimize CPU-intensive operations"
                    })
            
            # Error rate bottlenecks
            if self.metrics["error_rates"]:
                avg_error_rate = mean(self.metrics["error_rates"])
                if avg_error_rate > 0.05:  # Threshold: 5%
                    bottlenecks.append({
                        "type": "error_rate",
                        "severity": "high" if avg_error_rate > 0.1 else "medium",
                        "description": f"High error rate: {avg_error_rate:.2%}",
                        "recommendation": "Improve error handling and recovery"
                    })
            
            self.bottlenecks = bottlenecks
            return True
            
        except Exception as e:
            log_error(e, "Failed to identify bottlenecks")
            return False
    
    def generate_report(self):
        """Generate performance analysis report."""
        try:
            log_action("Generating performance report", "Creating analysis report")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"performance_report_{timestamp}.json"
            
            report = {
                "timestamp": timestamp,
                "metrics": self.analysis,
                "bottlenecks": self.bottlenecks,
                "recommendations": self._generate_recommendations()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=4)
            
            # Print summary
            print("\nPerformance Analysis Summary:")
            print(f"Response Time: {self.analysis['response_time']['mean']:.2f}s")
            print(f"Memory Usage: {self.analysis['memory_usage']['mean']:.2f}MB")
            print(f"CPU Usage: {self.analysis['cpu_usage']['mean']:.2f}%")
            print(f"Error Rate: {self.analysis['error_rate']['mean']:.2%}")
            
            if self.bottlenecks:
                print("\nIdentified Bottlenecks:")
                for bottleneck in self.bottlenecks:
                    print(f"- {bottleneck['type']}: {bottleneck['description']}")
            
            log_action("Performance report generated", f"Report saved to {report_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate performance report")
            return False
    
    def _generate_recommendations(self):
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Response time recommendations
        if self.metrics["response_times"]:
            avg_response_time = mean(self.metrics["response_times"])
            if avg_response_time > 1.0:
                recommendations.append({
                    "category": "response_time",
                    "priority": "high" if avg_response_time > 2.0 else "medium",
                    "recommendation": "Implement caching and optimize database queries",
                    "impact": "Reduce response time by 30-50%"
                })
        
        # Memory recommendations
        if self.metrics["memory_usage"]:
            avg_memory = mean(self.metrics["memory_usage"])
            if avg_memory > 300:
                recommendations.append({
                    "category": "memory",
                    "priority": "high" if avg_memory > 500 else "medium",
                    "recommendation": "Implement memory pooling and optimize resource usage",
                    "impact": "Reduce memory usage by 20-40%"
                })
        
        # CPU recommendations
        if self.metrics["cpu_usage"]:
            avg_cpu = mean(self.metrics["cpu_usage"])
            if avg_cpu > 60:
                recommendations.append({
                    "category": "cpu",
                    "priority": "high" if avg_cpu > 80 else "medium",
                    "recommendation": "Optimize CPU-intensive operations and implement parallel processing",
                    "impact": "Reduce CPU usage by 25-45%"
                })
        
        # Error rate recommendations
        if self.metrics["error_rates"]:
            avg_error_rate = mean(self.metrics["error_rates"])
            if avg_error_rate > 0.03:
                recommendations.append({
                    "category": "error_rate",
                    "priority": "high" if avg_error_rate > 0.05 else "medium",
                    "recommendation": "Improve error handling and implement retry mechanisms",
                    "impact": "Reduce error rate by 40-60%"
                })
        
        return recommendations

def main():
    """Main analyzer entry point."""
    try:
        analyzer = PerformanceAnalyzer()
        
        # Load and analyze data
        if not all([
            analyzer.load_performance_data(),
            analyzer.analyze_metrics(),
            analyzer.identify_bottlenecks(),
            analyzer.generate_report()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Analysis interrupted", "User interrupted performance analysis")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Performance analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 