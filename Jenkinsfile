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
                        cosign sign --key $COSIGN_KEY \
                            --tlog-upload=false \
                            -a "pipeline=jenkins" \
                            -a "commit=${IMAGE_TAG}" \
                            ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} --yes
                        cosign sign --key $COSIGN_KEY \
                            --tlog-upload=false \
                            -a "pipeline=jenkins" \
                            -a "commit=${IMAGE_TAG}" \
                            ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} --yes
                    """
                }
            }
        }

        stage('Helm Deploy') {
            steps {
                withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_CONTENT')]) {
                    sh """
                        echo "${KUBECONFIG_CONTENT}" > /tmp/kubeconfig-jenkins
                        helm upgrade --install ztso ${WORKSPACE}/k8s/helm/ztso \
                          --namespace ztso-app \
                          --set image.tag=${IMAGE_TAG} \
                          --kubeconfig /tmp/kubeconfig-jenkins
                        rm -f /tmp/kubeconfig-jenkins
                    """
                }
            }
        }

    }

	stage('Helm Deploy') {
	     steps {
		withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_CONTENT')]) {
            	    script {
                	writeFile file: '/tmp/kubeconfig-jenkins', text: KUBECONFIG_CONTENT
            		}
            	sh """
                	helm upgrade --install ztso ${WORKSPACE}/k8s/helm/ztso \
                 	 --namespace ztso-app \
                  	--set image.tag=${IMAGE_TAG} \
                  	--kubeconfig /tmp/kubeconfig-jenkins
                	rm -f /tmp/kubeconfig-jenkins
            	   """
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
