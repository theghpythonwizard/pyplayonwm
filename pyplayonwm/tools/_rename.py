import os
import re

class Rename:
    def __init__(self, path):
        self.path_to_file = path
        self.dirname = os.path.dirname(path)


    def _get_file_name(self):
        return os.path.basename(self.path_to_file)

    @staticmethod
    def _get_season(filename):
        print(filename)
        raw = filename.split('-')[1].split()[0].strip()
        s = re.findall(r'S\d{2}', raw, re.IGNORECASE)
        if isinstance(s, list):
            return s[0].upper()
        else:
            return s.upper()

    @staticmethod
    def _get_episode(filename):
        raw = filename.split('-')[1].split()[0].strip()
        e = re.findall(r'E\d{2}', raw, re.IGNORECASE)
        if isinstance(e, list):
            return e[0].upper()
        else:
            return e.upper()

    @staticmethod
    def _get_extension(filename):
        return filename.split('.')[-1].split(".")[-1]

    @staticmethod
    def _get_title(filename):
        title = "_".join([i.split('.')[0] for i in filename.split('-')[1].split()[1:]])
        return title.upper()

    @staticmethod
    def _construct_new_name(season, episode, title, extension):
        new_name = f'{episode}_{title}_{season}{episode}.{extension}'
        return new_name

    def rename(self):
        filename = self._get_file_name()
        episode = self._get_episode(filename)
        season = self._get_season(filename)
        extension = self._get_extension(filename)
        title = self._get_title(filename)
        new_name = self._construct_new_name(season, episode, title, extension)
        new_path = os.path.join(self.dirname, new_name)
        os.rename(self.path_to_file, new_path)