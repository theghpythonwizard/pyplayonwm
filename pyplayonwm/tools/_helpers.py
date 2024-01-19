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
        
