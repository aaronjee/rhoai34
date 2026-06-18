# OpenShift AI 3.4 Kubeflow Pipeline Hands-on (CPU 기반)

간단한 Iris 분류 파이프라인을 통해 OpenShift AI 3.4에서 Kubeflow Pipelines의 핵심 개념을 30-60분 내에 학습합니다.

## Prerequisites

시작하기 전에 다음 항목을 확인하세요:

- [ ] OpenShift AI 3.4 클러스터 접근 권한
- [ ] Data Science Project 생성 완료
- [ ] **Jupyter Workbench 생성 및 실행 중**
  - Image: Standard Data Science (Python 3.11 이상)
  - Container size: Small 이상
  - Workbench 상태: Running
  - **인터넷 연결 가능** (pip로 PyPI에서 패키지 자동 다운로드)
- [ ] S3 호환 Object Storage Data Connection 설정 완료 (파이프라인 아티팩트 저장용)
- [ ] Pipeline Server 활성화 (Project → Data Science Pipelines → Configure)

## Quick Start

### 1. Jupyter Workbench 접속 (1분)
1. OpenShift AI Dashboard → Data Science Projects
2. 생성한 프로젝트 선택
3. Workbenches 탭 → 생성한 Workbench의 **Open** 클릭
4. JupyterLab 환경 실행 확인

### 2. S3 데이터 준비 (Jupyter Workbench에서 실행) (10분)

#### Step 2.1: 파일 다운로드
**Jupyter Terminal 실행**:
- JupyterLab 좌측 상단 메뉴 → File → New → Terminal

**Terminal에서 실행**:
```bash
cd ~
git clone https://github.com/aaronjee/rhoai34.git
cd rhoai34/kubeflow/
```

#### Step 2.2: 필수 패키지 설치
**Jupyter Terminal에서 실행**:

**참고**: OpenShift AI Workbench는 기본적으로 Red Hat curated Python Index를 사용하며, s3cmd가 포함되지 않습니다. 공식 PyPI에서 직접 설치해야 합니다.

```bash
# scikit-learn과 pandas는 이미 설치되어 있을 수 있음
pip install scikit-learn pandas

# s3cmd는 공식 PyPI에서 설치 (Red Hat Index에 없음)
pip install --index-url https://pypi.org/simple s3cmd
```

**설명**:
- `scikit-learn`: Iris 데이터셋 로드 및 머신러닝 라이브러리
- `pandas`: 데이터 처리 및 CSV 생성
- `s3cmd`: S3 버킷 업로드 도구 (공식 PyPI에서만 제공)

예상 출력:
```
Looking in indexes: https://console.redhat.com/api/pypi/public-rhai/rhoai/3.4/cpu-ubi9/simple/
Requirement already satisfied: scikit-learn in /opt/app-root/lib64/python3.12/site-packages (1.8.0)
Requirement already satisfied: pandas in /opt/app-root/lib64/python3.12/site-packages (3.0.2)

Looking in indexes: https://pypi.org/simple
Collecting s3cmd
  Downloading s3cmd-2.4.0.tar.gz (181 kB)
Successfully installed s3cmd-2.4.0
```

**대안: Python boto3 스크립트 사용** (s3cmd 설치 불가 시)
```bash
# boto3는 Red Hat Index에 포함되어 있음
pip install boto3
```

boto3를 사용한 S3 업로드 스크립트는 Step 2.5에서 제공됩니다.

#### Step 2.3: Iris 데이터셋 CSV 생성
**Jupyter Terminal에서 실행**:
```bash
python prepare_iris_data.py
```

예상 출력: `iris.csv` 파일 생성 (150행, 5컬럼)

**생성 확인**:
- JupyterLab 파일 브라우저에서 `iris.csv` 파일 확인
- 더블 클릭하여 데이터 미리보기 가능

#### Step 2.4: s3cmd 설정 (Jupyter Terminal에서 실행)

**s3cmd는 Step 2.2에서 이미 설치됨 (`pip install s3cmd`)**

**s3cmd 설정**:
```bash
s3cmd --configure
```

대화형 설정 입력:
```
Access Key: <Data Connection에서 확인한 Access Key>
Secret Key: <Data Connection에서 확인한 Secret Key>
Default Region: us-east-1 (엔터)
S3 Endpoint: <S3 Endpoint URL>  # 예: s3.amazonaws.com 또는 minio.example.com
DNS-style bucket: %(bucket)s.<endpoint>  # 엔터 (기본값)
Encryption password: (엔터 - 선택 사항)
Path to GPG program: (엔터 - 기본값)
Use HTTPS protocol: Yes (엔터)
HTTP Proxy server: (엔터)

Save settings? (y/N) y
```

설정 파일 저장 위치: `~/.s3cfg`

**Data Connection 정보 확인 방법**:
1. OpenShift AI Dashboard → Data Science Project
2. Data connections 탭 → 생성한 Data Connection 선택
3. Access key, Secret key, Endpoint URL 복사

#### Step 2.5: S3 버킷에 업로드 (Jupyter Terminal에서 실행)

**방법 1: s3cmd 사용**
```bash
# 단일 파일 업로드
s3cmd put iris.csv s3://handon-kubeflow/dataset/iris.csv

# 업로드 확인
s3cmd ls s3://handon-kubeflow/dataset/
```

예상 출력:
```
upload: 'iris.csv' -> 's3://handon-kubeflow/dataset/iris.csv'
2024-01-15 10:30   2745   s3://handon-kubeflow/dataset/iris.csv
```

**방법 2: Python boto3 스크립트 사용** (s3cmd 설치 실패 시 대안)

**upload_to_s3.py 파일 생성**:
```python
import boto3
import os

# Data Connection 환경변수에서 자격 증명 가져오기
# 또는 직접 입력
s3_endpoint = os.getenv('AWS_S3_ENDPOINT', 'https://s3.amazonaws.com')
access_key = os.getenv('AWS_ACCESS_KEY_ID', '<your-access-key>')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '<your-secret-key>')

# S3 클라이언트 생성
s3 = boto3.client(
    's3',
    endpoint_url=s3_endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

# 파일 업로드
bucket_name = 'handon-kubeflow'
file_path = 'iris.csv'
s3_key = 'dataset/iris.csv'

s3.upload_file(file_path, bucket_name, s3_key)
print(f"✓ Uploaded {file_path} to s3://{bucket_name}/{s3_key}")

# 업로드 확인
response = s3.list_objects_v2(Bucket=bucket_name, Prefix='dataset/')
for obj in response.get('Contents', []):
    print(f"  {obj['Key']} ({obj['Size']} bytes)")
```

**Jupyter Terminal에서 실행**:
```bash
python upload_to_s3.py
```

예상 출력:
```
✓ Uploaded iris.csv to s3://handon-kubeflow/dataset/iris.csv
  dataset/iris.csv (2745 bytes)
```

**방법 3: JupyterLab UI 사용**
1. JupyterLab 파일 브라우저에서 `iris.csv` 우클릭
2. Download 선택하여 로컬에 저장
3. OpenShift AI Dashboard → Data connections → S3 버킷 브라우저
4. `dataset/` 폴더에 `iris.csv` 업로드

### 3. pipeline.py 이해 (10분)
파이프라인은 4개 컴포넌트로 구성됩니다:
- `load_data_from_s3`: S3 버킷에서 데이터셋 로드
- `preprocess`: 80/20 train/test split
- `train`: LogisticRegression 학습
- `evaluate`: 정확도 및 Confusion Matrix 출력

**중요**: 각 컴포넌트의 `packages_to_install` 파라미터에 지정된 패키지들은 **파이프라인 실행 시 자동으로 인터넷을 통해 PyPI에서 다운로드 및 설치**됩니다.
```python
@dsl.component(
    base_image='registry.redhat.io/rhoai/odh-pipeline-runtime-datascience-cpu-py312-rhel9',
    packages_to_install=['scikit-learn>=1.3.0', 'pandas>=2.0.0', 's3fs>=2023.1.0', 'boto3>=1.28.0']
    # ↑ 파이프라인 실행 시 컨테이너 내부에서 pip install로 자동 설치됨
)
```

### 4. pipeline.yaml 컴파일 (3분)
```python
from kfp import compiler

compiler.Compiler().compile(
    pipeline_func=iris_classification_pipeline,
    package_path='pipeline.yaml'
)
```

예상 출력: `pipeline.yaml` 파일 생성 완료

### 5. 파이프라인 실행 - UI 방식 (10분)
1. OpenShift AI Dashboard → Data Science Pipelines → Import pipeline
2. `pipeline.yaml` 업로드
3. Create run → Run once
4. **Parameters 설정**:
   - `s3_dataset_path`: `s3://handon-kubeflow/dataset/iris.csv` (기본값)
5. Submit
6. 실행 상태 모니터링 (약 5분 소요)

### 6. 결과 확인 (5분)
- Run details에서 각 컴포넌트 로그 확인
- `load_data_from_s3` 로그: S3에서 로드된 행/컬럼 수
- `evaluate` 컴포넌트 Output: accuracy 및 Confusion Matrix

## File Structure

- `README.md` - 이 가이드
- `pipeline.py` - 파이프라인 소스 (4개 컴포넌트: load_data_from_s3 → preprocess → train → evaluate)
- `pipeline.yaml` - 컴파일된 IR YAML
- `prepare_iris_data.py` - Iris 데이터셋 CSV 생성 스크립트
- `notebook.ipynb` - Jupyter 실습 파일
- `requirements.txt` - Python 의존성 (kfp, scikit-learn, pandas, s3fs, boto3)

## Execution Methods

**UI 실행** (권장): Quick Start 참조  
**SDK 실행** (Advanced): `kfp.client.Client().create_run_from_pipeline_package('pipeline.yaml')`

## Pipeline Naming 규칙 및 권장사항

Kubeflow Pipelines는 Kubernetes 위에서 실행되므로 **DNS-1123 subdomain naming 규칙**을 준수해야 합니다.

### 필수 규칙 (Kubernetes DNS-1123)

| 항목 | 규칙 | 예시 |
|------|------|------|
| **문자** | 소문자 영숫자, 하이픈(-), 점(.) 만 허용 | `iris-pipeline`, `ml-v1.0` |
| **시작/끝** | 영숫자로 시작하고 끝나야 함 | ✅ `my-pipeline` ❌ `-pipeline-` |
| **길이** | 최대 253자 | `my-very-long-pipeline-name...` (253자 이내) |
| **대문자** | 사용 불가 | ❌ `Iris-Pipeline` ✅ `iris-pipeline` |
| **특수문자** | 언더스코어(_), 공백 등 사용 불가 | ❌ `iris_pipeline` ✅ `iris-pipeline` |

### Pipeline Name (@dsl.pipeline)

**현재 예제**:
```python
@dsl.pipeline(
    name='iris-classification-pipeline',  # ✅ kebab-case
    description='Iris 분류 파이프라인 (S3 데이터 로드, CPU 기반, OpenShift AI 3.4)'
)
```

**권장 패턴**:
- `<use-case>-<model-type>-pipeline`: `fraud-detection-xgboost-pipeline`
- `<dataset>-<task>-pipeline`: `iris-classification-pipeline`
- `<team>-<project>-v<version>`: `datascience-iris-v1`

**피해야 할 패턴**:
- ❌ `Iris_Classification_Pipeline` (대문자, 언더스코어)
- ❌ `iris classification` (공백)
- ❌ `pipeline` (너무 일반적)
- ❌ `-my-pipeline-` (하이픈으로 시작/끝)

### Component Function Names (Python 함수)

Component 함수명은 **Python naming convention (snake_case)** 을 따릅니다.

**현재 예제**:
```python
def load_data_from_s3(...)  # ✅ snake_case
def preprocess(...)
def train(...)
def evaluate(...)
```

**권장 패턴**:
- 동사로 시작: `load_data`, `preprocess_features`, `train_model`, `evaluate_metrics`
- 명확하고 구체적: `load_from_s3` → `load_data_from_s3`
- 일관된 접미사: `_task`, `_step`, `_component` (선택 사항)

### Pipeline Parameters

파라미터명도 **snake_case** 를 사용하되, 의미가 명확해야 합니다.

**현재 예제**:
```python
def iris_classification_pipeline(
    s3_dataset_path: str = 's3://handon-kubeflow/dataset/iris.csv'  # ✅
)
```

**권장 패턴**:
- `s3_dataset_path`, `model_version`, `train_test_split_ratio`
- `input_bucket`, `output_bucket`, `learning_rate`

**피해야 할 패턴**:
- ❌ `path` (너무 모호)
- ❌ `S3Path` (camelCase)
- ❌ `s3-path` (kebab-case는 Python 변수로 사용 불가)

### Task Variable Names (pipeline 함수 내부)

Task 변수는 컴포넌트 간 연결을 추적하기 쉽도록 명명합니다.

**현재 예제**:
```python
load_task = load_data_from_s3(...)        # ✅
preprocess_task = preprocess(...)         # ✅
train_task = train(...)                   # ✅
evaluate(...)  # 반환값 미사용 시 변수 생략 가능
```

**권장 패턴**:
- `<component-name>_task` 또는 `<component-name>_op`
- 일관된 접미사 사용 (task, op, step 중 선택)

### Artifact Names (Input/Output)

Artifact 파라미터명은 **역할을 명확히** 표현합니다.

**현재 예제**:
```python
def preprocess(
    dataset_in: Input[Dataset],      # ✅ 입력 명확
    train_data_out: Output[Dataset], # ✅ 출력 명확
    test_data_out: Output[Dataset]   # ✅ 출력 명확
)
```

**권장 패턴**:
- 입력: `<name>_in` (dataset_in, model_in)
- 출력: `<name>_out` (dataset_out, model_out, metrics_out)
- 또는: `input_<name>`, `output_<name>`

### Run Name (실행 시 지정)

OpenShift AI UI 또는 SDK로 파이프라인 실행 시 Run name을 지정할 수 있습니다.

**권장 패턴**:
- `<pipeline-name>-<timestamp>`: `iris-pipeline-20240615-1430`
- `<pipeline-name>-<experiment>`: `iris-pipeline-experiment-1`
- `<user>-<pipeline-name>`: `aaron-iris-pipeline`

**UI 기본값**: 
- OpenShift AI는 자동으로 타임스탬프 기반 이름 생성
- 예: `iris-classification-pipeline-2024-06-15-14-30-45`

### 버전 관리 권장사항

파이프라인 버전을 관리할 때:

**Option 1: Pipeline name에 버전 포함**
```python
@dsl.pipeline(
    name='iris-classification-pipeline-v1',
    description='Iris 분류 파이프라인 v1.0'
)
```

**Option 2: Description에 버전 명시**
```python
@dsl.pipeline(
    name='iris-classification-pipeline',
    description='Iris 분류 파이프라인 (v1.0.0, 2024-06-15)'
)
```

**Option 3: Git tag와 연동**
- Git tag: `v1.0.0`, `v1.1.0-rc1`
- Pipeline name: `iris-classification-pipeline` (고정)
- Pipeline YAML 파일명: `pipeline-v1.0.0.yaml`

### 요약 표

| 항목 | Naming Convention | 예시 |
|------|-------------------|------|
| **Pipeline Name** | kebab-case, DNS-1123 | `iris-classification-pipeline` |
| **Component Function** | snake_case (Python) | `load_data_from_s3`, `train_model` |
| **Parameters** | snake_case (Python) | `s3_dataset_path`, `learning_rate` |
| **Task Variables** | snake_case + _task | `load_task`, `preprocess_task` |
| **Artifact I/O** | snake_case + _in/_out | `dataset_in`, `model_out` |
| **Run Name** | kebab-case + timestamp | `iris-pipeline-20240615-1430` |

---

## Pipeline 등록 및 Run 생성 시 Naming 규칙

OpenShift AI Dashboard에서 파이프라인을 등록하고 실행할 때의 명명 규칙입니다.

### 1. Pipeline 등록 (Import Pipeline)

**단계**: OpenShift AI Dashboard → Data Science Pipelines → **Import pipeline**

#### Pipeline Name (필수)

파이프라인을 처음 업로드할 때 지정하는 이름입니다.

**규칙**:
- **DNS-1123 준수** (소문자, 숫자, 하이픈만)
- **고유성**: 프로젝트 내에서 유일해야 함
- **불변성**: 한번 등록하면 이름 변경 불가 (삭제 후 재등록 필요)

**권장 패턴**:
```
<use-case>-pipeline-<version>
<team>-<project>-pipeline
<dataset>-<model>-pipeline
```

**예시**:
- ✅ `iris-classification-pipeline` (버전 없음 - 단일 버전 관리)
- ✅ `iris-classification-pipeline-v1` (버전 포함 - 다중 버전 관리)
- ✅ `datascience-iris-ml-pipeline`
- ✅ `fraud-detection-xgboost-pipeline`
- ❌ `Iris_Pipeline` (대문자, 언더스코어)
- ❌ `pipeline` (너무 일반적)

**버전 관리 전략**:

**전략 A: 이름에 버전 포함** (권장)
```
iris-classification-pipeline-v1
iris-classification-pipeline-v2
iris-classification-pipeline-v3
```
- 장점: 여러 버전 동시 존재 가능, 롤백 쉬움
- 단점: 프로젝트에 파이프라인 개수 증가

**전략 B: 버전 없이 덮어쓰기**
```
iris-classification-pipeline (삭제 후 재등록)
```
- 장점: 파이프라인 목록 간결
- 단점: 이전 버전 복구 불가

**실제 UI 예시**:
```
Import pipeline 화면:
┌─────────────────────────────────────────┐
│ Pipeline name: iris-classification-v1   │  ← 여기에 입력
│ Description: Iris 분류 (v1.0, CPU)      │
│ Pipeline file: [pipeline.yaml 선택]     │
└─────────────────────────────────────────┘
```

#### Pipeline Description (선택 사항)

**권장 내용**:
- 파이프라인의 목적
- 주요 컴포넌트
- 버전 정보
- 마지막 업데이트 날짜

**예시**:
```
Iris 분류 파이프라인 (v1.0.0)
- S3에서 데이터 로드
- LogisticRegression 학습
- CPU 전용, OpenShift AI 3.4
- 업데이트: 2024-06-15
```

---

### 2. Run 생성 (Create Run)

**단계**: Pipeline 선택 → **Create run** → Run 세부사항 입력

#### Run Name (필수)

각 실행마다 고유한 이름을 지정합니다.

**규칙**:
- **DNS-1123 준수**
- **고유성**: 프로젝트 내에서 유일해야 함
- **자동 생성**: 비워두면 OpenShift AI가 자동으로 타임스탬프 기반 이름 생성

**권장 패턴**:

**패턴 1: 자동 생성 사용** (권장 - 간편함)
```
UI에서 비워두면 자동 생성:
iris-classification-pipeline-v1-20240615143025
```

**패턴 2: 실험 번호 포함**
```
<pipeline-name>-exp<number>
<pipeline-name>-experiment-<description>
```
예시:
- `iris-v1-exp001`
- `iris-v1-exp002-tuned`
- `iris-v1-baseline`
- `iris-v1-hyperparameter-test`

**패턴 3: 날짜 + 실험 설명**
```
<pipeline-name>-<YYYYMMDD>-<description>
```
예시:
- `iris-v1-20240615-baseline`
- `iris-v1-20240616-increased-data`
- `iris-v1-20240617-feature-eng`

**패턴 4: 사용자 + 목적**
```
<user>-<pipeline-name>-<purpose>
```
예시:
- `aaron-iris-v1-testing`
- `aaron-iris-v1-production`
- `datascience-iris-v1-demo`

**실제 UI 예시**:
```
Create run 화면:
┌──────────────────────────────────────────────────┐
│ Run name: iris-v1-20240615-baseline              │  ← 여기에 입력 (비워두면 자동)
│ Description: Baseline 실험 - 기본 하이퍼파라미터 │
│ Pipeline: iris-classification-pipeline-v1        │
│ Pipeline version: (latest)                       │
│                                                  │
│ Parameters:                                      │
│   s3_dataset_path: s3://handon-kubeflow/...     │
└──────────────────────────────────────────────────┘
```

#### Run Description (선택 사항)

**권장 내용**:
- 실험 목적
- 변경된 파라미터
- 예상 결과
- 실행자 이름

**예시**:
```
Baseline 실험
- 기본 하이퍼파라미터 사용
- Train/Test split: 80/20
- 실행자: Aaron
- 목적: 성능 벤치마크 설정
```

---

### 3. Experiment (실험 그룹) - 선택 사항

OpenShift AI는 여러 Run을 **Experiment**로 그룹화할 수 있습니다.

#### Experiment Name

**규칙**: DNS-1123 준수

**권장 패턴**:
```
<project>-<phase>-<date>
<model>-<optimization-goal>
```

**예시**:
- `iris-hyperparameter-tuning`
- `iris-feature-engineering-june2024`
- `iris-model-comparison`
- `fraud-detection-accuracy-improvement`

**실제 사용 예시**:
```
Experiment: iris-hyperparameter-tuning
├─ Run 1: iris-v1-learning-rate-001
├─ Run 2: iris-v1-learning-rate-01
├─ Run 3: iris-v1-learning-rate-1
└─ Run 4: iris-v1-best-params
```

---

### 4. 실전 명명 예시

#### 시나리오 1: 초기 개발 단계

```
Pipeline: iris-classification-pipeline-dev
Run 1:    iris-dev-20240615-initial-test
Run 2:    iris-dev-20240615-bugfix
Run 3:    iris-dev-20240616-ready-for-review
```

#### 시나리오 2: 하이퍼파라미터 튜닝

```
Pipeline:   iris-classification-pipeline-v1
Experiment: iris-hyperparameter-tuning-june2024

Run 1: iris-v1-lr-0001-iter-100
Run 2: iris-v1-lr-001-iter-100
Run 3: iris-v1-lr-001-iter-200
Run 4: iris-v1-best-params
```

#### 시나리오 3: A/B 테스트

```
Pipeline:   iris-classification-pipeline-v2
Experiment: iris-model-comparison

Run 1: iris-v2-logistic-regression
Run 2: iris-v2-random-forest
Run 3: iris-v2-svm
Run 4: iris-v2-ensemble
```

#### 시나리오 4: 프로덕션 배포

```
Pipeline: iris-classification-pipeline-prod
Run 1:    iris-prod-20240615-release-v1.0.0
Run 2:    iris-prod-20240620-release-v1.0.1-hotfix
Run 3:    iris-prod-20240701-release-v1.1.0
```

---

### 5. 명명 규칙 체크리스트

**Pipeline 등록 시**:
- [ ] 소문자, 숫자, 하이픈만 사용
- [ ] 프로젝트 내 고유한 이름
- [ ] 버전 관리 전략 결정 (이름에 포함 vs 별도 관리)
- [ ] Description에 주요 정보 기록

**Run 생성 시**:
- [ ] 실험 목적이 명확한 이름
- [ ] 프로젝트 내 고유한 이름
- [ ] 일관된 패턴 사용 (팀 내 합의)
- [ ] Description에 실험 세부사항 기록

**권장하지 않는 패턴**:
- ❌ `test`, `test1`, `test2` (목적 불명확)
- ❌ `run`, `pipeline-run` (너무 일반적)
- ❌ `asdf`, `temp`, `tmp` (임시로 만들고 삭제 안함)
- ❌ `IRIS-Pipeline` (대문자)
- ❌ `iris_pipeline_2024_06_15` (언더스코어)

---

### 6. 명명 규칙 요약 표

| 항목 | 범위 | 규칙 | 예시 |
|------|------|------|------|
| **Pipeline Name** | 프로젝트 내 고유 | kebab-case, DNS-1123 | `iris-classification-pipeline-v1` |
| **Run Name** | 프로젝트 내 고유 | kebab-case, DNS-1123 | `iris-v1-20240615-baseline` |
| **Experiment Name** | 프로젝트 내 고유 | kebab-case, DNS-1123 | `iris-hyperparameter-tuning` |
| **Description** | 자유 형식 | 명확한 설명 | `Baseline 실험 - 기본 파라미터` |

## Troubleshooting

### s3cmd 설치 실패 (Red Hat Python Index에서 찾을 수 없음)
**증상**:
```
Looking in indexes: https://console.redhat.com/api/pypi/public-rhai/rhoai/3.4/cpu-ubi9/simple/
ERROR: Could not find a version that satisfies the requirement s3cmd (from versions: none)
ERROR: No matching distribution found for s3cmd
```

**원인**: OpenShift AI Workbench는 Red Hat curated Python Index를 사용하며, s3cmd는 보안 및 지원 정책상 포함되지 않음

**해결 방법 1: 공식 PyPI에서 직접 설치**
```bash
pip install --index-url https://pypi.org/simple s3cmd
```

**해결 방법 2: boto3 사용 (권장 대안)**
```bash
# boto3는 Red Hat Index에 포함되어 있음
pip install boto3

# Step 2.5의 "방법 2: Python boto3 스크립트 사용" 참조
```

### S3 환경변수 누락
**증상**: `AWS_ACCESS_KEY_ID not found` 에러
**해결**: Data Connection 설정 확인 및 Pipeline Server 재시작

### s3cmd 연결 실패
**증상**: `ERROR: S3 error: 403 (AccessDenied)`
**해결**: 
```bash
# s3cmd 설정 재확인
s3cmd --configure

# 연결 테스트
s3cmd ls s3://handon-kubeflow/

# 설정 파일 확인
cat ~/.s3cfg
```

### s3cmd 업로드 오류
**증상**: `ERROR: Bucket 'handon-kubeflow' does not exist`
**해결**:
```bash
# 버킷 생성 (필요시)
s3cmd mb s3://handon-kubeflow

# 버킷 목록 확인
s3cmd ls
```

### pip 패키지 설치 실패
**증상**: `Could not find a version that satisfies the requirement` 또는 연결 타임아웃
**원인**: 인터넷 연결 문제 또는 PyPI 접근 불가
**해결**:
```bash
# 인터넷 연결 확인
ping pypi.org

# pip 기본 index 확인
pip config list

# 프록시 환경인 경우 설정
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
pip install scikit-learn pandas s3cmd
```

### 파이프라인 컴포넌트 패키지 설치 실패
**증상**: 파이프라인 실행 중 컴포넌트가 `ImagePullBackOff` 또는 `CrashLoopBackOff`
**원인**: 컨테이너 내부에서 PyPI 접근 불가 (인터넷 연결 또는 방화벽)
**해결**:
- OpenShift 클러스터의 아웃바운드 인터넷 연결 확인
- NetworkPolicy가 PyPI (pypi.org, files.pythonhosted.org) 접근을 허용하는지 확인
- Pod 로그 확인: `oc logs <pod-name> -n <namespace>`

### KFP 버전 불일치
**증상**: `ImportError: cannot import name 'dsl'`
**해결**: `pip install --upgrade kfp>=2.14.3`

### 파이프라인 실행 실패
**증상**: 컴포넌트가 Pending 상태에서 진행 안됨
**해결**: Pod 리소스 확인 (`oc get pods -n <project-namespace>`)

## Next Steps

프로덕션 환경에서 고려할 사항:
- 파이프라인 캐싱 활성화 (중복 실행 방지)
- 컴포넌트별 리소스 요청/제한 설정
- 에러 핸들링 및 재시도 로직 추가
- 모델 메트릭 추적 (MLflow 연동)

## 참고 문서
- [OpenShift AI 3.4 공식 문서](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/3.4)
- [Kubeflow Pipelines SDK 2.x](https://www.kubeflow.org/docs/components/pipelines/v2/)
- [s3cmd 공식 웹사이트](https://s3tools.org/s3cmd)
- [s3cmd GitHub](https://github.com/s3tools/s3cmd)
- [s3cmd 사용 가이드](https://s3tools.org/usage)
