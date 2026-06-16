#!/bin/bash

# vLLM Granite Chat 배포 스크립트
# OpenShift AI 3.4 호환 CPU 기반 모델 서빙

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 vLLM Granite Chat 배포를 시작합니다..."

# 1. 네임스페이스 및 기본 리소스 배포
echo "📂 네임스페이스 및 리소스 쿼터 생성 중..."
oc apply -f 00-namespace.yaml
oc apply -f 07-resourcequota.yaml

echo "⏳ 네임스페이스 준비 완료 대기 중..."
oc wait --for=condition=Active namespace/rhel-ai-chat --timeout=30s

# 2. 모델 서빙 (KServe)
echo "🤖 ServingRuntime 생성 중..."
oc apply -f 01-serving-runtime.yaml

echo "📦 InferenceService 배포 중 (모델 다운로드 및 서빙)..."
oc apply -f 02-inference-service.yaml

echo "⏳ InferenceService 준비 대기 중 (최대 5분)..."
oc wait --for=condition=Ready inferenceservice/granite-chat -n rhel-ai-chat --timeout=300s || echo "⚠️  타임아웃: 수동으로 상태 확인 필요"

# 3. OpenWebUI 배포
echo "🌐 Open WebUI 배포 중..."
oc apply -f 03-openwebui-deployment.yaml
oc apply -f 04-openwebui-service.yaml

# 4. Route 생성
echo "🌍 외부 접근 경로 생성 중..."
oc apply -f 05-route.yaml

echo "✅ 배포 완료!"
echo ""
echo "📋 배포 상태 확인:"
echo "   oc get pods -n rhel-ai-chat"
echo "   oc get svc -n rhel-ai-chat"
echo "   oc get route -n rhel-ai-chat"
echo ""
echo "🔗 웹 UI 접속:"
echo "   $(oc get route openwebui-route -n rhel-ai-chat -o jsonpath='{.spec.host}' 2>/dev/null || echo 'Route 정보를 가져오는 중...')"
echo ""
echo "⚠️  vLLM 모델 로딩에 2-3분이 소요될 수 있습니다."