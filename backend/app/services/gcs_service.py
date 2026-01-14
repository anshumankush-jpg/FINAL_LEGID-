"""Google Cloud Storage service for file uploads."""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from google.cloud import storage
from google.oauth2 import service_account
import json

logger = logging.getLogger(__name__)

class GcsService:
    """Service for Google Cloud Storage operations."""

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.credentials_path = os.getenv("GCS_CREDENTIALS_PATH")

        if not self.bucket_name:
            logger.warning("GCS_BUCKET_NAME not set, GCS functionality disabled")
            self.client = None
            return

        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = storage.Client(credentials=credentials)
            else:
                # Use default credentials (for Google Cloud environments)
                self.client = storage.Client()

            # Test connection
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCS service initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS service: {e}")
            self.client = None

    def generate_upload_signed_url(
        self,
        blob_name: str,
        content_type: str,
        expiration_minutes: int = 15
    ) -> str:
        """Generate a signed URL for uploading a file to GCS."""
        if not self.client or not self.bucket:
            raise Exception("GCS service not configured")

        try:
            blob = self.bucket.blob(blob_name)

            # Set expiration time
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)

            # Generate signed URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="PUT",
                content_type=content_type,
                # Allow public read access after upload
                # access_token=None  # Let the client handle auth
            )

            logger.info(f"Generated signed URL for blob: {blob_name}")
            return signed_url

        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            raise Exception(f"Failed to generate upload URL: {str(e)}")

    def generate_download_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60
    ) -> str:
        """Generate a signed URL for downloading a file from GCS."""
        if not self.client or not self.bucket:
            raise Exception("GCS service not configured")

        try:
            blob = self.bucket.blob(blob_name)

            # Check if blob exists
            if not blob.exists():
                raise Exception(f"Blob {blob_name} does not exist")

            # Set expiration time
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)

            # Generate signed URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )

            logger.info(f"Generated download URL for blob: {blob_name}")
            return signed_url

        except Exception as e:
            logger.error(f"Failed to generate download URL for {blob_name}: {e}")
            raise Exception(f"Failed to generate download URL: {str(e)}")

    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from GCS."""
        if not self.client or not self.bucket:
            raise Exception("GCS service not configured")

        try:
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                logger.info(f"Deleted blob: {blob_name}")
                return True
            else:
                logger.warning(f"Blob {blob_name} does not exist")
                return False

        except Exception as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")

    def get_public_url(self, blob_name: str) -> str:
        """Get the public URL for a blob (if bucket allows public access)."""
        if not self.bucket_name:
            raise Exception("GCS bucket not configured")

        return f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"

    def make_blob_public(self, blob_name: str) -> str:
        """Make a blob publicly accessible and return its public URL."""
        if not self.client or not self.bucket:
            raise Exception("GCS service not configured")

        try:
            blob = self.bucket.blob(blob_name)
            blob.make_public()
            public_url = blob.public_url
            logger.info(f"Made blob public: {blob_name}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to make blob public {blob_name}: {e}")
            raise Exception(f"Failed to make file public: {str(e)}")

# Global service instance
_gcs_service = None

def get_gcs_service() -> GcsService:
    """Get the global GCS service instance."""
    global _gcs_service
    if _gcs_service is None:
        _gcs_service = GcsService()
    return _gcs_service