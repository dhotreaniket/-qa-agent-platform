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

        stage('Install Dependencies') {
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
                    bat 'npx playwright test tests/login.spec.js --headed --reporter=list'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'playwright-runner/test-results/**', allowEmptyArchive: true
            publishHTML(target: [
                reportDir: 'output',
                reportFiles: 'execution_report.html',
                reportName: 'QA Automation Report'
            ])
        }
        failure {
            echo 'Pipeline failed - regression detected.'
        }
    }
}
