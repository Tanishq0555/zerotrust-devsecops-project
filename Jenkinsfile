pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code checked out successfully'
            }
        }
    }

    post {
        success {
            echo 'Pipeline passed'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}
