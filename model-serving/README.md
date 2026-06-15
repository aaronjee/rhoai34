# Model Serving - CPU 기반 vLLM + Open WebUI

이 디렉토리는 CPU 환경에서 vLLM과 Open WebUI를 사용한 모델 서빙 테스트 시나리오를 제공합니다.

## 개요

- **목적**: CPU 기반 환경에서 IBM Granite 3.0 2B 모델 서빙 및 웹 UI 제공
- **구성요소**: vLLM (CPU 모드) + Open WebUI
- **보안**: Pod Security Standards (restricted) 적용
  - `seccompProfile: RuntimeDefault` 필수
  - `runAsNonRoot: true` 필수
  - OpenShift SCC 자동 UID/GID 할당
- **리소스**: CPU 최적화된 설정

## 디렉토리 구조

```
model-serving/
├── README.md                    # 이 파일
├── cpu/
│   └── vllm-granite-chat/
│       ├── 00-namespace.yaml           # 네임스페이스 정의
│       ├── 01-vllm-deployment.yaml     # vLLM CPU 배포
│       ├── 02-vllm-service.yaml        # vLLM 서비스
│       ├── 03-openwebui-deployment.yaml # Open WebUI 배포
│       ├── 04-openwebui-service.yaml   # Open WebUI 서비스
│       ├── 05-route.yaml               # OpenShift Route
│       └── 07-resourcequota.yaml       # 리소스 쿼터
```

## 주요 특징

### OpenShift AI 통합
- **대시보드 연동**: `opendatahub.io/dashboard: 'true'` 라벨로 OpenShift AI Dashboard에서 관리

### vLLM 설정
- **이미지**: `registry.redhat.io/rhoai/vllm-cpu-rhel9:3.4.1-1780356811` (Red Hat 공식 CPU 전용, OpenShift AI 3.4.1)
- **모델**: IBM Granite 3.0 2B Instruct
- **디바이스**: CPU 전용 (`--device cpu`)
- **보안**: 비특권 컨테이너, Pod Security Standards 준수
- **스토리지**: emptyDir 사용 (PVC 불필요)
- **헬스체크**: readiness/liveness probe 설정

### Open WebUI 설정
- **인증**: 비활성화 (`WEBUI_AUTH=false`)
- **API 연결**: vLLM 서비스와 자동 연결
- **보안**: OpenShift SCC 호환 보안 컨텍스트 적용

### 네트워크 보안
- **Route**: TLS edge termination, HTTP → HTTPS 리다이렉트

### 리소스 관리
- **CPU 요청/제한**: 최적화된 CPU 할당
- **메모리**: 모델 크기에 맞춘 메모리 설정
- **ResourceQuota**: 네임스페이스 레벨 리소스 제한

## 배포 방법

### 자동 배포 (권장)
```bash
cd model-serving/cpu/vllm-granite-chat
./deploy.sh
```

### 자동 제거
```bash
cd model-serving/cpu/vllm-granite-chat
./undeploy.sh
```

### 수동 배포 순서

1. **기본 인프라**
   ```bash
   oc apply -f 00-namespace.yaml
   oc apply -f 07-resourcequota.yaml
   ```

2. **vLLM 배포**
   ```bash
   oc apply -f 01-vllm-deployment.yaml
   oc apply -f 02-vllm-service.yaml
   ```

3. **Open WebUI 배포**
   ```bash
   oc apply -f 03-openwebui-deployment.yaml
   oc apply -f 04-openwebui-service.yaml
   oc apply -f 05-route.yaml
   ```

### 일괄 배포 명령어
```bash
# 디렉토리 전체 적용
oc apply -f .

# 또는 와일드카드 사용
oc apply -f *.yaml
```

## 검증

1. **Pod 상태 확인**
   ```bash
   oc get pods -n rhel-ai-chat
   ```

2. **서비스 연결 확인**
   ```bash
   oc get svc -n rhel-ai-chat
   ```

3. **Route URL 확인**
   ```bash
   oc get route -n rhel-ai-chat
   ```

4. **웹 UI 접속**
   - Route URL로 접속하여 채팅 인터페이스 확인

## 주의사항

- **CPU 전용 환경**: 추론 속도가 GPU 대비 느림
- **모델 로딩 시간**: 2-3분 소요 가능 (초기 readiness probe 90초 대기)
- **Red Hat 이미지**: OpenShift AI 3.4.1 공식 지원 CPU 최적화 vLLM 런타임 사용
- **리소스 제한**: 동시 사용자 수 제한 가능
- **인증 필요**: Red Hat 레지스트리 접근을 위한 Pull Secret 필요할 수 있음

## 트러블슈팅

### vLLM Pod 시작 실패
- **메모리 부족**: ResourceQuota 확인
- **이미지 풀 실패**: 
  - 네트워크 연결 확인
  - Red Hat 레지스트리 인증 확인: `oc get secret -n rhel-ai-chat | grep pull`
  - Pull Secret 생성: `oc create secret docker-registry rh-pull-secret --docker-server=registry.redhat.io --docker-username=<username> --docker-password=<token>`
- **SCC 에러**: OpenShift는 UID/GID를 자동 할당하므로 `runAsUser`, `runAsGroup`, `fsGroup` 수동 설정 불가
- **Pod Security 에러**: `restricted` 정책에서는 `seccompProfile` 필수 설정

### Pod Security Standards & SCC 오류 해결
```bash
# 기존 배포 정리
oc delete deployment vllm-cpu-server -n rhel-ai-chat
oc delete deployment openwebui -n rhel-ai-chat

# 수정된 manifest로 재배포
oc apply -f 01-vllm-deployment.yaml
oc apply -f 03-openwebui-deployment.yaml
```

### Open WebUI 연결 실패
- vLLM 서비스 상태 확인
- 환경변수 `OPENAI_API_BASE_URL` 확인

### 성능 이슈
- CPU 리소스 할당 증가
- `OMP_NUM_THREADS` 조정
- `VLLM_CPU_KVCACHE_SPACE` 튜닝