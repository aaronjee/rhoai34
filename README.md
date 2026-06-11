# RHOAI 3.4 Test Manifests Repository

## 프로젝트 소개 (Project Overview)

이 저장소는 **Red Hat OpenShift AI (RHOAI) 3.4** 기반에서 다양한 AI/ML 워크로드를 테스트하기 위한 manifest 파일들을 제공합니다. 각 시나리오별로 구성된 YAML 파일들을 통해 OpenShift AI의 핵심 기능들을 쉽고 빠르게 검증할 수 있습니다.

## 목적 (Purpose)

- **시나리오별 YAML 파일 제공**: 다양한 AI/ML 사용 사례에 맞는 manifest 파일 모음
- **쉬운 배포 및 테스트**: git clone 후 즉시 배포 가능한 ready-to-use 설정
- **기능 검증**: RHOAI 3.4의 주요 기능들을 단계별로 테스트
- **학습 및 참고 자료**: OpenShift AI 활용을 위한 실용적인 예제 제공

## 사전 요구사항 (Prerequisites)

- **OpenShift Cluster**: 4.12+ 버전 권장
- **RHOAI 3.4 설치**: Red Hat OpenShift AI Operator 설치 완료
- **CLI 도구**: `oc` (OpenShift CLI), `kubectl`
- **권한**: cluster-admin 또는 적절한 RBAC 권한
- **리소스**: 충분한 CPU/Memory/Storage 할당

## 디렉토리 구조 (Directory Structure)

```
rhoai34/
├── README.md
├── basic-workloads/          # 기본 워크로드 테스트
│   ├── jupyter-notebook/     # Jupyter Notebook 배포
│   ├── model-training/       # 모델 훈련 작업
│   └── data-preprocessing/   # 데이터 전처리 파이프라인
├── model-serving/            # 모델 서빙 테스트
│   ├── tensorflow-serving/   # TensorFlow 모델 서빙
│   ├── pytorch-serving/      # PyTorch 모델 서빙
│   └── custom-runtime/       # 커스텀 런타임 설정
├── data-pipelines/           # 데이터 파이프라인
│   ├── kubeflow-pipelines/   # Kubeflow Pipelines 예제
│   ├── data-science-pipeline/ # Data Science Pipeline
│   └── workflow-automation/  # 워크플로우 자동화
├── scaling-tests/            # 스케일링 테스트
│   ├── horizontal-scaling/   # 수평 확장 테스트
│   ├── vertical-scaling/     # 수직 확장 테스트
│   └── auto-scaling/         # 자동 스케일링 설정
└── monitoring/               # 모니터링 및 관찰성
    ├── prometheus-config/    # Prometheus 설정
    ├── grafana-dashboards/   # Grafana 대시보드
    └── alerting-rules/       # 알림 규칙 설정
```

## 사용법 (Usage Guide)

### 1. 저장소 클론 (Clone Repository)
```bash
git clone <repository-url>
cd rhoai34
```

### 2. 시나리오별 배포 (Deploy by Scenario)
```bash
# 기본 워크로드 배포
oc apply -f basic-workloads/jupyter-notebook/

# 모델 서빙 테스트
oc apply -f model-serving/tensorflow-serving/

# 데이터 파이프라인 실행
oc apply -f data-pipelines/kubeflow-pipelines/
```

### 3. 배포 상태 확인 (Verify Deployment)
```bash
# Pod 상태 확인
oc get pods -n <namespace>

# 서비스 상태 확인
oc get svc -n <namespace>

# 로그 확인
oc logs <pod-name> -n <namespace>
```

### 4. 정리 (Cleanup)
```bash
# 특정 시나리오 정리
oc delete -f basic-workloads/jupyter-notebook/

# 전체 정리
oc delete project <test-project-name>
```

## 시나리오별 설명 (Scenario Descriptions)

### 🚀 Basic Workloads
- **Jupyter Notebook**: 데이터 사이언스 개발 환경 구성
- **Model Training**: 기본적인 모델 훈련 작업 실행
- **Data Preprocessing**: 데이터 전처리 파이프라인 구성

### 🎯 Model Serving
- **TensorFlow Serving**: TensorFlow 모델의 실시간 추론 서비스
- **PyTorch Serving**: PyTorch 모델 서빙 및 API 제공
- **Custom Runtime**: 사용자 정의 런타임 환경 구성

### 🔄 Data Pipelines
- **Kubeflow Pipelines**: ML 워크플로우 오케스트레이션
- **Data Science Pipeline**: 엔드투엔드 데이터 사이언스 파이프라인
- **Workflow Automation**: 자동화된 ML 워크플로우

### 📈 Scaling Tests
- **Horizontal Scaling**: 워크로드 수평 확장 테스트
- **Vertical Scaling**: 리소스 수직 확장 검증
- **Auto Scaling**: HPA/VPA 기반 자동 스케일링

### 📊 Monitoring
- **Prometheus Config**: 메트릭 수집 및 모니터링 설정
- **Grafana Dashboards**: 시각화 대시보드 구성
- **Alerting Rules**: 알림 및 경고 규칙 설정

## 기여 방법 (Contributing)

1. 새로운 시나리오 추가 시 해당 디렉토리 구조 유지
2. 각 manifest 파일에 주석으로 설명 추가
3. 테스트 완료 후 Pull Request 생성
4. README 업데이트 시 한국어/영어 병행 작성

## 라이선스 (License)

이 프로젝트는 교육 및 테스트 목적으로 제공됩니다.

---

**참고**: 이 저장소의 manifest 파일들은 RHOAI 3.4 환경에서 테스트되었으며, 프로덕션 환경 사용 전 충분한 검토가 필요합니다.