def generate_jenkinsfile(runner_dir: str, test_command: str, app_name: str) -> str:
    return f"""pipeline {{
    agent any

    triggers {{
        cron('H 2 * * *')  // Daily regression run at ~2 AM
    }}

    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}

        stage('Install Playwright Dependencies') {{
            steps {{
                dir('{runner_dir}') {{
                    bat 'npm install'
                    bat 'npx playwright install --with-deps'
                }}
            }}
        }}

        stage('Run Automation Suite - {app_name}') {{
            steps {{
                dir('{runner_dir}') {{
                    bat '{test_command} > ..\\\\test_output.txt 2>&1'
                }}
            }}
        }}

        stage('Generate Report') {{
            steps {{
                bat 'python generate_report_only.py test_output.txt "{app_name}"'
            }}
        }}
    }}

    post {{
        always {{
            archiveArtifacts artifacts: '{runner_dir}/test-results/**, output/execution_report.html, test_output.txt', allowEmptyArchive: true
        }}
        failure {{
            echo 'Pipeline failed - regression detected.'
        }}
    }}
}}
"""