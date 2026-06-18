#!/usr/bin/env python3
"""
boto3를 사용하여 Iris CSV 파일을 S3 버킷에 업로드

s3cmd가 설치되지 않거나 사용할 수 없는 경우의 대안

Usage:
    # 환경변수 설정 (선택 사항)
    export AWS_S3_ENDPOINT=https://s3.amazonaws.com
    export AWS_ACCESS_KEY_ID=<your-access-key>
    export AWS_SECRET_ACCESS_KEY=<your-secret-key>
    
    # 실행
    python upload_to_s3.py
"""

import boto3
import os
import sys

def upload_iris_to_s3():
    """Iris CSV를 S3에 업로드"""
    
    # S3 설정 (환경변수 또는 직접 입력)
    s3_endpoint = os.getenv('AWS_S3_ENDPOINT', 'https://s3.amazonaws.com')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # 자격 증명 확인
    if not access_key or not secret_key:
        print("❌ AWS 자격 증명이 설정되지 않았습니다.")
        print("\n다음 환경변수를 설정하세요:")
        print("  export AWS_S3_ENDPOINT=<your-s3-endpoint>")
        print("  export AWS_ACCESS_KEY_ID=<your-access-key>")
        print("  export AWS_SECRET_ACCESS_KEY=<your-secret-key>")
        print("\n또는 이 스크립트를 수정하여 직접 입력하세요:")
        print("  access_key = '<your-access-key>'")
        print("  secret_key = '<your-secret-key>'")
        sys.exit(1)
    
    # 파일 및 버킷 설정
    bucket_name = 'handon-kubeflow'
    file_path = 'iris.csv'
    s3_key = 'dataset/iris.csv'
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        print(f"\n먼저 다음 명령어로 파일을 생성하세요:")
        print(f"  python prepare_iris_data.py")
        sys.exit(1)
    
    try:
        # S3 클라이언트 생성
        print(f"S3 연결 중... (endpoint: {s3_endpoint})")
        s3 = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # 파일 업로드
        print(f"업로드 중: {file_path} → s3://{bucket_name}/{s3_key}")
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"✓ 업로드 완료!")
        
        # 업로드 확인
        print(f"\n버킷 내용 확인: s3://{bucket_name}/dataset/")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='dataset/')
        
        if 'Contents' in response:
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"  {obj['Key']} ({size_kb:.2f} KB)")
        else:
            print("  (파일 없음)")
    
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
        print("\n문제 해결:")
        print("  1. S3 Endpoint URL 확인")
        print("  2. Access Key/Secret Key 확인")
        print("  3. 버킷 이름 확인")
        print("  4. 네트워크 연결 확인")
        sys.exit(1)

if __name__ == '__main__':
    upload_iris_to_s3()
