import json
import sys
from pathlib import Path
from datetime import datetime
import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
from utils.logger import log_action, log_error, log_debug

class TestDashboard:
    """Generates an interactive test results dashboard."""
    
    def __init__(self):
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.dashboard_dir = Path("test_dashboard")
        self.dashboard_dir.mkdir(exist_ok=True)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
    
    def load_results(self):
        """Load aggregated test results."""
        try:
            log_action("Loading test results", "Reading aggregated report")
            
            report_files = list(self.reports_dir.glob("aggregated_report_*.json"))
            if not report_files:
                log_error(Exception("No aggregated reports found"), "No results to display")
                return False
            
            # Load most recent report
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                self.results = json.load(f)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load test results")
            return False
    
    def setup_layout(self):
        """Set up the dashboard layout."""
        try:
            log_action("Setting up dashboard", "Configuring dashboard layout")
            
            # Create layout
            self.app.layout = html.Div([
                html.H1("Test Results Dashboard"),
                html.Div([
                    html.H2("Summary"),
                    self._create_summary_cards()
                ]),
                html.Div([
                    html.H2("Trends"),
                    self._create_trend_charts()
                ]),
                html.Div([
                    html.H2("Issues"),
                    self._create_issues_table()
                ]),
                html.Div([
                    html.H2("Recommendations"),
                    self._create_recommendations_table()
                ])
            ])
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to set up dashboard")
            return False
    
    def _create_summary_cards(self):
        """Create summary metric cards."""
        try:
            summary = self.results["summary"]
            
            cards = html.Div([
                html.Div([
                    html.H3("Test Results"),
                    html.P(f"Total Tests: {summary['total_tests']}"),
                    html.P(f"Passed: {summary['passed_tests']}"),
                    html.P(f"Failed: {summary['failed_tests']}"),
                    html.P(f"Skipped: {summary['skipped_tests']}"),
                    html.P(f"Pass Rate: {summary['pass_rate']:.2f}%")
                ], className="card"),
                html.Div([
                    html.H3("Coverage"),
                    html.P(f"Code Coverage: {summary['coverage']:.2f}%")
                ], className="card"),
                html.Div([
                    html.H3("Performance"),
                    html.P(f"Performance Score: {summary['performance_score']:.2f}")
                ], className="card"),
                html.Div([
                    html.H3("Security"),
                    html.P(f"Security Score: {summary['security_score']:.2f}")
                ], className="card")
            ], className="summary-cards")
            
            return cards
            
        except Exception as e:
            log_error(e, "Failed to create summary cards")
            return html.Div("Error creating summary cards")
    
    def _create_trend_charts(self):
        """Create trend visualization charts."""
        try:
            trends = self.results["trends"]
            
            # Coverage trend
            coverage_fig = px.line(
                trends["coverage"],
                x="timestamp",
                y="coverage",
                title="Code Coverage Trend"
            )
            
            # Performance trend
            performance_fig = px.line(
                trends["performance"],
                x="timestamp",
                y="score",
                title="Performance Score Trend"
            )
            
            # Security trend
            security_fig = px.line(
                trends["security"],
                x="timestamp",
                y="score",
                title="Security Score Trend"
            )
            
            charts = html.Div([
                dcc.Graph(figure=coverage_fig),
                dcc.Graph(figure=performance_fig),
                dcc.Graph(figure=security_fig)
            ], className="trend-charts")
            
            return charts
            
        except Exception as e:
            log_error(e, "Failed to create trend charts")
            return html.Div("Error creating trend charts")
    
    def _create_issues_table(self):
        """Create issues table."""
        try:
            issues = self.results["issues"]
            
            table = html.Table([
                html.Tr([html.Th(col) for col in ["Type", "Severity", "Description", "Timestamp"]]),
                *[html.Tr([
                    html.Td(issue["type"]),
                    html.Td(issue["severity"]),
                    html.Td(issue["description"]),
                    html.Td(issue["timestamp"])
                ]) for issue in issues]
            ], className="issues-table")
            
            return table
            
        except Exception as e:
            log_error(e, "Failed to create issues table")
            return html.Div("Error creating issues table")
    
    def _create_recommendations_table(self):
        """Create recommendations table."""
        try:
            recommendations = self.results["recommendations"]
            
            table = html.Table([
                html.Tr([html.Th(col) for col in ["Category", "Priority", "Recommendation", "Impact"]]),
                *[html.Tr([
                    html.Td(rec["category"]),
                    html.Td(rec["priority"]),
                    html.Td(rec["recommendation"]),
                    html.Td(rec["impact"])
                ]) for rec in recommendations]
            ], className="recommendations-table")
            
            return table
            
        except Exception as e:
            log_error(e, "Failed to create recommendations table")
            return html.Div("Error creating recommendations table")
    
    def run_dashboard(self):
        """Run the dashboard server."""
        try:
            log_action("Starting dashboard", "Launching dashboard server")
            
            # Run the server
            self.app.run_server(debug=True, port=8050)
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to run dashboard")
            return False

def main():
    """Main dashboard entry point."""
    try:
        dashboard = TestDashboard()
        
        # Load results and run dashboard
        if not all([
            dashboard.load_results(),
            dashboard.run_dashboard()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Dashboard interrupted", "User interrupted dashboard")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Dashboard failed")
        sys.exit(1)

if __name__ == "__main__":
    main()