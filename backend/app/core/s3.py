import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import logging
from typing import Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# S3 client
s3_client = None


def get_s3_client():
    """Get S3 client instance."""
    global s3_client
    if s3_client is None:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    return s3_client


async def upload_file_to_s3(
    file_content: bytes,
    file_name: str,
    content_type: str,
    folder: str = "attachments"
) -> Optional[str]:
    """
    Upload a file to S3 and return the URL.
    
    Args:
        file_content: The file content as bytes
        file_name: The original file name
        content_type: The MIME type of the file
        folder: The S3 folder to upload to
    
    Returns:
        The S3 URL of the uploaded file, or None if upload failed
    """
    try:
        # Generate unique file name
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_file_name = f"{uuid.uuid4()}.{file_extension}"
        s3_key = f"{folder}/{unique_file_name}"
        
        # Upload file to S3
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
            ContentDisposition=f'attachment; filename="{file_name}"'
        )
        
        # Return the public URL
        file_url = f"{settings.S3_BASE_URL}/{s3_key}"
        logger.info(f"File uploaded successfully: {file_url}")
        return file_url
        
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {e}")
        return None


async def delete_file_from_s3(file_url: str) -> bool:
    """
    Delete a file from S3.
    
    Args:
        file_url: The S3 URL of the file to delete
    
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Extract S3 key from URL
        if not file_url.startswith(settings.S3_BASE_URL):
            logger.error(f"Invalid S3 URL: {file_url}")
            return False
        
        s3_key = file_url.replace(f"{settings.S3_BASE_URL}/", "")
        
        # Delete file from S3
        s3_client = get_s3_client()
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        
        logger.info(f"File deleted successfully: {file_url}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting file: {e}")
        return False


def generate_presigned_url(file_name: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate a presigned URL for uploading a file to S3.
    
    Args:
        file_name: The name of the file
        expiration: Time in seconds for the URL to expire
    
    Returns:
        The presigned URL, or None if generation failed
    """
    try:
        s3_client = get_s3_client()
        
        # Generate unique file name
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_file_name = f"{uuid.uuid4()}.{file_extension}"
        s3_key = f"attachments/{unique_file_name}"
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': 'application/octet-stream'
            },
            ExpiresIn=expiration
        )
        
        return presigned_url
        
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {e}")
        return None
