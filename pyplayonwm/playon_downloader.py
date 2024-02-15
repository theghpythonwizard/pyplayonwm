from .tools._playon_recorder import PlayOnLogin, PlayOnRecorder


class PlayOnDownloader:

    def __init__(self):
        self.pl = PlayOnLogin()
        self.pd = PlayOnRecorder()

    def playon_token(self):
        return self.pl._login_token()

    def recorded_list(self, token=None):
        if not token:
            token = self.pl._login_token()
        return self.pd._get_recorded_list(token)

    def download_data(self, url, headers, logger):
        return self.pd._get_download_data_from_library_url(url, headers, logger)

    def download_content(self, url, file_name, logger):
        return self.pd._download_content(url, file_name, logger)

    def delete_cloud_recording(self, logger, video_name_to_delete="", video_list_to_delete=[], headers=None):
        return self.pd._delete_processed_recording_from_cloud_storage(logger, video_name_to_delete=video_name_to_delete,
                                                                      video_list_to_delete=video_list_to_delete, headers=headers)
