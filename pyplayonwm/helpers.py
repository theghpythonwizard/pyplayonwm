from .tools._helpers import Helpers
from .tools._playon_recorder import PlayOnLogin, PlayOnRecorder


class HelperTools():

    def __init__(self):
        self.h = Helpers()
        self.p = PlayOnLogin()
        self.pr = PlayOnRecorder()

    def git_root(self):
        return self.h._get_git_root()

    def processed_files_path(self):
        return self.h._get_processed_files_path()

    def processed_files(self):
        return self.h._get_processed_files()

    def recording_ids(self, recording_name):
        return self.pr._get_id_from_name(recording_name)

    def recording_name(self, recording_name):
        return self.pr._generate_full_recording_name(recording_name)

    def files_to_process(self, processed_files, recorded_files_from_api):
        return self.h._define_filenames_that_need_processing(processed_files, recorded_files_from_api)

    def write_files_to_process(self, files_to_process):
        self.h._write_files_to_process(files_to_process)

    def get_id(self, name, entries):
        return self.pr._get_id_from_name(name, entries)

    def library_url(self, id):
        return self.pr._generate_library_url(id)

    def download_url(self, url, expires, signature, key_pair_id):
        return self.pr._gen_cloudfront_download_url(url, expires, signature, key_pair_id)

    def remove_file_from_unprocessed_tracker(self, filename):
        return self.h._move_filename_from_unprocessed_tracker_to_processed_tracker(filename)

    def delete_after_processing(self, filename):
        self.h._delete_unprocessed_recording_after_processing(filename)
