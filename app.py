import os
import subprocess
import tempfile
import gradio as gr
from moviepy.editor import VideoFileClip

# execute a CLI command
def execute_command(command: str) -> None:
    subprocess.run(command, check=True)


def infer(video_source, audio_target):
    
    output = "results/result.mp4"
    command = [
      f"python", 
      f"inference.py",
      f"--face={video_source}",
      f"--audio={audio_target}",
      f"--outfile={output}"
    ]

    execute_command(command)

    input_file = output  # Replace with the path to your input video
    
    # Create a temporary directory to store the output file
    output_dir = tempfile.mkdtemp()
    output_file = os.path.join(output_dir, 'output_video.mp4')

    # Load the video
    video = VideoFileClip(input_file)
    
    # Write the video to the output file with automatic codec selection
    video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    
    print("Video conversion successful.")
   
    
    return output_file

css="""
#col-container{
    margin: 0 auto;
    max-width: 720px;
    text-align: left;
}
"""
    
with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col-container"):
        gr.HTML("""
        <h2 style="text-align: center;">Video ReTalking</h2>
        <p style="text-align: center;">
            Audio-based Lip Synchronization for Talking Head Video Editing in the Wild
        </p>
                """)

        with gr.Row():
            with gr.Column():
                video_source = gr.Video(label="Source Video", type="filepath")
                audio_target = gr.Audio(label="Audio Target", type="filepath")
        
                submit_btn = gr.Button("Submit")

                gr.Examples(
                  label="Examples",
                  examples=[
                    ["examples/face/1.mp4", "examples/audio/1.wav"],
                    ["examples/face/2.mp4", "examples/audio/1.wav"],
                    ["examples/face/3.mp4", "examples/audio/2.wav"],
                    ["examples/face/4.mp4", "examples/audio/2.wav"], 
                    ["examples/face/5.mp4", "examples/audio/1.wav"]
                  ],
                  fn=infer,
                  inputs=[video_source, audio_target],
                  outputs=[result]
                )
            
            with gr.Column():
                result = gr.Video(label="Result")

            
    submit_btn.click(fn=infer, inputs=[video_source, audio_target], outputs=[result])
    
demo.queue(max_size=12).launch()
