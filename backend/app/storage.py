import os
import boto3
from dotenv import load_dotenv
load_dotenv()


BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
# B2 will expose an s3 compatible endpoint
s3 = boto3.client( "s3",endpoint_url=os.getenv("B2_ENDPOINT_URL"),aws_access_key_id=os.getenv("B2_KEY_ID"),
    aws_secret_access_key=os.getenv("B2_APPLICATION_KEY"))

# upload the file to the bucket
def upload_object(key, file, content_type):
    s3.upload_fileobj(file, BUCKET_NAME, key, ExtraArgs={"ContentType": content_type or "application/octet-stream"})

# Fetch the file from the bucket
def download_object(key):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return response["Body"]

# Delete the file from the bucket
def delete_object(key):
    s3.delete_object(Bucket=BUCKET_NAME, Key=key)