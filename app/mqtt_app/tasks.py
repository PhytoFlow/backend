import os
from celery import shared_task
import boto3
from botocore.exceptions import NoCredentialsError

def boto3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    )

@shared_task
def upload_to_s3(content):
    s3 = boto3_client()
    try:
        s3.put_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key='arquivo.txt', Body=content)
        return "Arquivo enviado com sucesso"
    except NoCredentialsError:
        return "Erro: Credenciais não encontradas"