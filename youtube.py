import yt_dlp as youtube_dl
from moviepy.editor import *
import os
import argparse

def download_clip(url, time_ranges, output_name_prefix):
    # Download options for youtube_dl
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': 'temp_video.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    # Fetch the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Check if the merged file exists
    if not os.path.exists('temp_video.mp4'):
        print("Error: Video not downloaded correctly!")
        return

    # Process each time range
    for idx, (start_time, end_time) in enumerate(time_ranges):
        # Slice the video
        main_clip = VideoFileClip('temp_video.mp4').subclip(start_time, end_time)

        # Load intro and outro if they exist, and concatenate
        clips_to_concatenate = []

        if os.path.exists('intro.mp4'):
            clips_to_concatenate.append(VideoFileClip('intro.mp4'))

        clips_to_concatenate.append(main_clip)

        if os.path.exists('outro.mp4'):
            clips_to_concatenate.append(VideoFileClip('outro.mp4'))

        final_clip = concatenate_videoclips(clips_to_concatenate, method='compose')

        # Generate unique output name for each clip
        output_name = f"{output_name_prefix}_{idx}.mp4"
        # Export the concatenated video
        final_clip.write_videofile(output_name, codec="libx264")

    # Remove temporary merged file
    os.remove('temp_video.mp4')

if __name__ == "__main__":
    # Use argparse to handle command line arguments
    parser = argparse.ArgumentParser(description='Download and process YouTube videos.')
    parser.add_argument('url', help='YouTube URL to download from.')
    parser.add_argument('time_ranges', nargs='+', help='Multiple time ranges in HH:MM:SS-HH:MM:SS format.')
    parser.add_argument('output_name_prefix', help='Prefix of the output file (e.g., output)')

    args = parser.parse_args()

    # Parse time_ranges
    time_ranges = [(tuple(map(int, time_range.split('-')[0].split(":"))),
                    tuple(map(int, time_range.split('-')[1].split(":")))) for time_range in args.time_ranges]

    download_clip(args.url, time_ranges, args.output_name_prefix)
