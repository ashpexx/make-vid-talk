from flask import Flask, request, jsonify, send_file, abort
import tempfile
import os
import datetime
import subprocess
from doservices import DigitalOceanService
from moviepy.editor import VideoFileClip
from tempfile import NamedTemporaryFile
import requests

app = Flask(__name__)
do_service = DigitalOceanService()

# Function to execute a CLI command
def execute_command(command: list) -> None:
    subprocess.run(command, check=True)

# Function to handle video processing
def infer(video_source, audio_target):
    temp_output_path = tempfile.mktemp(suffix='.mp4')
    command = [
        "python", 
        "inference.py",
        f"--face={video_source}",
        f"--audio={audio_target}",
        f"--outfile={temp_output_path}"
    ]

    execute_command(command)

    # Load the processed video
    video = VideoFileClip(temp_output_path)
    output_file = tempfile.mktemp(suffix='.mp4')

    # Save the processed video with desired codec and settings
    video.write_videofile(output_file, codec="libx264", audio_codec="aac")

    # Clean up the temporary file created by inference
    os.remove(temp_output_path)

    return output_file

@app.route('/', methods=['GET'])
def server_active():
    return jsonify({'status': 'active', 'message': 'Server is running'})

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'video' not in request.files or 'audio' not in request.files:
            abort(400, 'Both video and audio files are required')
        
        video_file = request.files['video']
        audio_file = request.files['audio']

        if not video_file or not audio_file:
            abort(400, 'Both video and audio files are required')

        video_slug = 'video'
        audio_slug = 'audio'
        print(video_file, audio_file)
        # Upload files to DigitalOcean Spaces
        video_url = do_service.upload_file(video_file.read(), video_slug, video_file.filename)
        audio_url = do_service.upload_file(audio_file.read(), audio_slug, audio_file.filename)

        # Validate file durations
        try:
            do_service.validate_file_duration(video_url)
            do_service.validate_file_duration(audio_url)
        except ValueError as e:
            abort(400, str(e))

        # Download files from URLs to temporary files
        with NamedTemporaryFile(delete=False, suffix='.mp4') as video_temp_file, \
             NamedTemporaryFile(delete=False, suffix='.wav') as audio_temp_file:
            video_temp_file.write(requests.get(video_url).content)
            audio_temp_file.write(requests.get(audio_url).content)
            video_temp_path = video_temp_file.name
            audio_temp_path = audio_temp_file.name

        # Process video and generate output
        output_file = infer(video_temp_path, audio_temp_path)
        print(output_file)
        file_content = do_service.read_file_content(output_file)
        audio_url = do_service.upload_file(file_content, "result", video_file.filename)
        thumbnail_url = do_service.generate_thumbnail(video_url, '/tmp', 'user-thumbnail')

        # Clean up temporary files
        os.remove(video_temp_path)
        os.remove(audio_temp_path)

        return jsonify({
            'video_url': video_url,
            'audio_url': audio_url,
            'result_url': output_file,
            'thumbnail_url': thumbnail_url
        })
    except Exception as e:
        print(e)
        abort(500, str(e))

@app.route('/delete/<string:key>', methods=['DELETE'])
def delete_file(key):
    try:
        do_service.delete_file(key)
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        abort(500, str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860)