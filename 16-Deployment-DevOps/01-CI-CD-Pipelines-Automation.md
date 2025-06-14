# CI/CD Pipelines & Automation

## Table of Contents
1. [CI/CD Fundamentals](#cicd-fundamentals)
2. [GitHub Actions Workflows](#github-actions-workflows)
3. [GitLab CI/CD](#gitlab-cicd)
4. [Jenkins Pipeline](#jenkins-pipeline)
5. [Azure DevOps](#azure-devops)
6. [Deployment Strategies](#deployment-strategies)
7. [Environment Management](#environment-management)
8. [Quality Gates & Testing](#quality-gates--testing)

## CI/CD Fundamentals

### Pipeline Architecture
```yaml
{% raw %}
{% raw %}
# CI/CD Pipeline Structure
stages:
  - build
  - test
  - security
  - quality
  - deploy
  - monitor

# Pipeline Configuration Template
pipeline:
  triggers:
    - push: [main, develop]
    - pull_request: [main]
    - schedule: "0 2 * * *"  # Nightly builds
    
  variables:
    NODE_VERSION: "18.x"
    CACHE_KEY: "node-modules-${{ hashFiles('**/package-lock.json') }}"
    
  stages:
    build:
      - install_dependencies
      - compile_application
      - generate_artifacts
      
    test:
      - unit_tests
      - integration_tests
      - e2e_tests
      - visual_regression_tests
      
    security:
      - dependency_audit
      - security_scan
      - license_check
      
    quality:
      - lint_check
      - type_check
      - code_coverage
      - performance_budget
      
    deploy:
      - staging_deployment
      - production_deployment
      - rollback_capability
      
    monitor:
      - deployment_verification
      - performance_monitoring
      - alert_setup
{% endraw %}
{% endraw %}
```

### Environment Configuration
```typescript
// config/environments.ts
export interface EnvironmentConfig {
  name: string;
  apiUrl: string;
  cdnUrl: string;
  features: Record<string, boolean>;
  analytics: {
    googleAnalyticsId?: string;
    sentryDsn?: string;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
  performance: {
    enableServiceWorker: boolean;
    enableCodeSplitting: boolean;
    maxBundleSize: number;
  };
}

export const environments: Record<string, EnvironmentConfig> = {
  development: {
    name: 'development',
    apiUrl: 'http://localhost:3001/api',
    cdnUrl: 'http://localhost:3000',
    features: {
      debugMode: true,
      mockData: true,
      experimentalFeatures: true
    },
    analytics: {
      logLevel: 'debug'
    },
    performance: {
      enableServiceWorker: false,
      enableCodeSplitting: true,
      maxBundleSize: 5000000 // 5MB for dev
    }
  },
  
  staging: {
    name: 'staging',
    apiUrl: 'https://api-staging.example.com/api',
    cdnUrl: 'https://cdn-staging.example.com',
    features: {
      debugMode: true,
      mockData: false,
      experimentalFeatures: true
    },
    analytics: {
      googleAnalyticsId: 'GA-STAGING-ID',
      sentryDsn: 'https://staging-sentry-dsn@sentry.io/project',
      logLevel: 'info'
    },
    performance: {
      enableServiceWorker: true,
      enableCodeSplitting: true,
      maxBundleSize: 2000000 // 2MB
    }
  },
  
  production: {
    name: 'production',
    apiUrl: 'https://api.example.com/api',
    cdnUrl: 'https://cdn.example.com',
    features: {
      debugMode: false,
      mockData: false,
      experimentalFeatures: false
    },
    analytics: {
      googleAnalyticsId: 'GA-PROD-ID',
      sentryDsn: 'https://prod-sentry-dsn@sentry.io/project',
      logLevel: 'error'
    },
    performance: {
      enableServiceWorker: true,
      enableCodeSplitting: true,
      maxBundleSize: 1000000 // 1MB
    }
  }
};

export const getCurrentEnvironment = (): EnvironmentConfig => {
  const env = process.env.NODE_ENV || 'development';
  return environments[env] || environments.development;
};
```

## GitHub Actions Workflows

### Complete Production Workflow
```yaml
{% raw %}
{% raw %}
# .github/workflows/production.yml
name: Production Deployment

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18.x'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      cache-key: ${{ steps.cache-key.outputs.key }}
      should-deploy: ${{ steps.changes.outputs.should-deploy }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate cache key
        id: cache-key
        run: echo "key=node-modules-${{ hashFiles('**/package-lock.json') }}" >> $GITHUB_OUTPUT
      
      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet HEAD~1 HEAD -- src/ public/ package.json; then
            echo "should-deploy=false" >> $GITHUB_OUTPUT
          else
            echo "should-deploy=true" >> $GITHUB_OUTPUT
          fi

  install:
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ needs.setup.outputs.cache-key }}
          restore-keys: |
            node-modules-
      
      - name: Install dependencies
        run: |
          npm ci --only=production=false
          npm audit --audit-level=moderate

  build:
    runs-on: ubuntu-latest
    needs: [setup, install]
    strategy:
      matrix:
        environment: [staging, production]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Restore node modules
        uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ needs.setup.outputs.cache-key }}
      
      - name: Build application
        run: npm run build
        env:
          NODE_ENV: ${{ matrix.environment }}
          REACT_APP_VERSION: ${{ github.sha }}
          REACT_APP_BUILD_TIME: ${{ github.run_number }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-${{ matrix.environment }}
          path: dist/
          retention-days: 30

  test:
    runs-on: ubuntu-latest
    needs: [setup, install]
    strategy:
      matrix:
        test-type: [unit, integration, e2e]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Restore node modules
        uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ needs.setup.outputs.cache-key }}
      
      - name: Run unit tests
        if: matrix.test-type == 'unit'
        run: |
          npm run test:unit -- --coverage --watchAll=false
          npm run test:coverage-report
      
      - name: Run integration tests
        if: matrix.test-type == 'integration'
        run: npm run test:integration
      
      - name: Run E2E tests
        if: matrix.test-type == 'e2e'
        run: |
          npm run build
          npm run start:test &
          sleep 30
          npm run test:e2e
          pkill -f "serve"
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.test-type }}
          path: |
            coverage/
            test-results/
            playwright-report/

  security:
    runs-on: ubuntu-latest
    needs: [setup, install]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Restore node modules
        uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ needs.setup.outputs.cache-key }}
      
      - name: Security audit
        run: |
          npm audit --audit-level=moderate
          npx audit-ci --moderate
      
      - name: License check
        run: npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC'
      
      - name: SAST scan
        uses: github/super-linter@v4
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          JAVASCRIPT_ES_CONFIG_FILE: .eslintrc.js
          VALIDATE_JAVASCRIPT_ES: true
          VALIDATE_TYPESCRIPT_ES: true
      
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: javascript

  quality:
    runs-on: ubuntu-latest
    needs: [setup, install]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Restore node modules
        uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ needs.setup.outputs.cache-key }}
      
      - name: Lint check
        run: |
          npm run lint
          npm run lint:css
      
      - name: Type check
        run: npm run type-check
      
      - name: Format check
        run: npm run format:check
      
      - name: Build size check
        run: |
          npm run build
          npm run bundle-analyzer
          npm run size-check

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [build, test, security, quality]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-staging
          path: dist/
      
      - name: Deploy to Staging
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
          cname: staging.example.com
      
      - name: Run staging tests
        run: |
          sleep 60 # Wait for deployment
          npm run test:staging
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    runs-on: ubuntu-latest
    needs: [deploy-staging]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-production
          path: dist/
      
      - name: Deploy to Production
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
          cname: example.com
      
      - name: Verify deployment
        run: |
          sleep 60
          npm run test:production
          npm run lighthouse:ci
      
      - name: Create GitHub release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
          body: |
            Automated release from commit ${{ github.sha }}
            
            ## Changes
            ${{ github.event.head_commit.message }}
          draft: false
          prerelease: false

  monitor:
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: always()
    steps:
      - name: Health check
        run: |
          curl -f https://example.com/health || exit 1
      
      - name: Performance check
        run: |
          npx @lhci/cli@0.12.x autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
      
      - name: Update monitoring
        run: |
          curl -X POST "${{ secrets.MONITORING_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d '{"deployment": "success", "version": "${{ github.sha }}", "environment": "production"}'
{% endraw %}
{% endraw %}
```

### Feature Branch Workflow
```yaml
{% raw %}
{% raw %}
# .github/workflows/feature.yml
name: Feature Branch

on:
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint and format check
        run: |
          npm run lint
          npm run format:check
      
      - name: Type check
        run: npm run type-check
      
      - name: Run tests
        run: npm run test -- --coverage --watchAll=false
      
      - name: Build application
        run: npm run build
      
      - name: Visual regression tests
        run: npm run test:visual
      
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const coverage = JSON.parse(fs.readFileSync('coverage/coverage-summary.json'));
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🚀 Build Results
              
              ✅ All checks passed!
              
              **Test Coverage:**
              - Lines: ${coverage.total.lines.pct}%
              - Functions: ${coverage.total.functions.pct}%
              - Branches: ${coverage.total.branches.pct}%
              - Statements: ${coverage.total.statements.pct}%
              
              **Bundle Size:** ![Bundle Size](https://img.shields.io/badge/Bundle-${process.env.BUNDLE_SIZE || 'Unknown'}-green)
              `
            });
{% endraw %}
{% endraw %}
```

## GitLab CI/CD

### Complete GitLab Pipeline
```yaml
# .gitlab-ci.yml
image: node:18-alpine

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"
  CYPRESS_CACHE_FOLDER: "$CI_PROJECT_DIR/cache/Cypress"

cache:
  paths:
    - .npm/
    - cache/Cypress/
    - node_modules/

stages:
  - install
  - build
  - test
  - security
  - deploy
  - monitor

install_dependencies:
  stage: install
  script:
    - npm ci --cache .npm --prefer-offline
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

build:
  stage: build
  needs: [install_dependencies]
  parallel:
    matrix:
      - ENVIRONMENT: [staging, production]
  script:
    - npm run build
    - echo "Build completed for $ENVIRONMENT"
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
    name: "build-$ENVIRONMENT-$CI_COMMIT_SHORT_SHA"
  environment:
    name: $ENVIRONMENT
  only:
    - main
    - develop

test:unit:
  stage: test
  needs: [install_dependencies]
  script:
    - npm run test:unit -- --coverage --watchAll=false
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
      junit: junit.xml
    paths:
      - coverage/
    expire_in: 1 week

test:integration:
  stage: test
  needs: [install_dependencies]
  script:
    - npm run test:integration
  artifacts:
    reports:
      junit: test-results/integration/junit.xml
    paths:
      - test-results/
    expire_in: 1 week

test:e2e:
  stage: test
  needs: [build]
  services:
    - name: cypress/included:latest
      alias: cypress
  script:
    - npm run build
    - npm run start:test &
    - sleep 30
    - npm run test:e2e:ci
  artifacts:
    when: always
    paths:
      - cypress/videos/
      - cypress/screenshots/
    expire_in: 1 week

security:audit:
  stage: security
  needs: [install_dependencies]
  script:
    - npm audit --audit-level moderate
    - npx audit-ci --moderate
  allow_failure: false

security:sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

security:dependency_scanning:
  stage: security
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml

security:license:
  stage: security
  needs: [install_dependencies]
  script:
    - npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC'

deploy:staging:
  stage: deploy
  needs: [build, test:unit, test:integration, security:audit]
  script:
    - echo "Deploying to staging environment"
    - npm run deploy:staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy:production:
  stage: deploy
  needs: [deploy:staging, test:e2e]
  script:
    - echo "Deploying to production environment"
    - npm run deploy:production
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main

pages:
  stage: deploy
  needs: [build]
  script:
    - mkdir public
    - cp -r dist/* public/
  artifacts:
    paths:
      - public
  only:
    - main

monitor:lighthouse:
  stage: monitor
  needs: [deploy:production]
  image: circleci/node:14-browsers
  script:
    - npm install -g @lhci/cli
    - lhci autorun
  artifacts:
    reports:
      performance: lhci_reports/manifest.json
  only:
    - main

monitor:health:
  stage: monitor
  needs: [deploy:production]
  script:
    - |
      for i in {1..5}; do
        if curl -f https://example.com/health; then
          echo "Health check passed"
          exit 0
        fi
        sleep 10
      done
      echo "Health check failed"
      exit 1
  only:
    - main
```

## Jenkins Pipeline

### Declarative Pipeline
```groovy
{% raw %}
{% raw %}
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        NODE_VERSION = '18'
        REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'react-app'
        KUBECONFIG = credentials('kubeconfig')
    }
    
    tools {
        nodejs "${NODE_VERSION}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                    env.BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        npm ci
                        npm audit --audit-level moderate
                    '''
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'reports',
                            reportFiles: 'eslint-report.html',
                            reportName: 'ESLint Report'
                        ])
                    }
                }
                
                stage('Type Check') {
                    steps {
                        sh 'npm run type-check'
                    }
                }
                
                stage('Format Check') {
                    steps {
                        sh 'npm run format:check'
                    }
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit -- --coverage --watchAll=false'
                        publishTestResults testResultsPattern: 'junit.xml'
                        publishCoverage adapters: [
                            istanbulCoberturaAdapter('coverage/cobertura-coverage.xml')
                        ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        sh 'npm run test:integration'
                        publishTestResults testResultsPattern: 'test-results/integration/junit.xml'
                    }
                }
            }
        }
        
        stage('Security Scan') {
            parallel {
                stage('Dependency Audit') {
                    steps {
                        sh 'npx audit-ci --moderate'
                    }
                }
                
                stage('SAST Scan') {
                    steps {
                        sh 'npx eslint-security-scanner src/'
                    }
                }
                
                stage('License Check') {
                    steps {
                        sh 'npx license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"'
                    }
                }
            }
        }
        
        stage('Build') {
            parallel {
                stage('Build Staging') {
                    steps {
                        sh '''
                            NODE_ENV=staging npm run build
                            tar -czf build-staging-${BUILD_VERSION}.tar.gz dist/
                        '''
                        archiveArtifacts artifacts: 'build-staging-*.tar.gz', fingerprint: true
                    }
                }
                
                stage('Build Production') {
                    when {
                        branch 'main'
                    }
                    steps {
                        sh '''
                            NODE_ENV=production npm run build
                            tar -czf build-production-${BUILD_VERSION}.tar.gz dist/
                        '''
                        archiveArtifacts artifacts: 'build-production-*.tar.gz', fingerprint: true
                    }
                }
            }
        }
        
        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def image = docker.build("${REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}")
                    docker.withRegistry("https://${REGISTRY}", 'registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('E2E Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    docker run -d --name test-app -p 3000:80 ${REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}
                    sleep 30
                    npm run test:e2e:ci
                    docker stop test-app
                    docker rm test-app
                '''
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'playwright-report',
                    reportFiles: 'index.html',
                    reportName: 'Playwright Report'
                ])
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh '''
                        helm upgrade --install react-app-staging ./helm-chart \
                            --set image.tag=${BUILD_VERSION} \
                            --set environment=staging \
                            --namespace staging
                    '''
                }
            }
        }
        
        stage('Staging Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    sleep 60
                    npm run test:staging
                    npx lighthouse-ci autorun --config=lighthouse-staging.json
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                allOf {
                    branch 'main'
                    expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
                }
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(name: 'DEPLOYMENT_STRATEGY', choices: ['rolling', 'blue-green', 'canary'], description: 'Deployment strategy')
                }
            }
            steps {
                script {
                    sh '''
                        helm upgrade --install react-app-production ./helm-chart \
                            --set image.tag=${BUILD_VERSION} \
                            --set environment=production \
                            --set deploymentStrategy=${DEPLOYMENT_STRATEGY} \
                            --namespace production
                    '''
                }
            }
        }
        
        stage('Production Verification') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    sleep 120
                    npm run test:production
                    npx lighthouse-ci autorun --config=lighthouse-production.json
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: ":white_check_mark: Deployment successful for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
        
        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: ":x: Deployment failed for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
        
        unstable {
            slackSend(
                channel: '#deployments',
                color: 'warning',
                message: ":warning: Deployment unstable for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
    }
}
{% endraw %}
{% endraw %}
```

## Azure DevOps

### Azure Pipelines Configuration
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - src/*
      - public/*
      - package.json

pr:
  branches:
    include:
      - main
      - develop

variables:
  - group: react-app-variables
  - name: nodeVersion
    value: '18.x'
  - name: buildConfiguration
    value: 'production'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildAndTest
    displayName: 'Build and Test'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: NodeTool@0
      displayName: 'Install Node.js'
      inputs:
        versionSpec: $(nodeVersion)
    
    - task: Cache@2
      displayName: 'Cache npm packages'
      inputs:
        key: 'npm | "$(Agent.OS)" | package-lock.json'
        restoreKeys: |
          npm | "$(Agent.OS)"
        path: $(npm_config_cache)
    
    - script: |
        npm ci
        npm audit --audit-level moderate
      displayName: 'Install dependencies'
    
    - script: |
        npm run lint
        npm run type-check
        npm run format:check
      displayName: 'Code quality checks'
    
    - script: |
        npm run test:unit -- --coverage --watchAll=false
      displayName: 'Run unit tests'
    
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'junit.xml'
        mergeTestResults: true
    
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish coverage results'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage/cobertura-coverage.xml'
        reportDirectory: 'coverage'
    
    - script: |
        npm run build
      displayName: 'Build application'
      env:
        NODE_ENV: $(buildConfiguration)
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish build artifacts'
      inputs:
        pathToPublish: 'dist'
        artifactName: 'build'

- stage: SecurityScan
  displayName: 'Security Scanning'
  dependsOn: Build
  jobs:
  - job: SecurityScan
    displayName: 'Security Scan'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
    
    - script: npm ci
      displayName: 'Install dependencies'
    
    - script: |
        npx audit-ci --moderate
        npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC'
      displayName: 'Security and license checks'

- stage: Deploy
  displayName: 'Deploy to Staging'
  dependsOn: [Build, SecurityScan]
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployStaging
    displayName: 'Deploy to Staging'
    environment: 'staging'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadBuildArtifacts@0
            inputs:
              artifactName: 'build'
              downloadPath: '$(System.ArtifactsDirectory)'
          
          - task: AzureStaticWebApp@0
            inputs:
              app_location: '$(System.ArtifactsDirectory)/build'
              azure_static_web_apps_api_token: '$(AZURE_STATIC_WEB_APPS_API_TOKEN_STAGING)'

- stage: ProductionDeploy
  displayName: 'Deploy to Production'
  dependsOn: Deploy
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployProduction
    displayName: 'Deploy to Production'
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadBuildArtifacts@0
            inputs:
              artifactName: 'build'
              downloadPath: '$(System.ArtifactsDirectory)'
          
          - task: AzureStaticWebApp@0
            inputs:
              app_location: '$(System.ArtifactsDirectory)/build'
              azure_static_web_apps_api_token: '$(AZURE_STATIC_WEB_APPS_API_TOKEN_PRODUCTION)'
```

## Deployment Strategies

### Blue-Green Deployment
```bash
{% raw %}
{% raw %}
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

ENVIRONMENT=${1:-production}
NEW_VERSION=${2:-latest}
HEALTH_CHECK_URL=${3:-https://api.example.com/health}

echo "🔄 Starting blue-green deployment for $ENVIRONMENT environment"

# Determine current and target slots
CURRENT_SLOT=$(kubectl get service app-service -o jsonpath='{.spec.selector.slot}')
if [ "$CURRENT_SLOT" == "blue" ]; then
    TARGET_SLOT="green"
else
    TARGET_SLOT="blue"
fi

echo "📍 Current slot: $CURRENT_SLOT"
echo "🎯 Target slot: $TARGET_SLOT"

# Deploy to target slot
echo "🚀 Deploying version $NEW_VERSION to $TARGET_SLOT slot"
helm upgrade --install app-$TARGET_SLOT ./helm-chart \
    --set image.tag=$NEW_VERSION \
    --set slot=$TARGET_SLOT \
    --set environment=$ENVIRONMENT \
    --namespace $ENVIRONMENT

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/app-$TARGET_SLOT -n $ENVIRONMENT --timeout=300s

# Health check
echo "🏥 Performing health checks..."
for i in {1..10}; do
    if curl -f $HEALTH_CHECK_URL; then
        echo "✅ Health check passed"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Health check failed after 10 attempts"
        exit 1
    fi
    sleep 10
done

# Run smoke tests
echo "🧪 Running smoke tests..."
npm run test:smoke:$ENVIRONMENT

# Switch traffic
echo "🔀 Switching traffic to $TARGET_SLOT slot"
kubectl patch service app-service -p '{"spec":{"selector":{"slot":"'$TARGET_SLOT'"}}}'

# Final verification
echo "🔍 Final verification..."
sleep 30
npm run test:production:smoke

echo "✅ Blue-green deployment completed successfully"
echo "🗑️ Previous slot ($CURRENT_SLOT) is still available for rollback"
{% endraw %}
{% endraw %}
```

### Canary Deployment
```yaml
# canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: react-app-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 2m}
      - setWeight: 20
      - pause: {duration: 2m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 80
      - pause: {duration: 5m}
      canaryService: react-app-canary
      stableService: react-app-stable
      trafficRouting:
        nginx:
          stableIngress: react-app-stable
          additionalIngressAnnotations:
            canary-by-header: X-Canary
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: react-app-canary
        startingStep: 2
        interval: 30s
        count: 5
        successCondition: result[0] >= 0.95
        failureCondition: result[0] < 0.90
  selector:
    matchLabels:
      app: react-app
  template:
    metadata:
      labels:
        app: react-app
    spec:
      containers:
      - name: react-app
        image: myregistry/react-app:latest
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Environment Management

### Infrastructure as Code with Terraform
```hcl
{% raw %}
{% raw %}
# infrastructure/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "react-app/terraform.tfstate"
    region = "us-west-2"
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

# S3 bucket for static hosting
resource "aws_s3_bucket" "app_bucket" {
  bucket = "${var.environment}-react-app-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_public_access_block" "app_bucket_pab" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "app_bucket_website" {
  bucket = aws_s3_bucket.app_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "app_distribution" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.app_bucket_website.website_endpoint
    origin_id   = "S3-${aws_s3_bucket.app_bucket.id}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  aliases = [var.domain_name]

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.app_bucket.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  # Cache behavior for static assets
  ordered_cache_behavior {
    path_pattern           = "/static/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.app_bucket.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      headers      = ["Origin"]
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 31536000
    max_ttl     = 31536000
  }

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.app_cert.arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = var.environment
    Application = "react-app"
  }
}

# SSL Certificate
resource "aws_acm_certificate" "app_cert" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = var.environment
    Application = "react-app"
  }
}

# Route53 DNS
resource "aws_route53_zone" "app_zone" {
  name = var.domain_name

  tags = {
    Environment = var.environment
    Application = "react-app"
  }
}

resource "aws_route53_record" "app_record" {
  zone_id = aws_route53_zone.app_zone.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.app_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.app_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

# Outputs
output "bucket_name" {
  value = aws_s3_bucket.app_bucket.id
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.app_distribution.id
}

output "domain_name" {
  value = var.domain_name
}
{% endraw %}
{% endraw %}
```

This comprehensive guide covers advanced CI/CD pipeline implementations across multiple platforms, providing production-ready configurations for automated testing, security scanning, deployment strategies, and infrastructure management. Each example includes real-world best practices and can be adapted to specific project requirements.
