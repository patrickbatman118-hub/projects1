import boto3
from botocore.exceptions import ClientError, BotoCoreError
from uuid import uuid4
from app.app import logger
from fastapi import UploadFile,HTTPException
import os
s3 = boto3.client('s3', region_name="ap-south-2")


async def upload_to_s3(file: UploadFile, user_id: str):
    try:
        _, file_extension = os.path.splitext(file.filename)
        s3_key = f"pfp/{user_id}/{uuid4()}{file_extension}"
        body = await file.read()
        s3.put_object(Bucket='spliits-pfp-bucket', Key = s3_key, Body = body, ContentType=file.content_type)
        return f"https://spliits-pfp-bucket.s3.ap-south-2.amazonaws.com/{s3_key}"
    except (ClientError,BotoCoreError):
        raise
    except Exception:
        logger.warning(f'file upload failed: {file.filename}')
        raise HTTPException(status_code=500, detail='Error uploading file')

async def delete_from_s3(pfp: str):
    try:
        s3_key = pfp.split('.amazonaws.com/', 1)[1]
        s3.delete_object(Bucket='spliits-pfp-bucket', Key=s3_key)
    except (ClientError,BotoCoreError) as e:
        logger.warning(f'error {e}')
    except Exception:
        logger.warning(f'Error deleting file: {pfp}')
    
