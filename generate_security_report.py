import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

def generate_security_report():
    """Generate weekly security report"""
    
    report = {
        "generated": datetime.now().isoformat(),
        "period": "weekly",
        "summary": {
            "total_requests": 0,
            "blocked_requests": 0,
            "vulnerability_scans": 0,
            "security_audits": 0
        },
        "recommendations": []
    }
    
    # Load WAF logs
    try:
        with open("waf_logs.json", "r") as f:
            waf_logs = json.load(f)
            report["summary"]["total_requests"] = len(waf_logs)
            report["summary"]["blocked_requests"] = len([l for l in waf_logs if l.get("blocked")])
    except:
        pass
    
    # Load security audit results
    try:
        import glob
        audit_files = glob.glob("security_audit_*.json")
        report["summary"]["security_audits"] = len(audit_files)
        
        if audit_files:
            latest_audit = max(audit_files)
            with open(latest_audit, "r") as f:
                audit = json.load(f)
                report["audit_score"] = audit.get("score", 0)
    except:
        pass
    
    # Generate recommendations
    if report["summary"]["blocked_requests"] > 100:
        report["recommendations"].append("High number of blocked requests - consider reviewing firewall rules")
    
    if report.get("audit_score", 100) < 80:
        report["recommendations"].append("Security audit score low - review and fix issues")
    
    # Save report
    report_file = f"security_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f" Security report generated: {report_file}")
    print(f" Security Score: {report.get('audit_score', 'N/A')}%")
    print(f" Blocked Requests: {report['summary']['blocked_requests']}")
    print(f" Recommendations: {len(report['recommendations'])}")
    
    return report

if __name__ == "__main__":
    generate_security_report()
