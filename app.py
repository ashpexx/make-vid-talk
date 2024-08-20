from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import subprocess
from doservices import DigitalOceanService
from moviepy.editor import VideoFileClip
import aiofiles
import aiohttp

app = FastAPI()
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

@app.get("/")
async def server_active():
    return {"status": "active", "message": "Server is running"}

@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile):
    try:
        if not video or not audio:
            raise HTTPException(status_code=400, detail="Both video and audio files are required")

        video_slug = 'video'
        audio_slug = 'audio'

        # Upload files to DigitalOcean Spaces
        video_content = await video.read()
        audio_content = await audio.read()
        video_url = do_service.upload_file(video_content, video_slug, video.filename)
        audio_url = do_service.upload_file(audio_content, audio_slug, audio.filename)

        # Validate file durations
        try:
            do_service.validate_file_duration(video_url)
            do_service.validate_file_duration(audio_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Download files from URLs to temporary files
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as video_response:
                video_temp_file = await aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                await video_temp_file.write(await video_response.read())
                video_temp_path = video_temp_file.name

            async with session.get(audio_url) as audio_response:
                audio_temp_file = await aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                await audio_temp_file.write(await audio_response.read())
                audio_temp_path = audio_temp_file.name

        # Process video and generate output
        output_file = infer(video_temp_path, audio_temp_path)
        file_content = do_service.read_file_content(output_file)
        result_url = do_service.upload_file(file_content, "result", video.filename)
        thumbnail_url = do_service.generate_thumbnail(video_url, '/tmp', 'user-thumbnail')

        # Clean up temporary files
        os.remove(video_temp_path)
        os.remove(audio_temp_path)

        return {
            "video_url": video_url,
            "audio_url": audio_url,
            "result_url": result_url,
            "thumbnail_url": thumbnail_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{key}")
async def delete_file(key: str):
    try:
        do_service.delete_file(key)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
