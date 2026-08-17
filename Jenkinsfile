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
        withSonarQubeEnv('SonarQube') {
            script {
                def scannerHome = tool 'SonarQube-Scanner'

                sh """
                    ${scannerHome}/bin/sonar-scanner \
                      -Dsonar.projectKey=apple-website-ci-cd \
                      -Dsonar.sources=.
                """
            }
        }
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