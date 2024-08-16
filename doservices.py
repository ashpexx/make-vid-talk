import boto3
import ffmpeg
import uuid
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from pathlib import Path
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv
import json
import subprocess

load_dotenv()

class DigitalOceanService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.environ['DO_S3_ENDPOINT'],  # Replace with your endpoint
            region_name=os.environ['DO_S3_REGION'],           # Replace with your region
            aws_access_key_id=os.environ['DO_S3_ACCESS_KEY'],  # Replace with your access key
            aws_secret_access_key=os.environ['DO_S3_SECRET_ACCESS_KEY']  # Replace with your secret key
        )
        self.bucket_name = os.environ['DO_S3_SPACENAME']  # Replace with your bucket name

    def delete_file(self, key: str) -> None:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"Failed to delete file from DigitalOcean: {str(e)}")

    def upload_file(self, file_content: bytes, slug: str, filename: str) -> str:
        timestamp = uuid.uuid4().hex
        key = f"{slug}/{timestamp}-{filename}"
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ACL='public-read'
            )
            return f"https://cdn.allwebtool.com/{key}"
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"Failed to upload file to DigitalOcean: {str(e)}")

    def get_file_duration(self, url):
        try:
            ffprobe_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {url}"
            output = subprocess.check_output(ffprobe_cmd, shell=True)
            duration = float(output.decode('utf-8').strip())
            return duration
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None

    def validate_file_duration(self, url: str) -> None:
        duration = self.get_file_duration(url)
        if duration > 30:
            raise ValueError('File exceeds 30 seconds')

    def generate_thumbnail(self, video_url: str, folder: str, slug: str) -> str:
        thumbnail_filename = f"{slug}-thumbnail.png"
        thumbnail_path = Path(folder) / thumbnail_filename
        
        try:
            ffmpeg.input(video_url).output(str(thumbnail_path), vframes=1, s='320x240').run()
            
            with open(thumbnail_path, 'rb') as f:
                thumbnail_buffer = f.read()
                
            thumbnail_url = self.upload_file(thumbnail_buffer, folder, thumbnail_filename)
            
            thumbnail_path.unlink()  # Clean up the temporary thumbnail file
            
            return thumbnail_url
        except ffmpeg.Error as e:
            raise Exception(f"Error generating thumbnail: {str(e)}")

# boto3 ffmpeg-python