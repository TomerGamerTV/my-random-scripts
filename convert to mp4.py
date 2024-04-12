import os
import subprocess

# Make sure you have ffmpeg installed and added to PATH!

def convert_videos(input_dir, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all video files in the input directory
    video_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    for video_file in video_files:
        # Generate the output file path
        output_file = os.path.join(output_dir, os.path.splitext(video_file)[0] + '.mp4')

        # Construct the FFmpeg command
        ffmpeg_command = f'ffmpeg -i {os.path.join(input_dir, video_file)} -c:v hevc_nvenc -q:v 0 {output_file}'

        # Execute the FFmpeg command
        subprocess.call(ffmpeg_command, shell=True)

    print('Video conversion completed!')

# Provide the input and output directory paths here
input_directory = '.'  # Current directory
output_directory = './converted_videos'

# Run the conversion script
convert_videos(input_directory, output_directory)