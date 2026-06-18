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
