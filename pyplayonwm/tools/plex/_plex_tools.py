import os
import logging
import requests
from urllib.parse import urljoin
import xmltodict
import re
from pprint import pprint as pp

from ...logger_default import LoggerDefault
from ...string_tools import StringColor
from ...helpers import HelperTools

logger = logging.getLogger(__name__)
logger = LoggerDefault(log_file="pyplayonwm.log").set_logger(logger)


class Plex:

    def __init__(self):
        self.sc = StringColor()
        self.h = HelperTools()
        self.config_file = os.path.join(self.h.git_root(), 'pyplayonwm', 'tools', 'plex', 'config')
        self.token = self._get_plex_token()

    def _get_plex_token(self):
        token = os.environ.get('PLEX_TOKEN')
        if not token:
            logger.info(self.sc.red_string("PLEX_TOKEN not found in environment variables"))
            logger.info(self.sc.red_string("run 'export PLEX_TOKEN=$(sed -n \'1p\' .plex_secrets)'"))
            exit(1)
        return token

    def _get_base_url(self):
        base_url = ""
        with open(self.config_file, 'r') as config:
            for line in config:
                if 'PLEX_BASE_URL' in line:
                    base_url = line.split('=')[1].strip().strip('"')
        if not base_url:
            logger.info(self.sc.red_string("PLEX_BASE_URL not found in config"))
            exit(1)
        return base_url

    def _get_library(self, token, base_url):
        url_token = f"?X-Plex-Token={token}"
        url = urljoin(base_url, f"library/sections{url_token}")
        response = requests.get(url)
        if response:
            response_dict = xmltodict.parse(response.text)
        return response_dict

    def _get_movie_library(self, token, base_url, library_data: dict):
        libraries = library_data['MediaContainer']['Directory']
        movie_library_path = ""
        for library in libraries:
            if library['@type'] == 'movie':
                movie_library_path = library['@key']
        url_token = f"?X-Plex-Token={token}"
        url = urljoin(base_url, f"/library/sections/{movie_library_path}/all{url_token}")
        response = requests.get(url)
        if response:
            response_dict = xmltodict.parse(response.text)
        return response_dict

    def _get_series_library(self, token, base_url, library_data: dict):
        libraries = library_data['MediaContainer']['Directory']
        tv_library_path = ""
        for library in libraries:
            if library['@type'] == 'show':
                tv_library_path = library['@key']
        url_token = f"?X-Plex-Token={token}"
        url = urljoin(base_url, f"library/sections/{tv_library_path}/all{url_token}")
        response = requests.get(url)
        if response:
            response_dict = xmltodict.parse(response.text)
        return response_dict

    def _get_seasons_library_from_series(self, token, base_url, show, series_data: dict):
        series = series_data['MediaContainer']['Directory']
        season_library_path = ""
        for item in series:
            if item['@title'].lower() == show.lower():
                season_library_path = item['@key']
        url_token = f"?X-Plex-Token={token}"
        url = urljoin(base_url, f"{season_library_path}{url_token}")
        response = requests.get(url)
        if response:
            response_dict = xmltodict.parse(response.text)
        return response_dict

    def _get_episodes_from_season(self, token, base_url, season, season_data: dict):
        seasons = season_data['MediaContainer']['Directory']
        episode_library_path = ""
        for item in seasons:
            if item['@title'] == 'All episodes':
                continue
            season_number = re.search(r'\d+', item['@title']).group()
            if season_number == season.lower():
                episode_library_path = item['@key']
        url_token = f"?X-Plex-Token={token}"
        url = urljoin(base_url, f"{episode_library_path}{url_token}")
        response = requests.get(url)
        if response:
            response_dict = xmltodict.parse(response.text)
        return response_dict

    def _refresh_episode_metadata(self, token, base_url, episode_data: dict):
        episode_name = episode_data['@title']
        episode_guid = episode_data['@guid']
        episode_id = episode_data['@ratingKey']
        update_url = f"{base_url}library/metadata/{episode_id}/match?guid={episode_guid}&name={episode_name}&X-Plex-Token={token}"
        response = requests.put(update_url)
        if response.status_code == 200 and response.text:
            return True
        return False

    def _change_series_episode_title(self, token, base_url, episode_data: dict):
        # PUT https://10-60-2-53.cc91b1338a6441cfba05d16c3c377acb.plex.direct:32400/library/sections/2/all?type=4&id=11919&includeExternalMedia=1&title.value=Pilot%20Test&title.locked=1&X-Plex-Product=Plex%20Web&X-Plex-Version=4.122.0&X-Plex-Client-Identifier=ms1zznjif89n4y2yge91zgsq&X-Plex-Platform=Chrome&X-Plex-Platform-Version=120.0&X-Plex-Features=external-media%2Cindirect-media%2Chub-style-list&X-Plex-Model=hosted&X-Plex-Device=OSX&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1920x934%2C1920x1080&X-Plex-Token=MR2F3K9781grnyPC_3dt&X-Plex-Language=en&X-Plex-Session-Id=ab9137e4-d253-4102-8e67-813206644b70 HTTP/1.1

        # I'm going to always set type as 4, because I don't really know what it does, but it works
        # I can inspect other updates to make sure in the future
        # I should also pass in the library id, but I'm going to hard code it for now, because I know it works in my scenario
        # What I really need for the update is...
        # Title, Sort Title, Originally Available, and Summary
        # I need external logic to figure out if the current metadata matches the file name.
        library_id = "2"
        episode_name = episode_data['@title']
        episode_guid = episode_data['@guid']
        episode_id = episode_data['@ratingKey']
        new_name = "Pilot Test"
        new_name = f"{new_name}".replace(" ", "%20")
        summary = "this is a test"
        summary = f"{summary}".replace(" ", "%20")
        update_url = f"{base_url}library/sections/{library_id}/all?type=4&id={episode_id}&includeExternalMedia=1&summary.value={summary}&summary.locked=1&X-Plex-Token={token}"

        response = requests.put(update_url)
        print(response.status_code, response.text)
        import pdb
        pdb.set_trace()
        if response.status_code == 200 and response.text:
            return True
        return False
