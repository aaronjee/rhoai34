"""
OpenShift AI 3.4 Kubeflow Pipeline - Iris Classification (CPU-based)

Simple 4-component classification pipeline:
1. load_data: Load Iris dataset from S3
2. preprocess: train/test split (80/20)
3. train: Train LogisticRegression model
4. evaluate: Evaluate accuracy and confusion matrix
"""

from kfp import dsl
from kfp.dsl import Output, Input, Dataset, Model, Metrics


@dsl.component(
    base_image='registry.redhat.io/rhoai/odh-pipeline-runtime-datascience-cpu-py312-rhel9@sha256:ed6634540d78910ceedc826b871641fb3f66b27be45b50df31c504582204a661',
    packages_to_install=['kfp>=2.0.0', 'scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0', 's3fs>=2023.1.0', 'boto3>=1.28.0']
)
def load_data_from_s3(
    s3_path: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_s3_endpoint: str,
    dataset_out: Output[Dataset]
):
    """Load dataset from S3 bucket"""
    import pandas as pd
    
    print(f"Loading data from S3: {s3_path}")
    print(f"Using S3 endpoint: {aws_s3_endpoint}")
    
    df = pd.read_csv(s3_path, storage_options={
        'key': aws_access_key_id,
        'secret': aws_secret_access_key,
        'client_kwargs': {'endpoint_url': aws_s3_endpoint}
    })
    
    df.to_csv(dataset_out.path, index=False)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")


@dsl.component(
    base_image='registry.redhat.io/rhoai/odh-pipeline-runtime-datascience-cpu-py312-rhel9@sha256:ed6634540d78910ceedc826b871641fb3f66b27be45b50df31c504582204a661',
    packages_to_install=['kfp>=2.0.0', 'scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
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
    base_image='registry.redhat.io/rhoai/odh-pipeline-runtime-datascience-cpu-py312-rhel9@sha256:ed6634540d78910ceedc826b871641fb3f66b27be45b50df31c504582204a661',
    packages_to_install=['kfp>=2.0.0', 'scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def train(
    train_data_in: Input[Dataset],
    model_out: Output[Model]
):
    """Train LogisticRegression model"""
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
    base_image='registry.redhat.io/rhoai/odh-pipeline-runtime-datascience-cpu-py312-rhel9@sha256:ed6634540d78910ceedc826b871641fb3f66b27be45b50df31c504582204a661',
    packages_to_install=['kfp>=2.0.0', 'scikit-learn>=1.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0']
)
def evaluate(
    model_in: Input[Model],
    test_data_in: Input[Dataset],
    metrics_out: Output[Metrics]
):
    """Evaluate model accuracy and confusion matrix"""
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
    description='Iris classification pipeline with S3 data loading, CPU-based runtime for OpenShift AI 3.4'
)
def iris_classification_pipeline(
    s3_dataset_path: str = 's3://handon-kubeflow/dataset/iris.csv',
    aws_access_key_id: str = '',
    aws_secret_access_key: str = '',
    aws_s3_endpoint: str = ''
):
    """4-component pipeline with S3 data loading"""
    proxy_url = 'http://192.168.10.6:3128'
    no_proxy = 'localhost,127.0.0.1,.svc,.svc.cluster.local,ai-aaron-team.svc.cluster.local,kubernetes.default.svc,172.30.0.0/16,10.0.0.0/8,192.168.0.0/16'
    
    load_task = load_data_from_s3(
        s3_path=s3_dataset_path,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_s3_endpoint=aws_s3_endpoint
    )
    load_task.set_env_variable('HTTP_PROXY', proxy_url)
    load_task.set_env_variable('HTTPS_PROXY', proxy_url)
    load_task.set_env_variable('NO_PROXY', no_proxy)
    load_task.set_env_variable('no_proxy', no_proxy)
    
    preprocess_task = preprocess(dataset_in=load_task.outputs['dataset_out'])
    preprocess_task.set_env_variable('HTTP_PROXY', proxy_url)
    preprocess_task.set_env_variable('HTTPS_PROXY', proxy_url)
    preprocess_task.set_env_variable('NO_PROXY', no_proxy)
    preprocess_task.set_env_variable('no_proxy', no_proxy)
    
    train_task = train(train_data_in=preprocess_task.outputs['train_data_out'])
    train_task.set_env_variable('HTTP_PROXY', proxy_url)
    train_task.set_env_variable('HTTPS_PROXY', proxy_url)
    train_task.set_env_variable('NO_PROXY', no_proxy)
    train_task.set_env_variable('no_proxy', no_proxy)
    
    evaluate_task = evaluate(
        model_in=train_task.outputs['model_out'],
        test_data_in=preprocess_task.outputs['test_data_out']
    )
    evaluate_task.set_env_variable('HTTP_PROXY', proxy_url)
    evaluate_task.set_env_variable('HTTPS_PROXY', proxy_url)
    evaluate_task.set_env_variable('NO_PROXY', no_proxy)
    evaluate_task.set_env_variable('no_proxy', no_proxy)


if __name__ == '__main__':
    from kfp import compiler
    
    compiler.Compiler().compile(
        pipeline_func=iris_classification_pipeline,
        package_path='pipeline.yaml'
    )
    print("Pipeline compiled to pipeline.yaml")
