"""An AWS Python Pulumi program"""

import os

import pulumi
import pulumi_aws as aws

# Making global variable for requesting this value once after pulumi execution.
project = pulumi.get_project()

# Runtime selection

## There is runtime dictionary with described options for each runtime.
runtimes = {
    'Python': {
        'source_code_path': '../lambdas/python/source',
        'layer_path': '../lambdas/python/layer',
        'runtime_version': 'python3.9',
        'memory_size': 256,
        'handler': 'lambda.handler'
    },
    'NodeJS': {
        'source_code_path': '../lambdas/nodejs/source',
        'layer_path': '../lambdas/nodejs/layer',
        'runtime_version': 'nodejs16.x',
        'memory_size': 256,
        'handler': 'lambda.handler'
    },
}

## Getting value from RUNTIME env. variable.
selected_runtime = os.getenv('RUNTIME', 'Python')

print(f'Your runtime is: {selected_runtime}')

# S3 bucket creation
bucket = aws.s3.Bucket(
    'alpacked-test-task',
    acl='private'
)

watermark_file = aws.s3.BucketObject(
    'watermark',
    key='watermark.jpeg',
    bucket=bucket.id,
    source=pulumi.FileAsset('../images/watermark.jpeg')
)

pulumi.export('bucket_name', bucket.id)
pulumi.export('bucket_arn', bucket.arn)

# Lambda creation

lambda_assume_role_policy = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    actions=['sts:AssumeRole'],
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type='Service',
        identifiers=['lambda.amazonaws.com'],
    )],
)])

lambda_inline_role_policy = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    actions=['s3:*'],
    resources=[
        bucket.arn
    ],
)])

lambda_iam_role = aws.iam.Role(
    f'{project}-lambda-role',
    assume_role_policy=lambda_assume_role_policy.json,
    inline_policies=[
        aws.iam.RoleInlinePolicyArgs(
            name=f'{project}-lambda-policy',
            policy=lambda_inline_role_policy.json
        )
    ],
    managed_policy_arns=[
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    ]
)

image_processing_lambda_layer = aws.lambda_.LayerVersion(
    f'{project}-image-processing',
    compatible_runtimes=[runtimes[selected_runtime]['runtime_version']],
    code=pulumi.FileArchive(runtimes[selected_runtime]['layer_path']),
    layer_name=f'{project}-image-processing'
)

image_processing_lambda = aws.lambda_.Function(
    f'{project}-image-processing',
    code=pulumi.FileArchive(runtimes[selected_runtime]['source_code_path']),
    role=lambda_iam_role.arn,
    handler=runtimes[selected_runtime]['handler'],
    runtime=runtimes[selected_runtime]['runtime_version'],
    memory_size=runtimes[selected_runtime]['memory_size'],
    layers=[image_processing_lambda_layer.arn],
    timeout=60,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            'WATERMARK_FILE_NAME': 'watermark.jpeg'
        },
    )
)

s3_bucket_permission = aws.lambda_.Permission(
    f'{project}-image-processing',
    action='lambda:InvokeFunction',
    function=image_processing_lambda.name,
    principal='s3.amazonaws.com',
    source_arn=bucket.arn
)

bucket_notification = aws.s3.BucketNotification(
    f'{project}-image-processing',
    bucket=bucket.id,
    lambda_functions=[aws.s3.BucketNotificationLambdaFunctionArgs(
        lambda_function_arn=image_processing_lambda.arn,
        events=['s3:ObjectCreated:*'],
        filter_prefix='input',
        filter_suffix='.zip'
    )],
    opts=pulumi.ResourceOptions(depends_on=[s3_bucket_permission])
)

pulumi.export('lambda_iam_role_arn', lambda_iam_role.arn)
pulumi.export('lambda_function_name', image_processing_lambda.name)