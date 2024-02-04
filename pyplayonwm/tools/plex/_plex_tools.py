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
        # pp(season_data)
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

    def _change_series_episode_title(self, token, base_url, episode_id, title, sort_title, originally_available, summary):
        # PUT https://10-60-2-53.cc91b1338a6441cfba05d16c3c377acb.plex.direct:32400/library/sections/2/all?type=4&id=11979&includeExternalMedia=1&title.value=Back%20from%20Vacation%20Test&titleSort.value=Back%20from%20Vacation%20Test&summary.value=Karen%20and%20Jim%20had%20their%20first%20big%20fight%20in%20the%20relationship.%20Karen%20had%20been%20living%20in%20a%20hotel%20since%20taking%20her%20job%20in%20Scranton.%20When%20she%20decided%20to%20live%20next%20door%20to%20Jim%2C%20he%20took%20it%20as%20the%20next%20step%20to%20living%20together%20and%20that%20was%20too%20fast.%20She%20was%20not%20pleased%20with%20his%20response.%20Test.&originallyAvailableAt.value=2008-01-04&title.locked=1&titleSort.locked=1&originallyAvailableAt.locked=1&summary.locked=1&X-Plex-Product=Plex%20Web&X-Plex-Version=4.122.0&X-Plex-Client-Identifier=ms1zznjif89n4y2yge91zgsq&X-Plex-Platform=Chrome&X-Plex-Platform-Version=120.0&X-Plex-Features=external-media%2Cindirect-media%2Chub-style-list&X-Plex-Model=hosted&X-Plex-Device=OSX&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1920x934%2C1920x1080&X-Plex-Token=MR2F3K9781grnyPC_3dt&X-Plex-Language=en&X-Plex-Session-Id=e3638848-278c-48bc-8cac-b8fca68c2660

        # I'm going to always set type as 4, because I don't really know what it does, but it works
        # I can inspect other updates to make sure in the future
        # I should also pass in the library id, but I'm going to hard code it for now, because I know it works in my scenario
        # What I really need for the update is...
        # Title, Sort Title, Originally Available, and Summary
        # I need external logic to figure out if the current metadata matches the file name.
        library_id = "2"
        title = title.replace(" ", "%20")
        sort_title = sort_title.replace(" ", "%20")
        originally_available = originally_available.replace(" ", "%20")
        summary = summary.replace(" ", "%20")
        update_url = (
            f"{base_url}library/sections/{library_id}/all?type=4"
            f"&id={episode_id}"
            f"&includeExternalMedia=1"
            f"&title.value={title}&title.locked=1"
            f"&summary.value={summary}&summary.locked=1"
            f"&titleSort.value={sort_title}&titleSort.locked=1"
            f"&originallyAvailableAt.value={originally_available}&originallyAvailableAt.locked=1"
            f"&X-Plex-Token={token}"
        )
        response = requests.put(update_url)
        if response.status_code == 200:
            return True
        return False

    def _is_metadata_correct(self, single_season_data: dict):
        episodes_data = single_season_data['MediaContainer']['Video']
        for episode in episodes_data:
            title = episode['@title']
            episode_fp = episode['Media']['Part']['@file']
            if title not in episode_fp:
                return False
        return True

    def _filtered_data_for_updates(self, token, base_url, single_season_data: dict):
        fields_needed_for_update = []

        episodes_data = single_season_data['MediaContainer']['Video']
        for episode in episodes_data:
            episode_fp = episode['Media']['Part']['@file']
            if "part" in os.path.basename(episode_fp).split("-")[-1].lower():
                title = os.path.basename(episode_fp).split("-")[-1].split(".mp4")[0].strip()
            else:
                title = episode['@title'].strip()
            sort_title = title
            try:
                originally_available = episode['@originallyAvailableAt']
            except KeyError:
                originally_available = ""
            episode_summary = episode['@summary']
            episode_id = episode['@ratingKey']
            if title in episode_fp:
                fields_needed_for_update.append({
                    'title': os.path.basename(episode_fp).split("-")[-1].split(".mp4")[0],
                    'sort_title': sort_title,
                    'originally_available': originally_available,
                    'episode_fp': episode_fp,
                    'episode_summary': episode_summary,
                    'episode_id': episode_id
                })
            elif title not in episode_fp:
                # I know this is going to be fragile. I'm solving for a specific use case.
                # I can try and figure out a way to generalize this later.
                # I'm sure there's a better way to look for the title from the file path
                # and find it in the episodes_data, but this works for now.
                actual_title = os.path.basename(episode_fp).split("-")[-1].split(".mp4")[0]
                title_match = os.path.basename(episode_fp.lower()).split("-")[-1].split(".mp4")[0].split("part")[0].lstrip()
                if title_match.lower().startswith("the"):
                    title_match = title_match[3:].lstrip()
                acutal_sort_title = actual_title
                try:
                    acutal_originally_available = [v['@originallyAvailableAt'] for v in episodes_data if title_match in v['@title'].lower()][0]
                except IndexError:
                    acutal_originally_available = ""
                try:
                    actual_episode_summary = [v['@summary'] for v in episodes_data if title_match in v['@title'].lower()][0]
                except IndexError:
                    actual_episode_summary = ""
                fields_needed_for_update.append({
                    'title': actual_title,
                    'sort_title': acutal_sort_title,
                    'originally_available': acutal_originally_available,
                    'episode_fp': episode_fp,
                    'episode_summary': actual_episode_summary,
                    'episode_id': episode_id
                })
        return fields_needed_for_update
