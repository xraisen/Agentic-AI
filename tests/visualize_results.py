import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import log_action, log_error, log_debug

class ResultsVisualizer:
    """Visualizes test results using matplotlib."""
    
    def __init__(self):
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.plots_dir = Path("test_plots")
        self.plots_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn')
        sns.set_palette("husl")
    
    def load_results(self):
        """Load aggregated test results."""
        try:
            log_action("Loading test results", "Reading aggregated report")
            
            report_files = list(self.reports_dir.glob("aggregated_report_*.json"))
            if not report_files:
                log_error(Exception("No aggregated reports found"), "No reports to visualize")
                return False
            
            # Load most recent report
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                self.results = json.load(f)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load test results")
            return False
    
    def generate_plots(self):
        """Generate visualization plots."""
        try:
            log_action("Generating plots", "Creating visualization plots")
            
            # Generate summary plots
            self._plot_test_summary()
            self._plot_coverage_trend()
            self._plot_performance_trend()
            self._plot_security_trend()
            self._plot_issues_by_type()
            self._plot_compliance_status()
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate plots")
            return False
    
    def _plot_test_summary(self):
        """Plot test summary statistics."""
        plt.figure(figsize=(10, 6))
        
        summary = self.results["summary"]
        labels = ["Passed", "Failed", "Skipped"]
        sizes = [
            summary["passed_tests"],
            summary["failed_tests"],
            summary["skipped_tests"]
        ]
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Test Results Summary")
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"test_summary_{timestamp}.png")
        plt.close()
    
    def _plot_coverage_trend(self):
        """Plot code coverage trend."""
        plt.figure(figsize=(10, 6))
        
        trends = self.results["trends"]["coverage"]
        timestamps = [t["timestamp"] for t in trends]
        coverage = [t["coverage"] for t in trends]
        
        plt.plot(timestamps, coverage, marker='o')
        plt.title("Code Coverage Trend")
        plt.xlabel("Timestamp")
        plt.ylabel("Coverage (%)")
        plt.xticks(rotation=45)
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"coverage_trend_{timestamp}.png")
        plt.close()
    
    def _plot_performance_trend(self):
        """Plot performance trend."""
        plt.figure(figsize=(10, 6))
        
        trends = self.results["trends"]["performance"]
        timestamps = [t["timestamp"] for t in trends]
        scores = [t["score"] for t in trends]
        
        plt.plot(timestamps, scores, marker='o', color='green')
        plt.title("Performance Score Trend")
        plt.xlabel("Timestamp")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"performance_trend_{timestamp}.png")
        plt.close()
    
    def _plot_security_trend(self):
        """Plot security trend."""
        plt.figure(figsize=(10, 6))
        
        trends = self.results["trends"]["security"]
        timestamps = [t["timestamp"] for t in trends]
        scores = [t["score"] for t in trends]
        
        plt.plot(timestamps, scores, marker='o', color='red')
        plt.title("Security Score Trend")
        plt.xlabel("Timestamp")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"security_trend_{timestamp}.png")
        plt.close()
    
    def _plot_issues_by_type(self):
        """Plot issues by type and severity."""
        plt.figure(figsize=(12, 6))
        
        issues = self.results["issues"]
        issue_types = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
        
        for issue in issues:
            issue_types[issue["type"]][issue["severity"]] += 1
        
        # Prepare data for stacked bar chart
        types = list(issue_types.keys())
        high_severity = [issue_types[t]["high"] for t in types]
        medium_severity = [issue_types[t]["medium"] for t in types]
        low_severity = [issue_types[t]["low"] for t in types]
        
        # Plot stacked bars
        plt.bar(types, high_severity, label="High", color='red')
        plt.bar(types, medium_severity, bottom=high_severity, label="Medium", color='orange')
        plt.bar(types, low_severity, bottom=[sum(x) for x in zip(high_severity, medium_severity)],
                label="Low", color='green')
        
        plt.title("Issues by Type and Severity")
        plt.xlabel("Issue Type")
        plt.ylabel("Count")
        plt.legend()
        plt.xticks(rotation=45)
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"issues_by_type_{timestamp}.png")
        plt.close()
    
    def _plot_compliance_status(self):
        """Plot compliance status."""
        plt.figure(figsize=(10, 6))
        
        compliance = self.results["compliance"]
        standards = list(compliance.keys())
        statuses = [compliance[s]["status"] for s in standards]
        
        # Convert status to numeric values
        status_values = {
            "compliant": 100,
            "partial": 50,
            "non_compliant": 0,
            "unknown": 25
        }
        values = [status_values[s] for s in statuses]
        
        plt.bar(standards, values)
        plt.title("Compliance Status")
        plt.xlabel("Standard")
        plt.ylabel("Compliance (%)")
        plt.xticks(rotation=45)
        
        # Add value labels
        for i, v in enumerate(values):
            plt.text(i, v + 5, f"{v}%", ha='center')
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(self.plots_dir / f"compliance_status_{timestamp}.png")
        plt.close()
    
    def generate_dashboard(self):
        """Generate a dashboard of all plots."""
        try:
            log_action("Generating dashboard", "Creating visualization dashboard")
            
            # Create figure with subplots
            fig = plt.figure(figsize=(20, 15))
            
            # Test summary
            plt.subplot(2, 2, 1)
            summary = self.results["summary"]
            labels = ["Passed", "Failed", "Skipped"]
            sizes = [
                summary["passed_tests"],
                summary["failed_tests"],
                summary["skipped_tests"]
            ]
            plt.pie(sizes, labels=labels, autopct='%1.1f%%')
            plt.title("Test Results Summary")
            
            # Coverage trend
            plt.subplot(2, 2, 2)
            trends = self.results["trends"]["coverage"]
            timestamps = [t["timestamp"] for t in trends]
            coverage = [t["coverage"] for t in trends]
            plt.plot(timestamps, coverage, marker='o')
            plt.title("Code Coverage Trend")
            plt.xlabel("Timestamp")
            plt.ylabel("Coverage (%)")
            plt.xticks(rotation=45)
            
            # Performance trend
            plt.subplot(2, 2, 3)
            trends = self.results["trends"]["performance"]
            timestamps = [t["timestamp"] for t in trends]
            scores = [t["score"] for t in trends]
            plt.plot(timestamps, scores, marker='o', color='green')
            plt.title("Performance Score Trend")
            plt.xlabel("Timestamp")
            plt.ylabel("Score")
            plt.xticks(rotation=45)
            
            # Security trend
            plt.subplot(2, 2, 4)
            trends = self.results["trends"]["security"]
            timestamps = [t["timestamp"] for t in trends]
            scores = [t["score"] for t in trends]
            plt.plot(timestamps, scores, marker='o', color='red')
            plt.title("Security Score Trend")
            plt.xlabel("Timestamp")
            plt.ylabel("Score")
            plt.xticks(rotation=45)
            
            # Adjust layout and save
            plt.tight_layout()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plt.savefig(self.plots_dir / f"dashboard_{timestamp}.png")
            plt.close()
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate dashboard")
            return False

def main():
    """Main visualizer entry point."""
    try:
        visualizer = ResultsVisualizer()
        
        # Load and generate visualizations
        if not all([
            visualizer.load_results(),
            visualizer.generate_plots(),
            visualizer.generate_dashboard()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Visualization interrupted", "User interrupted visualization generation")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Visualization generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 