from .tools.plex._plex_tools import Plex


class PlexTools:

    def __init__(self):
        self.plex = Plex()
        self.token = self.plex.token

    def get_plex_token(self):
        return self.token

    @property
    def base_url(self):
        return self.plex._get_base_url()

    def get_library(self, token, base_url):
        return self.plex._get_library(token, base_url)

    def get_movie_library(self, token, base_url, library_data: dict):
        return self.plex._get_movie_library(token, base_url, library_data)

    def get_series_library(self, token, base_url, library_data: dict):
        return self.plex._get_series_library(token, base_url, library_data)

    def get_seasons_library_from_series(self, token, base_url, show, series_data: dict):
        return self.plex._get_seasons_library_from_series(token, base_url, show, series_data)

    def get_episodes_from_season(self, token, base_url, season, season_data: dict):
        return self.plex._get_episodes_from_season(token, base_url, season, season_data)

    def refresh_episode_metadata(self, token, base_url, episode_data: dict):
        return self.plex._refresh_episode_metadata(token, base_url, episode_data)

    def change_series_episode_title(self, token, base_url, episode_data: dict):
        return self.plex._change_series_episode_title(token, base_url, episode_data)
