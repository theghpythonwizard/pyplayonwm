import json
import os
from pathlib import Path
import platform
import sys
import argparse
# import requests
# import cv2
# import pytesseract


import warnings

from pprint import pprint as pp

from pyplayonwm import process_series, \
    rename_episode, strip_playon_watermarks as spm, \
    playon_login as pol

from pyplayonwm import helpers
from pyplayonwm import playon_downloader
from pyplayonwm.string_tools import StringColor

PLATFORM = platform.platform().split("-")[0]

def run_cmd(file_path, episode_name, output_dir):
    if "macOS" not in PLATFORM:
        i = process_series.RunHandbrakeCli(
                file_path,
                episode_name,
                output_dir
            )
        output = i.run()
        return output

class ApiDownloader:

    def __init__(self, downloader, playon_token):
        self.downloader = downloader
        self.playon_token = self.downloader.playon_token()
        self.headers = {
            'Authorization': f'Bearer {playon_token}'
        }

    def download_files_from_api(self):
        """this function will get a list of recorded files
        from the playon api and compare it to files that have
        already been processed in the local file data/processed_files.txt.
        If there are files from the api that are not in the processed_files.txt
        it will add those file name to a new file pyplayonwm/data/unprocessed_files.txt
        and then use those names to determine the download url and download
        each file to pyplayonwm/unprocessed/
        """

        print(string_color.cyan_string("Retreiving list of recorded files from PlayOn API"))
        video_entries = self.downloader.recorded_list(self.playon_token)
        
        h = helpers.HelperTools()
        processed_files = h.processed_files()
        
        files_names_from_api = []
        for i in video_entries['data']['entries']:
            full_recording_name = h.recording_name(i)
            files_names_from_api.append(full_recording_name)
        # for i in files_names_from_api:
        #     print(i)

        print(string_color.yellow_string("Determining which files need processing"))
        files_to_process = h.files_to_process(processed_files, files_names_from_api)
        if files_to_process:
            print(string_color.green_string("Writing files to process to pyplayonwm/data/unprocessed_files.txt"))
            h.write_files_to_process(files_to_process)
        else:
            print(string_color.yellow_string("No files to process."))

        all_download_data = []
        for file in files_to_process:
            temp_data = {"url": "", "file_name": ""}
            file_name_with_extension = f"{file}.mp4"
            id = h.get_id(file, video_entries['data']['entries'])
            url = h.library_url(id)
            print(string_color.cyan_string(f"Attempting retreival of download url data for \"{file_name_with_extension}\""))
            download_data = self.downloader.download_data(url, self.headers)
            if download_data['success']:
                url = download_data['data']['url']
                cloudfront_data = download_data['data']['data']
                print(string_color.green_string(f"Generating download url for \"{file_name_with_extension}\" with Playon Api data"))
                cloudfront_url = h.download_url(url, cloudfront_data['CloudFront-Expires'], cloudfront_data['CloudFront-Signature'], cloudfront_data['CloudFront-Key-Pair-Id'])
                download_file_path = os.path.join(h.git_root(), "unprocessed", file_name_with_extension)
                temp_data['file_name'] = download_file_path
                temp_data['url'] = cloudfront_url
                all_download_data.append(temp_data)

        for data in all_download_data:
            fp = data['file_name']
            url = data['url']
            print(string_color.cyan_string(f"Attempting Download of \"{os.path.split(fp)[-1]}\" to \"{os.path.split(fp)[0]}\""))
            status_code, downloaded = self.downloader.download_content(url, fp)
            if status_code == 200:
                if downloaded == True:
                    print(string_color.green_string(f"Download for \"{fp}\" complete."))
            elif status_code != 200:
                print(string_color.red_string(f"Download for \"{fp}\" failed."))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input_path', help='file path for the video we want the water mark stripped from', required=False)
    parser.add_argument('-o', '--output_path', help='the name of the file you want to use. If none is defined. \
                        The file will be stripped of white space and placed a "processed" directory', required=False)
    parser.add_argument('-so', '--start_offset', help='start time offset. number of seconds to strip at the beginning.', type=int, required=False)
    parser.add_argument('-r', '--rename', help='rename episodes', type=bool, required=False)
    parser.add_argument('-fp', '--files_to_process', help='a list of files to process.', required=False)

    args = parser.parse_args()

    video_input_path = args.input_path
    video_output_path = args.output_path
    start_time_offset = args.start_offset
    files_to_process = args.files_to_process

    string_color = StringColor()

    h = helpers.HelperTools()
    git_root = h.git_root()

    downloader = playon_downloader.PlayOnDownloader()
    playon_token = downloader.playon_token()
    api_downloader = ApiDownloader(downloader,
                                   playon_token)

    if not video_input_path and not files_to_process:
        api_downloader.download_files_from_api()
        unprocessed_files_path = os.path.join(git_root, "unprocessed")
        for file in sorted(os.listdir(unprocessed_files_path)):
            video_to_process = os.path.join(unprocessed_files_path, file)
            if start_time_offset:
                trimmer = spm.StripPlayonWatermarks(
                    video_to_process,
                    start_remove_time=start_time_offset
                )
                try:
                    trimmer.trim_video()
                    h.remove_file_from_unprocessed_tracker(file)
                    h.delete_after_processing(file)
                except KeyboardInterrupt:
                    sys.exit(1)
                except:
                    print(string_color.red_string(f"Failed to trim {video_to_process}"))
                
            else:
                trimmer = spm.StripPlayonWatermarks(
                    video_to_process
                )
                try:
                    trimmer.trim_video()
                    h.remove_file_from_unprocessed_tracker(file)
                    h.delete_after_processing(file)
                except KeyboardInterrupt:
                    sys.exit(1)
                except:
                    print(string_color.red_string(f"Failed to trim {video_to_process}"))
    
    if files_to_process:
        with open('files_to_process.txt') as f:
            file_paths = [line.strip() for line in f.readlines()]
            for file_path in file_paths:
                video_input_path = file_path
                if start_time_offset:
                    trimmer = spm.StripPlayonWatermarks(
                        video_input_path,
                        start_remove_time=start_time_offset
                    )
                    trimmer.trim_video()
                else:
                    trimmer = spm.StripPlayonWatermarks(
                        video_input_path
                    )

                trimmer.trim_video()

    elif video_input_path:
        if start_time_offset:
            trimmer = spm.StripPlayonWatermarks(
                video_input_path,
                start_remove_time=start_time_offset
            )
            trimmer.trim_video()
        else:
            trimmer = spm.StripPlayonWatermarks(
                    video_input_path
                )
        
            trimmer.trim_video()

    ## This was written when I was using WSL on windows and
    ## Having issue getting ffmpeg to work.
    ## ffmpeg is working fine on macOS
    ## I'll likely remove all the handbrake code 
    ## in favor of moviepy soon.
    ## just commenting it out for now
    # for episode in os.listdir(input_dir):
    #     print(episode)
    #     try:
    #         output = run_cmd(input_dir, episode, output_path)
    #         print(output)
    #         if args.rename:
    #             rename_episode.rename(os.path.join(output_path, episode))
    #     except KeyboardInterrupt:
    #         sys.exit(1)