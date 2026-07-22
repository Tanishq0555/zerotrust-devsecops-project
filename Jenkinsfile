pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.GIT_COMMIT[0..6]}"
        DOCKERHUB_USER = "atharvahange"
        IMAGE_NAME_BACKEND = "${DOCKERHUB_USER}/ztso-backend"
        IMAGE_NAME_FRONTEND = "${DOCKERHUB_USER}/ztso-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Building commit: ${env.GIT_COMMIT}"
            }
        }

        stage('Gitleaks - Secret Scan') {
            steps {
                sh 'rm -rf .scannerwork'
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
                sh """
                    trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                    trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                """
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                        docker rmi ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        docker rmi ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                        docker image prune -f
                    """
                }
            }
        }

        stage('Cosign - Image Sign') {
            steps {
                withCredentials([
                    file(credentialsId: 'cosign-private-key', variable: 'COSIGN_KEY'),
                    string(credentialsId: 'cosign-password', variable: 'COSIGN_PASSWORD')
                ]) {
                    sh """
                        cosign sign --key $COSIGN_KEY --tlog-upload=false -a "pipeline=jenkins" -a "commit=${IMAGE_TAG}" ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} --yes
                        cosign sign --key $COSIGN_KEY --tlog-upload=false -a "pipeline=jenkins" -a "commit=${IMAGE_TAG}" ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} --yes
                    """
                }
            }
        }

        stage('Helm Deploy') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh "helm upgrade --install ztso ${WORKSPACE}/k8s/helm/ztso --namespace ztso-app --set image.tag=${IMAGE_TAG} --kubeconfig \$KUBECONFIG"
                }
            }
        }

    }

    post {
        success {
            withCredentials([string(credentialsId: 'slack-webhook-jenkins', variable: 'SLACK_WEBHOOK')]) {
                sh "curl -s -X POST -H 'Content-type: application/json' --data '{\"text\":\"✅ Pipeline Passed - Job: ${env.JOB_NAME} Build: ${env.BUILD_NUMBER} Commit: ${IMAGE_TAG}\"}' \$SLACK_WEBHOOK"
            }
            mail(to: 'media.apexmedia@gmail.com', subject: "PASSED - ${env.JOB_NAME} #${env.BUILD_NUMBER}", body: "Pipeline passed. Commit: ${IMAGE_TAG}. View: ${env.BUILD_URL}")
        }
        failure {
            withCredentials([string(credentialsId: 'slack-webhook-jenkins', variable: 'SLACK_WEBHOOK')]) {
                sh "curl -s -X POST -H 'Content-type: application/json' --data '{\"text\":\"🔴 Pipeline Failed - Job: ${env.JOB_NAME} Build: ${env.BUILD_NUMBER} Commit: ${IMAGE_TAG}\"}' \$SLACK_WEBHOOK"
            }
            mail(to: 'media.apexmedia@gmail.com', subject: "FAILED - ${env.JOB_NAME} #${env.BUILD_NUMBER}", body: "Pipeline failed. Commit: ${IMAGE_TAG}. View: ${env.BUILD_URL}")
        }
    }
}

