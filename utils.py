import os
import io
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT_URL = "https://storage.yandexcloud.net"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


# Функция для загрузки данных из S3
def load_parquet_from_s3(s3_key):
    s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    buffer = io.BytesIO()
    s3_client.download_fileobj(Bucket=S3_BUCKET_NAME, Key=s3_key, Fileobj=buffer)
    buffer.seek(0)
    return buffer
