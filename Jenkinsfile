pipeline {
    agent any
    options {
        skipDefaultCheckout false
    }
    stages{
        /////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("Set up env"){
            when{
                expression{
                    return GIT_BRANCH =~ "feature/*" || GIT_BRANCH =~ "dev"
                }
            }
            steps("Set up env"){
                sh "pipenv install -d"
                sh "echo $GIT_BRANCH"
            }
        }

        /////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("Tests Unitaires"){
            when {
                expression {
                    return GIT_BRANCH =~ "feature/*"
                }
            }
            steps("Execution des tests et realisation de la couverture de tests"){
                sh """
                    rm -f reports/*.xml 
                    rm -f -r reports/coverage_html
                    pipenv run coverage run --include="./**/*.py" --omit="./**/temp_*.py" -m pytest tests/*.py --junitxml=reports/tests.xml
                    pipenv run coverage xml -o reports/coverage.xml && pipenv run coverage html -d reports/coverage_html
                    """
            }
            post {
                always {
                    junit "reports/tests.xml"
                    cobertura (
                        autoUpdateHealth: false,
                        autoUpdateStability: false,
                        coberturaReportFile: 'reports/coverage.xml',
                        lineCoverageTargets: '70, 0, 70',
                        maxNumberOfBuilds: 0, methodCoverageTargets: '70, 0, 70',
                        onlyStable: false,
                        sourceEncoding: 'ASCII',
                        zoomCoverageChart: false)
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'HTML Report',
                        reportTitles: ''])
                }
            }
        }

        ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("Tests Integration"){
            when {
                expression {
                    return GIT_BRANCH =~ "dev" //a Remplacer par dev
                }
            }
            steps("Execution des tests et realisation de la couverture de tests"){
                sh """
                    rm -f reports/*.xml 
                    rm -f -r reports/coverage_html
                    pipenv run coverage run --include="./**/*.py" --omit="./**/temp_*.py" -m pytest tests/*.py --junitxml=reports/tests.xml
                    pipenv run coverage xml -o reports/coverage.xml && pipenv run coverage html -d reports/coverage_html
                    """
            }
            post {
                always {
                    junit "reports/tests.xml"
                    cobertura (
                        autoUpdateHealth: false,
                        autoUpdateStability: false,
                        coberturaReportFile: 'reports/coverage.xml',
                        lineCoverageTargets: '70, 0, 70',
                        maxNumberOfBuilds: 0, methodCoverageTargets: '70, 0, 70',
                        onlyStable: false,
                        sourceEncoding: 'ASCII',
                        zoomCoverageChart: false)
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'HTML Report',
                        reportTitles: ''])
                }
            }
        }

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("Analyse du code"){
            when {
                expression {
                    return GIT_BRANCH =~ "feature/*" || GIT_BRANCH =~ "dev"
                }
            }
            steps("Flake8"){
                sh """
                    pipenv run flake8 --exit-zero > ./reports/flake8.report
                    """
            }
            post{
                always{
                    recordIssues(
                        tool: flake8(pattern: 'reports/flake8.report'),
                        //tool: [pyLint(pattern: "reports/pylint.report"), pyDocStyle(pattern: "backend/reports/pylint.report")],
                        //unstableTotalAll: 20,
                        //failedTotalAll: 30,
                        //aggregatingResults: true
                    )
                    /*recordIssues(
                        tool: pyDocStyle(pattern: "reports/pylint.report"),
                        unstableTotalAll: 20,
                        failedTotalAll: 30,
                        aggregatingResults: true
                    )*/
                }
            }    
        }

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("Formatage du code"){
            when{
                expression{
                    return GIT_BRANCH =~ "feature/*" || GIT_BRANCH =~ "dev"
                }
            }
            steps("Application de black (?)"){
                sh "pipenv run black  **/*.py"
            }
        }

        ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("SonarQube analysis") {
            when {
                expression{
                    return GIT_BRANCH =~ "dev"
                }
            }
            environment {
                scannerHome = tool 'SonarQubeScanner' 
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh "ls reports/"
                    sh "${scannerHome}/bin/sonar-scanner -X"
                }
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true 
                }
            }
        }

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("DEPLOY dev") {
            when {
                expression{
                    return GIT_BRANCH =~ "dev"
                }
            }
            steps("Deploy to distant server") {
                sh '''
                    ssh root@192.168.101.14 'rm -rf /root/backend/*';
                    scp -r -p $WORKSPACE/* root@192.168.101.14:/root/backend/;
                    ssh root@192.168.101.14 'cp /root/pic_settings.py /root/backend/openCMMS/';
                    ssh root@192.168.101.14 'cp /root/file1.py /root/backend/utils/data_providers/';
                    ssh root@192.168.101.14 'cp /root/file2.py /root/backend/utils/data_providers/';
                    ssh root@192.168.101.14 systemctl restart gunicorn.service 
                '''
            }
        }




        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        stage("DEPLOY") {
            when {
                expression{
                    return GIT_BRANCH =~ "master"
                }
            }
            steps("Deploy to distant server") {
                sh '''
                    ssh root@192.168.101.9 'rm -rf /root/backend/*';
                    scp -r -p $WORKSPACE/* root@192.168.101.9:/root/backend/;
                    ssh root@192.168.101.9 'cp /root/pic_settings.py /root/backend/openCMMS/';
                    ssh root@192.168.101.9 'cp /root/file1.py /root/backend/utils/data_providers/';
                    ssh root@192.168.101.9 'cp /root/file2.py /root/backend/utils/data_providers/';
                    ssh root@192.168.101.9 systemctl restart gunicorn.service 
                '''
            }
        }
    }
}