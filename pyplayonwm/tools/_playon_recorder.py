import json
import os
import requests
from typing import List
from ._string_tools import RedString, YellowString, GreenString
from ..string_tools import StringColor

class PlayOnLogin:

    def __init__(self):
        self.api_login_url = "https://api.playonrecorder.com/v3/login"
        self.api_list_url = "https://api.playonrecorder.com/v3/library/all"
        # self.headers = {'Cookie': 'laravel_session=RyFMrZ8EapUGtuRovAT6Xhew4vSGUeDfUGhavRA6'}
        playon_login_email = os.environ.get('PLAYON_LOGIN_EMAIL')
        playon_login_password = os.environ.get('PLAYON_LOGIN_PASSWORD')
        if not playon_login_email:
            print('run `export PLAYON_LOGIN_EMAIL={playon email used to login to web ui}`')
            exit(1)
        if not playon_login_password:
            print('run `export PLAYON_LOGIN_PASSWORD={playon password used to login to web ui}`')
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
    
class PlayOnRecorder:

    def __init__(self):
        self.recorded_list = []
        self.api_list_url = "https://api.playonrecorder.com/v3/library/all"
        self.sc = StringColor()
        

    def _get_recorded_list(self, token):
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(self.api_list_url, headers=headers)
        content = json.loads(response.content)
        return content

    def _get_id_from_name(self, fname, entries: List):
        for entry in entries:
            if entry['Name'] in fname:
                return entry['ID']
            else:
                continue
        return None

    def _generate_full_recording_name(self, name):
        series = name['Series']
        video_name = name['Name']
        if series == None:
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
    
    def _get_download_data_from_library_url(self, url, headers):
        response = requests.get(url, headers=headers)
        content = response.json()
        return content
    
    def _download_content(self, url, full_file_path):
        response = requests.get(url, stream=True)
        path_directory = os.path.split(full_file_path)[0]
        if not os.path.exists(path_directory):
            os.mkdir(path_directory)
        if response.status_code == 200:
            if not os.path.exists(full_file_path):
                with open(full_file_path, 'wb') as video_file:
                    video_file.write(response.content)
                return (response.status_code, True)
            else:
                print(self.sc.yellow_string(f"File already exists: {full_file_path}"))
                print(self.sc.yellow_string("To reattempt, delete the file and try again."))
                return (response.status_code, False)
        else:
            return False
        

#   CDS_HOSTNAME = 'cds.playonrecorder.com'
#   CDS_BASE = f'https://{CDS_HOSTNAME}/api/v6/'

#   CDS_HOSTNAME_LOCAL = 'cds-au.playonrecorder.com'
#   CDS_BASE_LOCAL = f'https://{CDS_HOSTNAME_LOCAL}/api/v6/'




