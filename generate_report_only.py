import sys
import os
from agents.report_generator import parse_test_results, generate_html_report


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_report_only.py <test_output_file> <app_name>")
        sys.exit(1)

    test_output_path = sys.argv[1]
    app_name = sys.argv[2]

    with open(test_output_path, "r", encoding="utf-8") as f:
        test_output = f.read()

    parsed_results = parse_test_results(test_output)
    html_report = generate_html_report(parsed_results, app_name)

    os.makedirs("output", exist_ok=True)
    with open("output/execution_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"Report generated: {parsed_results['passed']} passed, {parsed_results['failed']} failed")


if __name__ == "__main__":
    main()