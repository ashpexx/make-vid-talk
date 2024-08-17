import grpc
from concurrent import futures
import service_pb2
import service_pb2_grpc
from flask import send_file
import tempfile
import os
import datetime
import subprocess
from doservices import DigitalOceanService
from moviepy.editor import VideoFileClip
from grpc_reflection.v1alpha import reflection


class VideoService(service_pb2_grpc.VideoServiceServicer):
    def __init__(self):
        self.do_service = DigitalOceanService()

    def execute_command(self, command: list) -> None:
        subprocess.run(command, check=True)

    def infer(self, video_url, audio_url):
        temp_output_path = tempfile.mktemp(suffix='.mp4')
        command = [
            "python", 
            "inference.py",
            f"--face={video_url}",
            f"--audio={audio_url}",
            f"--outfile={temp_output_path}"
        ]

        self.execute_command(command)

        video = VideoFileClip(temp_output_path)
        output_file = tempfile.mktemp(suffix='.mp4')
        video.write_videofile(output_file, codec="libx264", audio_codec="aac")

        os.remove(temp_output_path)
        return output_file

    def ServerActive(self, request, context):
        return service_pb2.StatusResponse(status='active', message='Server is running')

    def Upload(self, request_iterator, context):
        video_chunks = []
        audio_chunks = []
        print(request)
        for request in request_iterator:
            if request.video:
                video_chunks.append(request.video)
            if request.audio:
                audio_chunks.append(request.audio)
        
        if not video_chunks or not audio_chunks:
            context.set_details('Both video and audio files are required')
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.UploadResponse()

        video_file = b''.join(video_chunks)
        audio_file = b''.join(audio_chunks)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        video_slug = 'video'
        audio_slug = 'audio'

        video_url = self.do_service.upload_file(video_file, video_slug, 'video.mp4')
        audio_url = self.do_service.upload_file(audio_file, audio_slug, 'audio.mp3')

        try:
            self.do_service.validate_file_duration(video_url)
            self.do_service.validate_file_duration(audio_url)
        except ValueError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return service_pb2.UploadResponse()

        output_file = self.infer(video_url, audio_url)
        thumbnail_url = self.do_service.generate_thumbnail(video_url, '/tmp', 'user-thumbnail')

        with open(output_file, 'rb') as f:
            result_url = f.read()

        return service_pb2.UploadResponse(
            video_url=video_url,
            audio_url=audio_url,
            result_url=result_url.decode('utf-8'),
            thumbnail_url=thumbnail_url
        )

    def DeleteFile(self, request, context):
        try:
            self.do_service.delete_file(request.key)
            return service_pb2.StatusResponse(status='success', message='File deleted successfully')
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.StatusResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=500), options=[
		('grpc.max_send_message_length', 50 * 1024 * 1024),
		('grpc.max_receive_message_length', 50 * 1024 * 1024)
      	])
    service_pb2_grpc.add_VideoServiceServicer_to_server(VideoService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server is running...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
