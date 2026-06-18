#!/usr/bin/env python3
"""
Iris 데이터셋을 CSV로 생성하여 S3 업로드 준비

Usage:
    python prepare_iris_data.py
    
Output:
    iris.csv - S3에 업로드할 Iris 데이터셋
"""

import sys

try:
    from sklearn.datasets import load_iris
    import pandas as pd
except ModuleNotFoundError as e:
    print(f"❌ 필수 패키지가 설치되지 않았습니다: {e}")
    print("\n다음 명령어로 설치하세요:")
    print("  pip install scikit-learn pandas")
    print("\n또는 전체 requirements.txt 설치:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

def generate_iris_csv():
    """Iris 데이터셋을 CSV 파일로 생성"""
    
    # sklearn에서 Iris 데이터 로드
    iris = load_iris()
    
    # DataFrame 생성
    df = pd.DataFrame(
        data=iris.data,
        columns=iris.feature_names
    )
    df['target'] = iris.target
    
    # CSV 저장
    output_file = 'iris.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✓ Iris 데이터셋 생성 완료: {output_file}")
    print(f"  - 행 개수: {len(df)}")
    print(f"  - 컬럼: {list(df.columns)}")
    print(f"  - 파일 크기: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    print(f"\n다음 명령어로 S3에 업로드하세요:")
    print(f"  s3cmd put {output_file} s3://handon-kubeflow/dataset/{output_file}")
    print(f"\n업로드 확인:")
    print(f"  s3cmd ls s3://handon-kubeflow/dataset/")
    print(f"\n또는 OpenShift AI UI에서:")
    print(f"  1. Data Science Project → Data connections")
    print(f"  2. S3 버킷 브라우저 열기")
    print(f"  3. dataset/ 폴더에 {output_file} 업로드")

if __name__ == '__main__':
    generate_iris_csv()
