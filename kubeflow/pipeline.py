"""
OpenShift AI 3.4 Kubeflow Pipeline - Iris Classification (CPU-based)

4개 컴포넌트로 구성된 간단한 분류 파이프라인:
1. load_data: Iris 데이터셋 로드
2. preprocess: train/test split (80/20)
3. train: LogisticRegression 학습
4. evaluate: 정확도 및 Confusion Matrix 출력
"""

from kfp import dsl
from kfp.dsl import Output, Input, Dataset, Model, Metrics


@dsl.component(
    base_image='quay.io/modh/runtime-images:runtime-cuda-tensorflow-ubi9-python-3.11-2024a-20240523',
    packages_to_install=['scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def load_data(dataset_out: Output[Dataset]):
    """Iris 데이터셋 로드"""
    from sklearn.datasets import load_iris
    import pandas as pd
    
    iris = load_iris()
    df = pd.DataFrame(
        data=iris.data,
        columns=iris.feature_names
    )
    df['target'] = iris.target
    
    df.to_csv(dataset_out.path, index=False)
    print(f"Loaded {len(df)} samples with {len(iris.feature_names)} features")


@dsl.component(
    base_image='quay.io/modh/runtime-images:runtime-cuda-tensorflow-ubi9-python-3.11-2024a-20240523',
    packages_to_install=['scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def preprocess(
    dataset_in: Input[Dataset],
    train_data_out: Output[Dataset],
    test_data_out: Output[Dataset]
):
    """Train/Test split (80/20)"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    
    df = pd.read_csv(dataset_in.path)
    X = df.drop('target', axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    train_df = X_train.copy()
    train_df['target'] = y_train
    test_df = X_test.copy()
    test_df['target'] = y_test
    
    train_df.to_csv(train_data_out.path, index=False)
    test_df.to_csv(test_data_out.path, index=False)
    
    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")


@dsl.component(
    base_image='quay.io/modh/runtime-images:runtime-cuda-tensorflow-ubi9-python-3.11-2024a-20240523',
    packages_to_install=['scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def train(
    train_data_in: Input[Dataset],
    model_out: Output[Model]
):
    """LogisticRegression 학습"""
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import pickle
    
    train_df = pd.read_csv(train_data_in.path)
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    
    clf = LogisticRegression(max_iter=200, random_state=42)
    clf.fit(X_train, y_train)
    
    with open(model_out.path, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"Model trained with {len(X_train)} samples")
    print(f"Model coefficients shape: {clf.coef_.shape}")


@dsl.component(
    base_image='quay.io/modh/runtime-images:runtime-cuda-tensorflow-ubi9-python-3.11-2024a-20240523',
    packages_to_install=['scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def evaluate(
    model_in: Input[Model],
    test_data_in: Input[Dataset],
    metrics_out: Output[Metrics]
):
    """정확도 및 Confusion Matrix 출력"""
    import pandas as pd
    import pickle
    from sklearn.metrics import accuracy_score, confusion_matrix
    
    test_df = pd.read_csv(test_data_in.path)
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']
    
    with open(model_in.path, 'rb') as f:
        clf = pickle.load(f)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    metrics_out.log_metric('accuracy', accuracy)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Confusion Matrix:\n{cm}")


@dsl.pipeline(
    name='iris-classification-pipeline',
    description='Iris 분류 파이프라인 (CPU 기반, OpenShift AI 3.4)'
)
def iris_classification_pipeline():
    """4개 컴포넌트 파이프라인"""
    load_task = load_data()
    preprocess_task = preprocess(dataset_in=load_task.outputs['dataset_out'])
    train_task = train(train_data_in=preprocess_task.outputs['train_data_out'])
    evaluate(
        model_in=train_task.outputs['model_out'],
        test_data_in=preprocess_task.outputs['test_data_out']
    )


if __name__ == '__main__':
    from kfp import compiler
    
    compiler.Compiler().compile(
        pipeline_func=iris_classification_pipeline,
        package_path='pipeline.yaml'
    )
    print("Pipeline compiled to pipeline.yaml")
