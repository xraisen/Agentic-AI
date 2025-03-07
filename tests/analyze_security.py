import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from utils.logger import log_action, log_error, log_debug

class SecurityAnalyzer:
    """Analyzes security test results."""
    
    def __init__(self):
        self.test_data_dir = Path("tests/test_data")
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Security metrics
        self.metrics = {
            "vulnerabilities": [],
            "threats": [],
            "risks": [],
            "mitigations": [],
            "compliance": []
        }
    
    def load_security_data(self):
        """Load security test data."""
        try:
            log_action("Loading security data", "Reading test data files")
            
            security_file = self.test_data_dir / "security.json"
            if not security_file.exists():
                log_error(Exception("Security data file not found"), "security.json not found")
                return False
            
            with open(security_file, 'r') as f:
                data = json.load(f)
            
            # Extract metrics
            for entry in data:
                self.metrics["vulnerabilities"].append({
                    "input": entry["input"],
                    "risk_level": entry["risk_level"],
                    "expected_behavior": entry["expected_behavior"]
                })
                self.metrics["mitigations"].extend(entry["mitigation"])
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to load security data")
            return False
    
    def analyze_vulnerabilities(self):
        """Analyze security vulnerabilities."""
        try:
            log_action("Analyzing vulnerabilities", "Processing security issues")
            
            analysis = {
                "vulnerability_types": defaultdict(int),
                "risk_levels": defaultdict(int),
                "mitigation_coverage": defaultdict(int),
                "compliance_issues": []
            }
            
            # Analyze vulnerabilities
            for vuln in self.metrics["vulnerabilities"]:
                # Count vulnerability types
                vuln_type = self._categorize_vulnerability(vuln["input"])
                analysis["vulnerability_types"][vuln_type] += 1
                
                # Count risk levels
                analysis["risk_levels"][vuln["risk_level"]] += 1
                
                # Check expected behavior
                if not all(vuln["expected_behavior"].values()):
                    analysis["compliance_issues"].append({
                        "input": vuln["input"],
                        "risk_level": vuln["risk_level"],
                        "missing_controls": [
                            k for k, v in vuln["expected_behavior"].items() if not v
                        ]
                    })
            
            # Analyze mitigations
            for mitigation in self.metrics["mitigations"]:
                analysis["mitigation_coverage"][mitigation] += 1
            
            self.analysis = analysis
            return True
            
        except Exception as e:
            log_error(e, "Failed to analyze vulnerabilities")
            return False
    
    def identify_threats(self):
        """Identify security threats."""
        try:
            log_action("Identifying threats", "Analyzing security threats")
            
            threats = []
            
            # Input validation threats
            if self._has_validation_issues():
                threats.append({
                    "type": "input_validation",
                    "severity": "high",
                    "description": "Insufficient input validation",
                    "impact": "Potential for injection attacks",
                    "recommendation": "Implement strict input validation"
                })
            
            # Authentication threats
            if self._has_auth_issues():
                threats.append({
                    "type": "authentication",
                    "severity": "high",
                    "description": "Weak authentication mechanisms",
                    "impact": "Unauthorized access risk",
                    "recommendation": "Strengthen authentication"
                })
            
            # Authorization threats
            if self._has_authz_issues():
                threats.append({
                    "type": "authorization",
                    "severity": "high",
                    "description": "Insufficient authorization checks",
                    "impact": "Privilege escalation risk",
                    "recommendation": "Implement proper authorization"
                })
            
            # Data protection threats
            if self._has_data_protection_issues():
                threats.append({
                    "type": "data_protection",
                    "severity": "high",
                    "description": "Inadequate data protection",
                    "impact": "Data breach risk",
                    "recommendation": "Enhance data protection"
                })
            
            self.threats = threats
            return True
            
        except Exception as e:
            log_error(e, "Failed to identify threats")
            return False
    
    def generate_report(self):
        """Generate security analysis report."""
        try:
            log_action("Generating security report", "Creating analysis report")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"security_report_{timestamp}.json"
            
            report = {
                "timestamp": timestamp,
                "vulnerability_analysis": self.analysis,
                "threats": self.threats,
                "recommendations": self._generate_recommendations(),
                "compliance_status": self._generate_compliance_status()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=4)
            
            # Print summary
            print("\nSecurity Analysis Summary:")
            print(f"Total Vulnerabilities: {len(self.metrics['vulnerabilities'])}")
            print(f"Risk Levels:")
            for level, count in self.analysis["risk_levels"].items():
                print(f"- {level}: {count}")
            
            if self.threats:
                print("\nIdentified Threats:")
                for threat in self.threats:
                    print(f"- {threat['type']}: {threat['description']}")
            
            log_action("Security report generated", f"Report saved to {report_file}")
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate security report")
            return False
    
    def _categorize_vulnerability(self, input_str):
        """Categorize vulnerability type based on input."""
        if "DROP TABLE" in input_str:
            return "sql_injection"
        elif "<script>" in input_str:
            return "xss"
        elif "eval(" in input_str:
            return "code_injection"
        elif "etc/passwd" in input_str:
            return "path_traversal"
        elif "OR '1'='1" in input_str:
            return "authentication_bypass"
        else:
            return "other"
    
    def _has_validation_issues(self):
        """Check for input validation issues."""
        return any(
            not vuln["expected_behavior"]["validation"]
            for vuln in self.metrics["vulnerabilities"]
        )
    
    def _has_auth_issues(self):
        """Check for authentication issues."""
        return any(
            not vuln["expected_behavior"]["authentication"]
            for vuln in self.metrics["vulnerabilities"]
        )
    
    def _has_authz_issues(self):
        """Check for authorization issues."""
        return any(
            not vuln["expected_behavior"]["authorization"]
            for vuln in self.metrics["vulnerabilities"]
        )
    
    def _has_data_protection_issues(self):
        """Check for data protection issues."""
        return any(
            not vuln["expected_behavior"]["data_protection"]
            for vuln in self.metrics["vulnerabilities"]
        )
    
    def _generate_recommendations(self):
        """Generate security improvement recommendations."""
        recommendations = []
        
        # Input validation recommendations
        if self._has_validation_issues():
            recommendations.append({
                "category": "input_validation",
                "priority": "high",
                "recommendation": "Implement comprehensive input validation",
                "impact": "Prevent injection attacks"
            })
        
        # Authentication recommendations
        if self._has_auth_issues():
            recommendations.append({
                "category": "authentication",
                "priority": "high",
                "recommendation": "Strengthen authentication mechanisms",
                "impact": "Prevent unauthorized access"
            })
        
        # Authorization recommendations
        if self._has_authz_issues():
            recommendations.append({
                "category": "authorization",
                "priority": "high",
                "recommendation": "Implement proper authorization checks",
                "impact": "Prevent privilege escalation"
            })
        
        # Data protection recommendations
        if self._has_data_protection_issues():
            recommendations.append({
                "category": "data_protection",
                "priority": "high",
                "recommendation": "Enhance data protection measures",
                "impact": "Prevent data breaches"
            })
        
        return recommendations
    
    def _generate_compliance_status(self):
        """Generate compliance status report."""
        return {
            "owasp_top_10": self._check_owasp_compliance(),
            "cwe_top_25": self._check_cwe_compliance(),
            "pci_dss": self._check_pci_compliance(),
            "gdpr": self._check_gdpr_compliance()
        }
    
    def _check_owasp_compliance(self):
        """Check OWASP Top 10 compliance."""
        # TODO: Implement OWASP Top 10 compliance checks
        return {"status": "partial", "issues": []}
    
    def _check_cwe_compliance(self):
        """Check CWE Top 25 compliance."""
        # TODO: Implement CWE Top 25 compliance checks
        return {"status": "partial", "issues": []}
    
    def _check_pci_compliance(self):
        """Check PCI DSS compliance."""
        # TODO: Implement PCI DSS compliance checks
        return {"status": "partial", "issues": []}
    
    def _check_gdpr_compliance(self):
        """Check GDPR compliance."""
        # TODO: Implement GDPR compliance checks
        return {"status": "partial", "issues": []}

def main():
    """Main analyzer entry point."""
    try:
        analyzer = SecurityAnalyzer()
        
        # Load and analyze data
        if not all([
            analyzer.load_security_data(),
            analyzer.analyze_vulnerabilities(),
            analyzer.identify_threats(),
            analyzer.generate_report()
        ]):
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Analysis interrupted", "User interrupted security analysis")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Security analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 