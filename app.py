from flask import Flask, request, send_file, jsonify
import os
import datetime
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

app = Flask(_name_)

# Ensure temp directories exist
os.makedirs('results', exist_ok=True)

# Execute a CLI command
def execute_command(command: str) -> None:
    subprocess.run(command, check=True)

def infer(video_path, audio_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    output = f"results/result_{timestamp}.mp4"
    command = [
        "python", 
        "inference.py",
        f"--face={video_path}",
        f"--audio={audio_path}",
        f"--outfile={output}"
    ]

    execute_command(command)

    # Load the video
    video = VideoFileClip(output)
    
    # Create a temporary directory to store the output file
    output_dir = tempfile.mkdtemp()
    output_file = os.path.join(output_dir, f'allwebtool_result_{timestamp}.mp4')

    # Write the video to the output file with automatic codec selection
    video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    
    print("Video conversion successful.")
    
    return output_file

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Success! The API is up and running."})

@app.route('/generate', methods=['POST'])
def generate():
    segment_length = int(request.form.get('segment_length', 0))
    video = request.files.get('video')
    audio = request.files.get('audio')
    
    if not video or not audio:
        return jsonify({"error": "Both video and audio files are required."}), 400
    
    video_path = os.path.join('temp/video', video.filename)
    audio_path = os.path.join('temp/audio', audio.filename)
    
    video.save(video_path)
    audio.save(audio_path)

    output_file = infer(video_path, audio_path)
    return send_file(output_file, as_attachment=True)

if _name_ == '_main_':
    app.run(debug=True)
