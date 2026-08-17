pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/Akshat250324/Apple-Website-DevOps.git'
            }
        }

        stage('SonarQube Analysis') {
    steps {
        script {
            def scannerHome = tool 'SonarQube-Scanner'

            echo "Scanner Home: ${scannerHome}"

            sh "ls -lah ${scannerHome}"
            sh "ls -lah ${scannerHome}/bin"
            sh "${scannerHome}/bin/sonar-scanner --version"
        }
    }
}

        stage('Docker Build') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Test') {
            steps {
                sh 'docker compose run --rm web python manage.py check'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose down
                    docker compose up -d
                '''
            }
        }

        stage('Verify') {
            steps {
                sh 'docker compose ps'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Waiting for application..."
                    sleep 10
                    curl -f http://localhost:8080/
                '''
            }
        }
    }
}