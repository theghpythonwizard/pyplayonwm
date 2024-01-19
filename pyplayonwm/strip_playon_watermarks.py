import os
import re
from pathlib import Path

from .tools._episode_metadata import VideoMetadata
from moviepy.video.io.VideoFileClip import VideoFileClip

class StripPlayonWatermarks():

    def __init__(self, 
                 full_input_file_path,
                 execution_directory="",
                 full_output_file_path="",
                 start_remove_time=5,
                 end_remove_time=5):
        self.vfi = VideoMetadata(full_input_file_path)._metadata()
        print(self.vfi)
        self.input_file = full_input_file_path
        print(self.input_file)
        if full_output_file_path == "":
            if execution_directory == "":
                script_directory = [i for i in Path(__file__).resolve().parents]
                if str(script_directory[0]).endswith("playonwm/pyplayonwm"):
                    execution_directory = str(script_directory[1])
                else:
                    execution_directory = str(script_directory[0])
            generated_full_output_file_path = os.path.join(execution_directory, "processed")
            if not Path(generated_full_output_file_path).is_dir():
                os.mkdir(generated_full_output_file_path)
            input_file_name_only = Path(full_input_file_path).name
            self.output_file = os.path.join(generated_full_output_file_path, input_file_name_only)
        else:
            self.output_file = full_output_file_path
        self.start_time = start_remove_time
        self.end_time = self.vfi['duration'] - end_remove_time

    def trim_video(self):
        video_clip = VideoFileClip(self.input_file)
        trimmed_clip = video_clip.subclip(self.start_time, self.end_time)
        trimmed_clip.write_videofile(self.output_file, codec='libx264', audio_codec='aac')
        video_clip.close()
    