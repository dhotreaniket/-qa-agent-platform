import re
from datetime import datetime


def parse_test_results(diagnostic_output: str) -> dict:
    """Parses Playwright's --reporter=list output into structured pass/fail data."""
    lines = diagnostic_output.splitlines()
    test_results = []

    for line in lines:
        match = re.search(r"(ok|✓|✗|failed)\s+\d+\s+\[(\w+)\].*?›\s*(.+?)\s*\((\d+\.?\d*s)\)", line, re.IGNORECASE)
        if match:
            status_raw, browser, test_name, duration = match.groups()
            status = "PASS" if status_raw.lower() in ("ok", "✓") else "FAIL"
            test_results.append({
                "name": test_name.strip(),
                "browser": browser,
                "status": status,
                "duration": duration
            })

    summary_match = re.search(r"(\d+)\s+passed.*?(\d+)?\s*(?:failed)?", diagnostic_output)
    total_passed = int(summary_match.group(1)) if summary_match else sum(1 for t in test_results if t["status"] == "PASS")
    total_failed = sum(1 for t in test_results if t["status"] == "FAIL")

    return {
        "tests": test_results,
        "total": len(test_results),
        "passed": total_passed,
        "failed": total_failed,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_html_report(parsed_results: dict, app_name: str) -> str:
    rows = ""
    for test in parsed_results["tests"]:
        status_color = "#28a745" if test["status"] == "PASS" else "#dc3545"
        rows += f"""
        <tr>
            <td>{test['name']}</td>
            <td>{test['browser']}</td>
            <td style="color:{status_color}; font-weight:bold;">{test['status']}</td>
            <td>{test['duration']}</td>
        </tr>"""

    pass_rate = round((parsed_results["passed"] / parsed_results["total"]) * 100, 1) if parsed_results["total"] else 0

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report - {app_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary span {{ font-size: 28px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }}
        th {{ background: #343a40; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
    </style>
</head>
<body>
    <h1>Test Execution Report</h1>
    <p><strong>Application:</strong> {app_name} &nbsp;|&nbsp; <strong>Run at:</strong> {parsed_results['timestamp']}</p>
    <div class="summary">
        <span style="color:#28a745;">{parsed_results['passed']} passed</span> &nbsp;&nbsp;
        <span style="color:#dc3545;">{parsed_results['failed']} failed</span> &nbsp;&nbsp;
        <span>{pass_rate}% pass rate</span>
    </div>
    <table>
        <tr><th>Test Case</th><th>Browser</th><th>Status</th><th>Duration</th></tr>
        {rows}
    </table>
</body>
</html>"""
    return html