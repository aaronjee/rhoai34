# OpenShift AI 3.4 Kubeflow Pipeline Hands-on (CPU 기반)

간단한 Iris 분류 파이프라인을 통해 OpenShift AI 3.4에서 Kubeflow Pipelines의 핵심 개념을 30-60분 내에 학습합니다.

## Prerequisites

시작하기 전에 다음 항목을 확인하세요:

- [ ] OpenShift AI 3.4 클러스터 접근 권한
- [ ] Data Science Project 생성 완료
- [ ] S3 호환 Object Storage Data Connection 설정 완료 (파이프라인 아티팩트 저장용)
- [ ] Pipeline Server 활성화 (Project → Data Science Pipelines → Configure)
- [ ] Jupyter Workbench 실행 중 (Python 3.11+)
- [ ] 필수 Python 패키지 설치: `pip install -r requirements.txt`

## Quick Start

### 1. 파일 다운로드 (1분)
```bash
git clone <repository-url>
cd rhoai34/kubeflow/
```

### 2. S3 데이터 준비 (5분)

#### Step 2.1: Iris 데이터셋 CSV 생성
```bash
python prepare_iris_data.py
```
예상 출력: `iris.csv` 파일 생성 (150행, 5컬럼)

#### Step 2.2: S3 버킷에 업로드
**방법 1: AWS CLI 사용**
```bash
aws s3 cp iris.csv s3://handon-kubeflow/dataset/iris.csv \
  --endpoint-url <S3-endpoint> \
  --profile <your-profile>
```

**방법 2: OpenShift AI UI 사용**
1. Data Science Project → Data connections
2. S3 버킷 브라우저 열기
3. `dataset/` 폴더 생성 (없으면)
4. `iris.csv` 업로드

### 3. pipeline.py 이해 (10분)
파이프라인은 4개 컴포넌트로 구성됩니다:
- `load_data_from_s3`: S3 버킷에서 데이터셋 로드
- `preprocess`: 80/20 train/test split
- `train`: LogisticRegression 학습
- `evaluate`: 정확도 및 Confusion Matrix 출력

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

### S3 환경변수 누락
**증상**: `AWS_ACCESS_KEY_ID not found` 에러
**해결**: Data Connection 설정 확인 및 Pipeline Server 재시작

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
