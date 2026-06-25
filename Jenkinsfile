pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.GIT_COMMIT[0..6]}"
        DOCKERHUB_USER = "atharvahange03"
        IMAGE_NAME_BACKEND = "${DOCKERHUB_USER}/ztso-backend"
        IMAGE_NAME_FRONTEND = "${DOCKERHUB_USER}/ztso-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Building commit: ${env.GIT_COMMIT}"
            }
        }

	stage('Gitleaks - Secret Scan') {
	    steps {
		sh 'gitleaks detect --source . --verbose'
	    }
	}

        stage('SonarQube - SAST') {
            steps {
                echo 'Running SonarQube scan...'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker images...'
            }
        }

        stage('Trivy - Image Scan') {
            steps {
                echo 'Running Trivy scan...'
            }
        }

        stage('Docker Push') {
            steps {
                echo 'Pushing images to DockerHub...'
            }
        }

        stage('Cosign - Image Sign') {
            steps {
                echo 'Signing images...'
            }
        }

        stage('Helm Deploy') {
            steps {
                echo 'Deploying to k3s...'
            }
        }

    }

    post {
        success {
            echo 'Pipeline passed successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}
