# Multimedia storages

# Storages
from storages.backends.s3boto3 import S3Boto3Storage


class FileStorage(S3Boto3Storage):
    """S3Boto3Storage for the file bucket"""

    bucket_name = 'business-network-profile-files'


class ImageStorage(S3Boto3Storage):
    """S3Boto3Storage for the image bucket"""

    bucket_name = 'business-network-profile-images'


class VideoStorage(S3Boto3Storage):
    """S3Boto3Storage for the video bucket"""

    bucket_name = 'business-network-profile-videos'