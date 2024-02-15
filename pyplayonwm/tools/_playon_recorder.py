import json
import os
import re
import requests
from retry import retry
import subprocess
import shlex
import sys
import time
from typing import List
from pprint import pprint as pp
# from ._string_tools import RedString, YellowString, GreenString
from ..string_tools import StringColor


class PlayOnLogin:

    def __init__(self):
        self.api_login_url = "https://api.playonrecorder.com/v3/login"
        self.api_list_url = "https://api.playonrecorder.com/v3/library/all"
        # self.headers = {'Cookie': 'laravel_session=RyFMrZ8EapUGtuRovAT6Xhew4vSGUeDfUGhavRA6'}
        playon_login_email = os.environ.get('PLAYON_LOGIN_EMAIL')
        playon_login_password = os.environ.get('PLAYON_LOGIN_PASSWORD')
        if not playon_login_email:
            print('run `export PLAYON_LOGIN_EMAIL=$(sed -n 1p .secrets)`')
            exit(1)
        if not playon_login_password:
            print('run `export PLAYON_LOGIN_PASSWORD=$(sed -n 2p .secrets)`')
            exit(1)

        self.login_payload = {
            'email': f'{playon_login_email}',
            'password': f'{playon_login_password}'
        }

    def _login_token(self):
        token_text = requests.post(self.api_login_url, data=self.login_payload).text
        token_data = json.loads(token_text)
        token = token_data['data']['token']
        return token

    def _login_headers(self):
        token = self._login_token()
        headers = {
            'Authorization': f'Bearer {token}'
        }
        return headers


class PlayOnRecorder:

    def __init__(self):
        self.recorded_list = []
        self.api_list_url = "https://api.playonrecorder.com/v3/library/all"
        self.sc = StringColor()

    @retry(tries=2, delay=1, backoff=2)
    def _get_recorded_list(self, token="", headers=None):
        if token:
            headers = {
                'Authorization': f'Bearer {token}'
            }
        if headers:
            headers = headers
        try:
            response = requests.get(self.api_list_url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}")
            content = json.loads(response.content)
            return content
        except Exception as e:
            raise Exception(f"Error occurred during request: {str(e)}")

    def _get_id_from_name(self, fname, entries: List):
        for entry in entries:
            if entry['Series'] is not None:
                if entry['Name'] in fname and entry['Series'] in fname:
                    return entry['ID']
            elif entry['Series'] is None:
                if entry['Name'] in fname:
                    return entry['ID']
            else:
                continue
        return None

    def _generate_full_recording_name(self, name):
        series = name['Series']
        video_name = name['Name']
        if series is None:
            full_name = f"{video_name}"
        else:
            full_name = f"{series} - {video_name}"
        return full_name

    def _generate_library_url(self, id):
        generated_url = f"https://api.playonrecorder.com/v3/library/{id}/download"
        return generated_url

    def _gen_cloudfront_download_url(self, url, expires, signature, key_pair_id):
        if url.endswith('mp4'):
            return f"{url}?Expires={expires}&Signature={signature}&Key-Pair-Id={key_pair_id}"
        else:
            raise Exception('This is not a download url, the url should end with .mp4')

    def _get_download_data_from_library_url(self, url, headers, logger):
        response = requests.get(url, headers=headers)
        if response and response.status_code == 200:
            logger.info(self.sc.green_string(f"Download url data retreived for \"{url}\""))
            content = response.json()
            return content
        else:
            print(self.sc.red_string(f"Download url data retreival failed for \"{url}\""))
            return None

    def _download_content(self, url, full_file_path, logger):
        response = requests.get(url, stream=True)
        path_directory = os.path.split(full_file_path)[0]
        if not os.path.exists(path_directory):
            os.mkdir(path_directory)
        if response.status_code == 200:
            try:
                if not os.path.exists(full_file_path):
                    with open(full_file_path, 'wb') as video_file:
                        video_file.write(response.content)
                    return (response.status_code, True)
                else:
                    logger.info(self.sc.yellow_string(f"File already exists: {full_file_path}"))
                    logger.info(self.sc.yellow_string("To reattempt, delete the file and try again."))
                    return (response.status_code, False)
            except KeyError:
                logger.info(self.sc.red_string(f"Failed to download \"{full_file_path}\""))
                logger.info(response)
                return (response.status_code, False)
            except TypeError:
                logger.info(self.sc.red_string(f"Failed to download \"{full_file_path}\""))
                logger.info(response)
                return (response.status_code, False)
        else:
            return False

    def _get_fps_from_ffmpeg_output(self, full_file_path):
        result = subprocess.Popen(shlex.split(f'ffmpeg -i \"{full_file_path}\"'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = result.communicate()
        fps_match = re.search(r"Stream #0:0.*?(\d+\.\d+) fps", stderr)
        if fps_match:
            fps = float(fps_match.group(1))
            return fps

    def _generate_delete_url(self, id):
        return f"https://api.playonrecorder.com/v3/library/{id}"

    def _delete_processed_recording_from_cloud_storage(self, logger, video_name_to_delete="", video_list_to_delete=[], headers={}):
        # DELETE https://api.playonrecorder.com/v3/library/14866867 HTTP/2.0
        if not headers:
            headers = PlayOnLogin()._login_headers()
        recorded_list = self._get_recorded_list(headers=headers)
        if not video_name_to_delete and not video_list_to_delete:
            logger.info("No video name provided, provide a video name to delete or list of names to delete.")
            sys.exit(1)
        for video in video_list_to_delete:
            video_id = self._get_id_from_name(video, recorded_list['data']['entries'])
            if video_id is not None:
                logger.info(self.sc.red_string(f"Preparing to delete {video} from cloud storage. You have 10 seconds to cancel."))
                time.sleep(10)
                delete_url = self._generate_delete_url(video_id)
                response = requests.delete(delete_url, headers=headers)
                logger.info(self.sc.green_string(f"Deletion of {video} from cloud storage is Success = {json.loads(response.text)['success']}"))
            else:
                logger.info(self.sc.yellow_string(f"Video {video} not found in recorded list. It must have already been deleted."))
