#!/bin/bash

# vLLM Granite Chat 제거 스크립트
# 배포된 모든 리소스를 안전하게 제거합니다

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🗑️  vLLM Granite Chat 제거를 시작합니다..."

# 확인 메시지
read -p "⚠️  모든 리소스가 삭제됩니다. 계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 제거가 취소되었습니다."
    exit 1
fi

echo "🔄 리소스 제거 중..."

# 역순으로 제거 (배포와 반대 순서)
oc delete -f 05-route.yaml --ignore-not-found=true
oc delete -f 04-openwebui-service.yaml --ignore-not-found=true
oc delete -f 03-openwebui-deployment.yaml --ignore-not-found=true
oc delete -f 02-vllm-service.yaml --ignore-not-found=true
oc delete -f 01-vllm-deployment.yaml --ignore-not-found=true
oc delete -f 07-resourcequota.yaml --ignore-not-found=true

# 네임스페이스는 마지막에 제거
echo "📂 네임스페이스 제거 중..."
oc delete -f 00-namespace.yaml --ignore-not-found=true

echo "✅ 모든 리소스가 성공적으로 제거되었습니다!"
echo ""
echo "📋 확인:"
echo "   oc get namespace rhel-ai-chat"
echo "   (네임스페이스가 존재하지 않아야 합니다)"