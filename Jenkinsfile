pipeline {
  agent any

  environment {
    scannerHome = tool 'sonar-scanner'
    SONAR_URL   = "http://192.168.135.146:9000"
    DD_URL      = "http://192.168.135.145:8080"
    PROJECT_KEY = "juice-shop"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('SonarQube Scan') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh "${scannerHome}/bin/sonar-scanner || true"
        }
      }
    }

    stage('Export Sonar Results') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'SONAR_CREDS', usernameVariable: 'SONAR_USER', passwordVariable: 'SONAR_PASS')]) {
          sh '''
            curl -f -u "$SONAR_USER:$SONAR_PASS" \
              "$SONAR_URL/api/issues/search?componentKeys=$PROJECT_KEY&ps=500" \
              -o sonar-report.json || true
          '''
        }
      }
    }

    stage('Import Sonar Results to DefectDojo') {
      steps {
        withCredentials([string(credentialsId: 'DD_API_KEY', variable: 'DD_API')]) {
          sh '''
            DD_URL="$DD_URL" \
            DD_API_KEY="$DD_API" \
            python3 defectdojo-upload-sonar.py sonar-report.json || true
          '''
        }
      }
    }

    stage('Secret Scan - Gitleaks') {
      steps {
        sh '''
          mkdir -p reports
          gitleaks detect --source . --report-path reports/gitleaks-report.json --report-format json || true
        '''
      }
    }

    stage('Upload GitLeaks Results to DefectDojo') {
      steps {
        withCredentials([string(credentialsId: 'DD_API_KEY', variable: 'DD_API')]) {
          sh '''
            DD_URL="$DD_URL" \
            DD_API_KEY="$DD_API" \
            python3 defectdojo-upload-gitleaks.py reports/gitleaks-report.json || true
          '''
        }
      }
    }

    stage('SCA - Trivy FS Scan') {
      steps {
        sh 'trivy fs . --format json --output trivy-report.json || true'
      }
    }

    stage('Upload Trivy FS Results to DefectDojo') {
      steps {
        withCredentials([string(credentialsId: 'DD_API_KEY', variable: 'DD_API')]) {
          sh '''
            DD_URL="$DD_URL" \
            DD_API_KEY="$DD_API" \
            python3 defectdojo-upload-trivy.py trivy-report.json || true
          '''
        }
      }
    }  

    stage('Build Docker Image') {
      steps {
        sh '''
          NODE_OPTIONS="--max_old_space_size=4096" \
          docker build -t juice-shop:${BUILD_NUMBER} . || true
        '''
      }
    }

    stage('Container Image Scan - Trivy') { 
      steps { 
        sh 'trivy image --format json --output trivy-image-report.json juice-shop:${BUILD_NUMBER} || true' 
        sh 'ls -lh trivy-image-report.json' 
      } 
    } 
    
    stage('Upload Trivy Image Results to DefectDojo') { 
      steps { 
        withCredentials([string(credentialsId: 'DD_API_KEY', variable: 'DD_API')]) { 
          sh '''
            DD_URL="$DD_URL" \
            DD_API_KEY="$DD_API" \
            python3 defectdojo-upload-trivy-docker.py trivy-image-report.json || true 
          '''
          } 
        } 
      }

    stage('Run Juice Shop Locally') {
      steps {
        sh '''
          docker stop juice-shop || true
          docker rm -f juice-shop || true
          docker run -d --name juice-shop -p 3000:3000 juice-shop:${BUILD_NUMBER}
          sleep 15
        '''
      }
    }

    stage('Verify Juice Shop is Reachable') {
      steps {
        sh '''
          curl -I http://localhost:3000 || exit 1
        '''
      }
    }

    stage('DAST Scan with OWASP ZAP') {
      steps {
        sh '''
          mkdir -p zap-reports
          pwd
          sleep 10
          docker run --rm --user 0 \
          --add-host=host.docker.internal:host-gateway \
          -v $(pwd)/zap-reports:/zap/wrk:rw \
          ghcr.io/zaproxy/zaproxy:stable \
          zap-full-scan.py \
          -t http://host.docker.internal:3000 \
          -r zap-report.html \
          -J zap-results.json \
          -x zap-results.xml \
          -d || true
        '''
        sh 'ls -lh zap-reports'
        sh 'pwd'
      }
    }

    stage('Upload ZAP Results to DefectDojo') {
      steps {
        withCredentials([string(credentialsId: 'DD_API_KEY', variable: 'DD_API')]) {
          sh '''
            DD_URL="$DD_URL" \
            DD_API_KEY="$DD_API" \
            python3 defectdojo-upload-zap.py zap-reports/zap-results.xml || true
          '''
        }
      }
    }
  }
}
