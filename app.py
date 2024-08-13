from flask import Flask, request, render_template, send_file
import os
import shutil
import subprocess
import random

app = Flask(_name_)

# Ensure temp directories exist
os.makedirs('temp/video', exist_ok=True)
os.makedirs('temp/audio', exist_ok=True)
os.makedirs('results', exist_ok=True)

def convert(segment_length, video_path, audio_path):
    if segment_length is None:
        segment_length = 0
    print(video_path, audio_path)

    if segment_length != 0:
        video_segments = cut_video_segments(video_path, segment_length)
        audio_segments = cut_audio_segments(audio_path, segment_length)
    else:
        video_segments = [move_file(video_path, 'temp/video')]
        audio_segments = [move_file(audio_path, 'temp/audio')]

    processed_segments = []
    for i, (video_seg, audio_seg) in enumerate(zip(video_segments, audio_segments)):
        processed_output = process_segment(video_seg, audio_seg, i)
        processed_segments.append(processed_output)

    output_file = f"results/output_{random.randint(0, 1000)}.mp4"
    concatenate_videos(processed_segments, output_file)

    # Remove temporary files
    cleanup_temp_files(video_segments + audio_segments)

    return output_file

def cleanup_temp_files(file_list):
    for file_path in file_list:
        if os.path.isfile(file_path):
            os.remove(file_path)

def cut_video_segments(video_file, segment_length):
    temp_directory = 'temp/video'
    shutil.rmtree(temp_directory, ignore_errors=True)
    os.makedirs(temp_directory, exist_ok=True)
    segment_template = f"{temp_directory}/{random.randint(0, 1000)}_%03d.mp4"
    command = ["ffmpeg", "-i", video_file, "-c", "copy", "-f", "segment", "-segment_time", str(segment_length), segment_template]
    subprocess.run(command, check=True)

    video_segments = [segment_template % i for i in range(len(os.listdir(temp_directory)))]
    return video_segments

def cut_audio_segments(audio_file, segment_length):
    temp_directory = 'temp/audio'
    shutil.rmtree(temp_directory, ignore_errors=True)
    os.makedirs(temp_directory, exist_ok=True)
    segment_template = f"{temp_directory}/{random.randint(0, 1000)}_%03d.mp3"
    command = ["ffmpeg", "-i", audio_file, "-f", "segment", "-segment_time", str(segment_length), segment_template]
    subprocess.run(command, check=True)

    audio_segments = [segment_template % i for i in range(len(os.listdir(temp_directory)))]
    return audio_segments

def process_segment(video_seg, audio_seg, i):
    output_file = f"results/{random.randint(10, 100000)}_{i}.mp4"
    command = ["python", "inference.py", "--face", video_seg, "--audio", audio_seg, "--outfile", output_file]
    subprocess.run(command, check=True)
    return output_file

def concatenate_videos(video_segments, output_file):
    with open("segments.txt", "w") as file:
        for segment in video_segments:
            file.write(f"file '{segment}'\n")
    command = ["ffmpeg", "-f", "concat", "-i", "segments.txt", "-c", "copy", output_file]
    subprocess.run(command, check=True)

def move_file(src, dest_dir):
    shutil.move(src, os.path.join(dest_dir, os.path.basename(src)))
    return os.path.join(dest_dir, os.path.basename(src))

@app.route('/', methods=['GET'])
def index():
    return "Success! The API is up and running."

@app.route('/generate', methods=['POST'])
def generate():
    segment_length = int(request.form.get('segment_length', 0))
    video = request.files.get('video')
    audio = request.files.get('audio')
    
    if not video or not audio:
        return "Both video and audio files are required.", 400
    
    video_path = os.path.join('temp/video', video.filename)
    audio_path = os.path.join('temp/audio', audio.filename)
    
    video.save(video_path)
    audio.save(audio_path)

    output_file = convert(segment_length, video_path, audio_path)
    return send_file(output_file, as_attachment=True)

def create_app():
    return app
