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
		sh 'gitleaks detect --source . --no-git --verbose'
	    }
	}


	stage('SonarQube - SAST') {
	    steps {
		withSonarQubeEnv('sonarqube') {
		sh "${tool 'sonarqube-scanner'}/bin/sonar-scanner"
			}
		}
	}
	
	stage('Quality Gate') {
	    steps {
		timeout(time: 5, unit: 'MINUTES') {
		waitForQualityGate abortPipeline: true
			}
		}
	}	
	
	

        stage('Docker Build') {
            steps {
                sh """
            docker build -t ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} ./backend
            docker build -t ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} ./frontend
        """
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
