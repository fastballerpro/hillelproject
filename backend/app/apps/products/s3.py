import boto3
from fastapi import UploadFile


class S3:

    BUCKET_NAME = 'group11112025'
    PUBLIC_URL ='https://pub-f8a0a61d58744db88283773e03043bb4.r2.dev'

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            region_name="EEUR",
            endpoint_url="https://8721af4803f2c3c631a90d8b64d397b7.r2.cloudflarestorage.com",
            aws_access_key_id="2ae25d402a48e45a66e8400661cb1e8f",
            aws_secret_access_key="32d65a0b27b9fb3789484262804a790c877a1257d96831a197f2cb182b616bdd",
        )

    def upload_file(self, file: UploadFile, product_uuid: str) -> str:

        target_filename = f'products/{product_uuid}/{file.filename}'
        self.s3.upload_fileobj(file.file, self.BUCKET_NAME, target_filename)
        url = f'{self.PUBLIC_URL}/{target_filename}'
        return url


s3_service = S3()