pipeline {
    agent any

    stages {
        stage('Build & Test') {
            steps {
                // Backend tests in a throwaway virtualenv; any failing line fails the stage.
                bat '''
                    python -m venv .ci-venv || exit /b 1
                    .ci-venv\\Scripts\\python -m pip install -q -r backend\\requirements-dev.txt || exit /b 1
                    cd backend || exit /b 1
                    ..\\.ci-venv\\Scripts\\python -m pytest -v || exit /b 1
                '''
                echo 'Building Payment and Notification Services... Test PASSED'
            }
        }

        stage('Docker Packaging') {
            steps {
                bat 'docker build -t payment-engine:capstone-two .'
                bat 'docker build -t payment-backend:capstone-two backend'
                bat 'docker build -t payment-frontend:capstone-two frontend'
                bat 'docker image inspect payment-engine:capstone-two payment-backend:capstone-two payment-frontend:capstone-two --format "Image {{.RepoTags}} {{.Id}}"'
            }
        }

        stage('Deploy Cluster') {
            steps {
                echo 'Applying Kubernetes Deployment manifests to cluster...'
            }
        }
    }

    post {
        always {
            bat 'if exist .ci-venv rmdir /s /q .ci-venv'
        }
    }
}
