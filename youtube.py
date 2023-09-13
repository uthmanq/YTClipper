import yt_dlp as youtube_dl
from moviepy.editor import *
import os
import argparse

def sections_callback(info_dict, ydl):
    # Convert the global time_ranges to the format yt-dlp expects.
    sections = []
    for idx, (start_time, end_time) in enumerate(time_ranges):
        section = {
            "start_time": sum(x * int(t) for x, t in zip([3600, 60, 1], start_time)),
            "end_time": sum(x * int(t) for x, t in zip([3600, 60, 1], end_time))
        }
        sections.append(section)
    return sections

def download_and_process_clip(url, time_ranges, output_name_prefix):
    for idx, (start_time, end_time) in enumerate(time_ranges):

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': f'temp_video_{idx}.%(ext)s',
            'merge_output_format': 'mp4',
            'download_ranges': sections_callback
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_path = f'temp_video_{idx}.mp4'
        main_clip = VideoFileClip(video_path)

        clips_to_concatenate = []

        if os.path.exists('intro.mp4'):
            clips_to_concatenate.append(VideoFileClip('intro.mp4'))

        clips_to_concatenate.append(main_clip)

        if os.path.exists('outro.mp4'):
            clips_to_concatenate.append(VideoFileClip('outro.mp4'))

        final_clip = concatenate_videoclips(clips_to_concatenate, method='compose')
        output_name = f"{output_name_prefix}_{idx}.mp4"
        final_clip.write_videofile(output_name, codec="libx264")
        os.remove(video_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and process YouTube video sections.')
    parser.add_argument('url', help='YouTube URL to download from.')
    parser.add_argument('time_ranges', nargs='+', help='Multiple time ranges in HH:MM:SS-HH:MM:SS format.')
    parser.add_argument('output_name_prefix', help='Prefix of the output file (e.g., output)')
    args = parser.parse_args()

    global time_ranges
    time_ranges = [(tuple(map(int, time_range.split('-')[0].split(":"))),
                    tuple(map(int, time_range.split('-')[1].split(":")))) for time_range in args.time_ranges]

    download_and_process_clip(args.url, time_ranges, args.output_name_prefix)
