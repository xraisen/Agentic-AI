import json
import sys
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from utils.logger import log_action, log_error, log_debug

class ResultsNotifier:
    """Sends notifications about test results."""
    
    def __init__(self):
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.notifications_dir = Path("test_notifications")
        self.notifications_dir.mkdir(exist_ok=True)
        self.exports_dir = Path("test_exports")
        self.exports_dir.mkdir(exist_ok=True)
        
        # Load notification configuration
        self.config = self._load_config()
        if self.config is None:
            self.config = {
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_address": "",
                    "to_addresses": []
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": ""
                },
                "thresholds": {
                    "test_pass_rate": 80,
                    "coverage": 80,
                    "performance_score": 80,
                    "security_score": 80
                }
            }
    
    def _load_config(self):
        """Load notification configuration."""
        try:
            config_file = Path("tests/notification_config.json")
            if not config_file.exists():
                return None
            
            with open(config_file, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            log_error(e, "Failed to load notification configuration")
            return None
    
    def load_results(self):
        """Load aggregated test results."""
        try:
            log_action("Loading test results", "Reading aggregated report")
            
            report_files = list(self.reports_dir.glob("aggregated_report_*.json"))
            if not report_files:
                log_error(Exception("No aggregated reports found"), "No results to notify")
                return False
            
            # Load most recent report
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                self.results = json.load(f)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load test results")
            return False
    
    def check_thresholds(self):
        """Check if results meet thresholds."""
        try:
            log_action("Checking thresholds", "Evaluating test results")
            
            summary = self.results["summary"]
            thresholds = self.config["thresholds"]
            
            issues = []
            
            # Check test pass rate
            pass_rate = (summary["passed_tests"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0
            if pass_rate < thresholds["test_pass_rate"]:
                issues.append({
                    "type": "test_pass_rate",
                    "threshold": thresholds["test_pass_rate"],
                    "actual": pass_rate,
                    "severity": "high" if pass_rate < 50 else "medium"
                })
            
            # Check coverage
            if summary["coverage"] < thresholds["coverage"]:
                issues.append({
                    "type": "coverage",
                    "threshold": thresholds["coverage"],
                    "actual": summary["coverage"],
                    "severity": "high" if summary["coverage"] < 50 else "medium"
                })
            
            # Check performance score
            if summary["performance_score"] < thresholds["performance_score"]:
                issues.append({
                    "type": "performance",
                    "threshold": thresholds["performance_score"],
                    "actual": summary["performance_score"],
                    "severity": "high" if summary["performance_score"] < 50 else "medium"
                })
            
            # Check security score
            if summary["security_score"] < thresholds["security_score"]:
                issues.append({
                    "type": "security",
                    "threshold": thresholds["security_score"],
                    "actual": summary["security_score"],
                    "severity": "high" if summary["security_score"] < 50 else "medium"
                })
            
            self.threshold_issues = issues
            return True
            
        except Exception as e:
            log_error(e, "Failed to check thresholds")
            return False
    
    def send_notifications(self):
        """Send notifications about test results."""
        try:
            log_action("Sending notifications", "Generating and sending notifications")
            
            # Generate notification content
            content = self._generate_notification_content()
            
            # Send notifications based on configuration
            if self.config["email"]["enabled"]:
                self._send_email_notification(content)
            
            if self.config["slack"]["enabled"]:
                self._send_slack_notification(content)
            
            # Save notification content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            notification_file = self.notifications_dir / f"notification_{timestamp}.json"
            
            with open(notification_file, 'w') as f:
                json.dump(content, f, indent=4)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to send notifications")
            return False
    
    def _generate_notification_content(self):
        """Generate notification content."""
        summary = self.results["summary"]
        
        content = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": summary["total_tests"],
                "passed_tests": summary["passed_tests"],
                "failed_tests": summary["failed_tests"],
                "skipped_tests": summary["skipped_tests"],
                "pass_rate": (summary["passed_tests"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0,
                "coverage": summary["coverage"],
                "performance_score": summary["performance_score"],
                "security_score": summary["security_score"]
            },
            "threshold_issues": self.threshold_issues,
            "critical_issues": [
                issue for issue in self.results["issues"]
                if issue["severity"] == "high"
            ],
            "recommendations": self.results["recommendations"]
        }
        
        return content
    
    def _send_email_notification(self, content):
        """Send email notification."""
        try:
            email_config = self.config["email"]
            
            # Create message
            msg = MIMEMultipart()
            msg["Subject"] = "Test Results Notification"
            msg["From"] = email_config["from_address"]
            msg["To"] = ", ".join(email_config["to_addresses"])
            
            # Create email body
            body = self._generate_email_body(content)
            msg.attach(MIMEText(body, "html"))
            
            # Attach report files
            self._attach_report_files(msg)
            
            # Send email
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)
            
            log_action("Sent email notification", "Email notification delivered")
            return True
            
        except Exception as e:
            log_error(e, "Failed to send email notification")
            return False
    
    def _send_slack_notification(self, content):
        """Send Slack notification."""
        try:
            # TODO: Implement Slack notification
            # This would require the slack-sdk package
            log_action("Slack notification", "Slack notification not implemented")
            return True
            
        except Exception as e:
            log_error(e, "Failed to send Slack notification")
            return False
    
    def _generate_email_body(self, content):
        """Generate HTML email body."""
        summary = content["summary"]
        issues = content["threshold_issues"]
        critical_issues = content["critical_issues"]
        recommendations = content["recommendations"]
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 20px; }}
                .issues {{ background-color: #fff3f3; padding: 20px; }}
                .recommendations {{ background-color: #f3f9f3; padding: 20px; }}
            </style>
        </head>
        <body>
            <h1>Test Results Notification</h1>
            <p>Generated on: {content["timestamp"]}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Tests</td><td>{summary["total_tests"]}</td></tr>
                    <tr><td>Passed Tests</td><td>{summary["passed_tests"]}</td></tr>
                    <tr><td>Failed Tests</td><td>{summary["failed_tests"]}</td></tr>
                    <tr><td>Skipped Tests</td><td>{summary["skipped_tests"]}</td></tr>
                    <tr><td>Pass Rate</td><td>{summary["pass_rate"]:.2f}%</td></tr>
                    <tr><td>Coverage</td><td>{summary["coverage"]:.2f}%</td></tr>
                    <tr><td>Performance Score</td><td>{summary["performance_score"]:.2f}</td></tr>
                    <tr><td>Security Score</td><td>{summary["security_score"]:.2f}</td></tr>
                </table>
            </div>
            
            {f'''
            <div class="issues">
                <h2>Threshold Issues</h2>
                <table>
                    <tr><th>Type</th><th>Threshold</th><th>Actual</th><th>Severity</th></tr>
                    {''.join(f'''
                    <tr>
                        <td>{issue["type"]}</td>
                        <td>{issue["threshold"]}</td>
                        <td>{issue["actual"]}</td>
                        <td>{issue["severity"]}</td>
                    </tr>
                    ''' for issue in issues)}
                </table>
            </div>
            ''' if issues else ""}
            
            {f'''
            <div class="issues">
                <h2>Critical Issues</h2>
                <table>
                    <tr><th>Type</th><th>Description</th><th>Timestamp</th></tr>
                    {''.join(f'''
                    <tr>
                        <td>{issue["type"]}</td>
                        <td>{issue["description"]}</td>
                        <td>{issue["timestamp"]}</td>
                    </tr>
                    ''' for issue in critical_issues)}
                </table>
            </div>
            ''' if critical_issues else ""}
            
            {f'''
            <div class="recommendations">
                <h2>Recommendations</h2>
                <table>
                    <tr><th>Category</th><th>Priority</th><th>Recommendation</th><th>Impact</th></tr>
                    {''.join(f'''
                    <tr>
                        <td>{rec["category"]}</td>
                        <td>{rec["priority"]}</td>
                        <td>{rec["recommendation"]}</td>
                        <td>{rec["impact"]}</td>
                    </tr>
                    ''' for rec in recommendations)}
                </table>
            </div>
            ''' if recommendations else ""}
        </body>
        </html>
        """
        
        return body
    
    def _attach_report_files(self, msg):
        """Attach report files to email."""
        try:
            # Attach JSON report
            report_files = list(self.reports_dir.glob("aggregated_report_*.json"))
            if report_files:
                latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                with open(latest_report, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=latest_report.name
                    )
                    msg.attach(attachment)
            
            # Attach Excel report
            excel_files = list(self.exports_dir.glob("test_results_*.xlsx"))
            if excel_files:
                latest_excel = max(excel_files, key=lambda x: x.stat().st_mtime)
                with open(latest_excel, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=latest_excel.name
                    )
                    msg.attach(attachment)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to attach report files")
            return False

def main():
    """Main notifier entry point."""
    try:
        notifier = ResultsNotifier()
        
        # Load results and send notifications
        if not all([
            notifier.load_results(),
            notifier.check_thresholds(),
            notifier.send_notifications()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Notification interrupted", "User interrupted notification process")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Notification process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 