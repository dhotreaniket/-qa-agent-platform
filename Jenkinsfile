pipeline {
    agent any

    triggers {
        cron('H 2 * * *')  // Daily regression run at ~2 AM
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Playwright Dependencies') {
            steps {
                dir('playwright-runner') {
                    bat 'npm install'
                    bat 'npx playwright install --with-deps'
                }
            }
        }

        stage('Run Automation Suite - Practice Test Automation - Login') {
            steps {
                dir('playwright-runner') {
                    bat 'npx playwright test tests/login.spec.js --headed --reporter=list --project=chromium --project=webkit > ..\\test_output.txt 2>&1'
                }
            }
        }

        stage('Generate Report') {
            steps {
                bat 'python generate_report_only.py test_output.txt "Practice Test Automation - Login"'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'playwright-runner/test-results/**, output/execution_report.html, test_output.txt', allowEmptyArchive: true
        }
        failure {
            echo 'Pipeline failed - regression detected.'
        }
    }
}
