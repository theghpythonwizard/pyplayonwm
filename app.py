import json
import os
from pathlib import Path
import platform
import sys
import argparse
import requests

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input_path', help='file path for the video we want the water mark stripped from', required=False)
    parser.add_argument('-o', '--output_path', help='the name of the file you want to use. If none is defined. \
                        The file will be stripped of white space and placed a "processed" directory', required=False)
    parser.add_argument('-so', '--start_offset', help='start time offset. number of seconds to strip at the beginning.')
    parser.add_argument('-r', '--rename', help='rename episodes', type=bool, required=False)
    parser.add_argument('-fp', '--files_to_process', help='a list of files to process.', required=False)

    args = parser.parse_args()

    video_input_path = args.input_path
    video_output_path = args.output_path
    start_time_offset = args.start_offset
    files_to_process = args.files_to_process

    string_color = StringColor()

    # if not video_input_path and not files_to_process:
    #     print("You need to provide an '--input_path' or a '--files_to_process' to continue")
    #     exit(1)

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

    script_directory = [i for i in Path(__file__).resolve().parents]
    # print(script_directory)
    
    # if files_to_process:
    #     with open('files_to_process.txt') as f:
    #         file_paths = [line.strip() for line in f.readlines()]
    #         for file_path in file_paths:
    #             video_input_path = file_path
    #             print(video_input_path)
    #             if start_time_offset:
    #                 trimmer = spm.StripPlayonWatermarks(
    #                     video_input_path,
    #                     start_remove_time=start_time_offset
    #                 )
    #             else:
    #                 trimmer = spm.StripPlayonWatermarks(
    #                     video_input_path
    #                 )

    #             output = trimmer.trim_video()
    #             print(output)

    # else:
    #     if start_time_offset:
    #         trimmer = spm.StripPlayonWatermarks(
    #             video_input_path,
    #             start_remove_time=start_time_offset
    #         )
    #     else:
    #         trimmer = spm.StripPlayonWatermarks(
    #                 video_input_path
    #             )
        
    #     output = trimmer.trim_video()
    #     print(output) 

    #######
        
    ## good start, but for now just use it manually
    downloader = playon_downloader.PlayOnDownloader()
    playon_token = downloader.playon_token()
    # print(playon_token)

    video_entries = downloader.recorded_list(playon_token)
    
    h = helpers.HelperTools()
    processed_files = h.processed_files()
    # # for i in processed_files:
    # #     print(i)
    
    files_names_from_api = []
    for i in video_entries['data']['entries']:
        full_recording_name = h.recording_name(i)
        files_names_from_api.append(full_recording_name)

    files_to_process = h.files_to_process(processed_files, files_names_from_api)
    h.write_files_to_process(files_to_process)

    headers = {
        'Authorization': f'Bearer {playon_token}'
    }

    all_download_data = []
    for file in files_to_process:
        temp_data = {"url": "", "file_name": ""}
        file_name_with_extension = f"{file}.mp4"
        id = h.get_id(file, video_entries['data']['entries'])
        url = h.library_url(id)
        download_data = downloader.download_data(url, headers)
        if download_data['success']:
            url = download_data['data']['url']
            cloudfront_data = download_data['data']['data']
            cloudfront_url = h.download_url(url, cloudfront_data['CloudFront-Expires'], cloudfront_data['CloudFront-Signature'], cloudfront_data['CloudFront-Key-Pair-Id'])
            download_file_path = os.path.join(h.git_root(), "unprocessed", file_name_with_extension)
            temp_data['file_name'] = download_file_path
            temp_data['url'] = cloudfront_url
            all_download_data.append(temp_data)

    for data in all_download_data:
        fp = data['file_name']
        url = data['url']
        print(string_color.green_string(f"Attempting Download of {os.path.split(fp)[-1]} to {os.path.split(fp)[0]}"))
        downloaded = downloader.download_content(url, fp)
        if downloaded == 200:
            print(f"Download for {fp} complete.")


        

    
    
    # download_data_list = []
    # for file_url in file_urls_to_download:
    #     download_data = dt.download_data(file_url, headers)
    #     if download_data['success']:
    #         download_data_list.append(download_data)
    
    # pp(download_data_list)

    
    # resp = requests.get(url, headers=headers)
    # resp_json = resp.json()

    # if resp_json['success']:
    #     url = resp_json['data']['url']
    #     cloudfront_data = resp_json['data']['data']
    #     cloudfront_url = h.download_url(url, cloudfront_data['CloudFront-Expires'], cloudfront_data['CloudFront-Signature'], cloudfront_data['CloudFront-Key-Pair-Id'])
    #     fr = requests.get(cloudfront_url)
    #     with open("test.mp4", 'wb') as vf:
    #         vf.write(fr.content)
    
    

    # download_url = r_content['data']['url']
    # download_params = r_content['data']['data']
    # # download_headers['CloudFront-Expires'] = str(download_headers['CloudFront-Expires'])
    
    # download_file = requests.get(download_url, headers=headers, params=download_params, stream=True)
    # print(download_file.status_code, download_file.content)
    # with open("test.mp4", 'wb') as video_file:
    #     for chunk in download_file.iter_content(chunk_size=8192):
    #         if chunk:
    #             video_file.write(chunk)

    # print(file_urls_to_download)
        
    #######
    
    # test_video_url = login.generate_download_url(video_entries['data']['entries'][2])
    # print(test_video_url)

    # destination_file_path = "/Users/jasonschultheis/Downloads/Princess Mononoke.mp4"

    # download_vf = login.download_video_file(token, test_video_url, destination_file_path)
    # print(download_vf.text)
    # # for video_entry in video_entries['data']['entries']:
    # #     login.generate_download_url(video_entry)



    