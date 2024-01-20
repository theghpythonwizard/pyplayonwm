import os
from pathlib import Path
import subprocess

__all__ = ['Helpers']

class Helpers():

    def __init__(self):
        self.git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip()
        
    def _get_git_root(self):
        return self.git_root
    
    def _get_processed_files_path(self):
        processed_files_path = os.path.join(self.git_root, "data", "processed_files.txt")
        return processed_files_path

    def _get_processed_files(self):
        processed_files = [i.rstrip() for i in open(self._get_processed_files_path(), "r").readlines()]
        return processed_files
    
    def _define_filenames_that_need_processing(self, processed_files, recorded_files_from_api):
        files_names_to_process = []
        for rf in recorded_files_from_api:
            if rf not in processed_files:
                files_names_to_process.append(rf)
        return files_names_to_process
    
    def _write_files_to_process(self, files_to_process):
        unprocessed_path = os.path.join(self.git_root, "data", "unprocessed_files.txt")
        with open(unprocessed_path, "w") as f:
            for i in files_to_process:
                f.write(i + "\n")

    def _move_filename_from_unprocessed_tracker_to_processed_tracker(self, filename):
        if filename.endswith(".mp4"):
            filename = filename[:-4]
        unprocessed_path = os.path.join(self.git_root, "data", "unprocessed_files.txt")
        processed_path = os.path.join(self.git_root, "data", "processed_files.txt")
        unprocessed_files = []
        processed_files = []
        with open(unprocessed_path, "r") as f:
            lines = f.readlines()
            unprocessed_files = [i.rstrip() for i in lines if i != "\n"]
        with open(processed_path, "r") as f:
            lines = f.readlines()
            processed_files = [i.rstrip() for i in lines if i != "\n"]

        for uf in unprocessed_files:
            if uf == filename:
                unprocessed_files.remove(uf)
                processed_files.append(uf)
                break
        
        with open(unprocessed_path, "w") as f:
            for line in unprocessed_files:
                f.write(line + "\n")
        with open(processed_path, "w") as f:
            for line in processed_files:
                f.write(line + "\n")

    def _delete_unprocessed_recording_after_processing(self, filename):
        unprocessed_path = os.path.join(self.git_root, "unprocessed", filename)
        os.remove(unprocessed_path)
        
