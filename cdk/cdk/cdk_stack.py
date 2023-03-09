import os

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_s3_deployment as s3deploy,
    aws_s3_notifications,
    aws_iam as iam
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        project = 'test-task'

        # Runtime selection

        ## There is runtime dictionary with described options for each runtime.
        runtimes = {
            'Python': {
                'name': 'Python',
                'source_code_path': '../lambdas/python/source',
                'layer_path': '../lambdas/python/layer',
                'runtime_version': _lambda.Runtime.PYTHON_3_9,
                'memory_size': 256,
                'handler': 'lambda.handler'
            },
            'NodeJS': {
                'name': 'NodeJS',
                'source_code_path': '../lambdas/nodejs/source',
                'layer_path': '../lambdas/nodejs/layer',
                'runtime_version': _lambda.Runtime.NODEJS_16_X,
                'memory_size': 256,
                'handler': 'lambda.handler'
            },
        }

        ## Getting value from RUNTIME env. variable.
        selected_runtime = os.getenv('RUNTIME', 'Python')

        print(f"Your runtime is: {selected_runtime}")

        s3 = _s3.Bucket(self,
            'alpacked-test-task'
        )

        s3deploy.BucketDeployment(self,
            s3.bucketName,
            destination_bucket=s3,
            sources=[s3deploy.Source.asset('../images')]
        )

        layer = _lambda.LayerVersion(self,
            f'{project}-image-processing-layer',
            code = _lambda.Code.from_asset(runtimes[selected_runtime]['layer_path']),
            compatible_runtimes = [runtimes[selected_runtime]['runtime_version']],
        )

        function = _lambda.Function(self,
            f'{project}-image-processing-lambda',
            code=_lambda.Code.from_asset(runtimes[selected_runtime]['source_code_path']),
            handler=runtimes[selected_runtime]['handler'],
            runtime=runtimes[selected_runtime]['runtime_version'],
            memory_size=runtimes[selected_runtime]['memory_size'],
            layers=[layer],
            environment={
                'WATERMARK_FILE_NAME': 'watermark.jpeg'
            },
            timeout=Duration.seconds(60)
        )

        assert function.role is not None
        function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        function.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                's3:*',
            ],
            resources=[
                s3.bucket_arn
            ],
        ))

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(
            _s3.EventType.OBJECT_CREATED,
            aws_s3_notifications.LambdaDestination(function),
            _s3.NotificationKeyFilter(
                prefix="input",
                suffix=".zip"
            )
        )
