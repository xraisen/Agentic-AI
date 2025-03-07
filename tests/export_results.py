import json
import sys
from pathlib import Path
from datetime import datetime
import csv
import xlsxwriter
from utils.logger import log_action, log_error, log_debug

class ResultsExporter:
    """Exports test results in various formats."""
    
    def __init__(self):
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.exports_dir = Path("test_exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def load_results(self):
        """Load aggregated test results."""
        try:
            log_action("Loading test results", "Reading aggregated report")
            
            report_files = list(self.reports_dir.glob("aggregated_report_*.json"))
            if not report_files:
                log_error(Exception("No aggregated reports found"), "No reports to export")
                return False
            
            # Load most recent report
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                self.results = json.load(f)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load test results")
            return False
    
    def export_results(self):
        """Export results in various formats."""
        try:
            log_action("Exporting results", "Generating export files")
            
            # Export in different formats
            if not all([
                self._export_json(),
                self._export_csv(),
                self._export_excel(),
                self._export_html()
            ]):
                return False
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to export results")
            return False
    
    def _export_json(self):
        """Export results in JSON format."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.exports_dir / f"test_results_{timestamp}.json"
            
            with open(export_file, 'w') as f:
                json.dump(self.results, f, indent=4)
            
            log_action("Exported JSON results", f"Saved to {export_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to export JSON results")
            return False
    
    def _export_csv(self):
        """Export results in CSV format."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export summary
            summary_file = self.exports_dir / f"test_summary_{timestamp}.csv"
            with open(summary_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for key, value in self.results["summary"].items():
                    writer.writerow([key, value])
            
            # Export issues
            issues_file = self.exports_dir / f"test_issues_{timestamp}.csv"
            with open(issues_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "Severity", "Description", "Timestamp"])
                for issue in self.results["issues"]:
                    writer.writerow([
                        issue["type"],
                        issue["severity"],
                        issue["description"],
                        issue["timestamp"]
                    ])
            
            # Export recommendations
            recommendations_file = self.exports_dir / f"test_recommendations_{timestamp}.csv"
            with open(recommendations_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Priority", "Recommendation", "Impact"])
                for rec in self.results["recommendations"]:
                    writer.writerow([
                        rec["category"],
                        rec["priority"],
                        rec["recommendation"],
                        rec["impact"]
                    ])
            
            log_action("Exported CSV results", "Saved to CSV files")
            return True
            
        except Exception as e:
            log_error(e, "Failed to export CSV results")
            return False
    
    def _export_excel(self):
        """Export results in Excel format."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file = self.exports_dir / f"test_results_{timestamp}.xlsx"
            
            workbook = xlsxwriter.Workbook(excel_file)
            
            # Summary sheet
            summary_sheet = workbook.add_worksheet("Summary")
            summary_sheet.write(0, 0, "Metric")
            summary_sheet.write(0, 1, "Value")
            for i, (key, value) in enumerate(self.results["summary"].items(), 1):
                summary_sheet.write(i, 0, key)
                summary_sheet.write(i, 1, value)
            
            # Issues sheet
            issues_sheet = workbook.add_worksheet("Issues")
            issues_sheet.write(0, 0, "Type")
            issues_sheet.write(0, 1, "Severity")
            issues_sheet.write(0, 2, "Description")
            issues_sheet.write(0, 3, "Timestamp")
            for i, issue in enumerate(self.results["issues"], 1):
                issues_sheet.write(i, 0, issue["type"])
                issues_sheet.write(i, 1, issue["severity"])
                issues_sheet.write(i, 2, issue["description"])
                issues_sheet.write(i, 3, issue["timestamp"])
            
            # Recommendations sheet
            recommendations_sheet = workbook.add_worksheet("Recommendations")
            recommendations_sheet.write(0, 0, "Category")
            recommendations_sheet.write(0, 1, "Priority")
            recommendations_sheet.write(0, 2, "Recommendation")
            recommendations_sheet.write(0, 3, "Impact")
            for i, rec in enumerate(self.results["recommendations"], 1):
                recommendations_sheet.write(i, 0, rec["category"])
                recommendations_sheet.write(i, 1, rec["priority"])
                recommendations_sheet.write(i, 2, rec["recommendation"])
                recommendations_sheet.write(i, 3, rec["impact"])
            
            # Trends sheet
            trends_sheet = workbook.add_worksheet("Trends")
            trends_sheet.write(0, 0, "Timestamp")
            trends_sheet.write(0, 1, "Coverage")
            trends_sheet.write(0, 2, "Performance")
            trends_sheet.write(0, 3, "Security")
            for i, (coverage, performance, security) in enumerate(zip(
                self.results["trends"]["coverage"],
                self.results["trends"]["performance"],
                self.results["trends"]["security"]
            ), 1):
                trends_sheet.write(i, 0, coverage["timestamp"])
                trends_sheet.write(i, 1, coverage["coverage"])
                trends_sheet.write(i, 2, performance["score"])
                trends_sheet.write(i, 3, security["score"])
            
            workbook.close()
            
            log_action("Exported Excel results", f"Saved to {excel_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to export Excel results")
            return False
    
    def _export_html(self):
        """Export results in HTML format."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = self.exports_dir / f"test_results_{timestamp}.html"
            
            with open(html_file, 'w') as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Test Results Report</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                        .summary { background-color: #f9f9f9; padding: 20px; }
                        .issues { background-color: #fff3f3; padding: 20px; }
                        .recommendations { background-color: #f3f9f3; padding: 20px; }
                        .trends { background-color: #f3f3f9; padding: 20px; }
                    </style>
                </head>
                <body>
                    <h1>Test Results Report</h1>
                    <p>Generated on: {timestamp}</p>
                    
                    <div class="summary">
                        <h2>Summary</h2>
                        <table>
                            <tr><th>Metric</th><th>Value</th></tr>
                """)
                
                # Write summary
                for key, value in self.results["summary"].items():
                    f.write(f"<tr><td>{key}</td><td>{value}</td></tr>")
                
                f.write("""
                        </table>
                    </div>
                    
                    <div class="issues">
                        <h2>Issues</h2>
                        <table>
                            <tr><th>Type</th><th>Severity</th><th>Description</th><th>Timestamp</th></tr>
                """)
                
                # Write issues
                for issue in self.results["issues"]:
                    f.write(f"""
                        <tr>
                            <td>{issue["type"]}</td>
                            <td>{issue["severity"]}</td>
                            <td>{issue["description"]}</td>
                            <td>{issue["timestamp"]}</td>
                        </tr>
                    """)
                
                f.write("""
                        </table>
                    </div>
                    
                    <div class="recommendations">
                        <h2>Recommendations</h2>
                        <table>
                            <tr><th>Category</th><th>Priority</th><th>Recommendation</th><th>Impact</th></tr>
                """)
                
                # Write recommendations
                for rec in self.results["recommendations"]:
                    f.write(f"""
                        <tr>
                            <td>{rec["category"]}</td>
                            <td>{rec["priority"]}</td>
                            <td>{rec["recommendation"]}</td>
                            <td>{rec["impact"]}</td>
                        </tr>
                    """)
                
                f.write("""
                        </table>
                    </div>
                    
                    <div class="trends">
                        <h2>Trends</h2>
                        <table>
                            <tr><th>Timestamp</th><th>Coverage</th><th>Performance</th><th>Security</th></tr>
                """)
                
                # Write trends
                for coverage, performance, security in zip(
                    self.results["trends"]["coverage"],
                    self.results["trends"]["performance"],
                    self.results["trends"]["security"]
                ):
                    f.write(f"""
                        <tr>
                            <td>{coverage["timestamp"]}</td>
                            <td>{coverage["coverage"]}%</td>
                            <td>{performance["score"]}</td>
                            <td>{security["score"]}</td>
                        </tr>
                    """)
                
                f.write("""
                        </table>
                    </div>
                </body>
                </html>
                """)
            
            log_action("Exported HTML results", f"Saved to {html_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to export HTML results")
            return False

def main():
    """Main exporter entry point."""
    try:
        exporter = ResultsExporter()
        
        # Load and export results
        if not all([
            exporter.load_results(),
            exporter.export_results()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Export interrupted", "User interrupted results export")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Results export failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 