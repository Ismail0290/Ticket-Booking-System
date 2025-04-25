pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_VERSION = '2.15.1'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                docker-compose run --rm web python manage.py test
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                docker-compose down
                docker-compose up -d
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose logs web > web_logs.txt'
            archiveArtifacts artifacts: 'web_logs.txt', allowEmptyArchive: true
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
