import os
import shlex
import subprocess
import sys

from .tools._episode_metadata import EpisodeMetadata
from .tools._install_handbrake import HandBrakeInstaller


class RunHandbrakeCli():

    def __init__(self, fpath="", ename="", output_path=""):
        self.fpath = fpath
        self.ename = ename
        self.output_path = output_path
        installer = HandBrakeInstaller()
        if installer.handbrake_installed():
            pass
        else:
            installer.install_handbrake()
    

    def _get_length_in_seconds(self):
        cap = EpisodeMetadata(os.path.join(self.fpath,self.ename))
        return cap._episode_duration()

    def _generate_hb_command(self, start_time=0, stop_time=0, quality=0):
        self.ename = self.ename.replace("'","\'")
        input_path = os.path.join(self.fpath, self.ename)
        output_path = os.path.join(self.output_path, self.ename)
        if not start_time:
            start_time = 5
        if not stop_time:
            stop_time = self._get_length_in_seconds() - 8
        if not quality:
            quality = "22.0"
        command = shlex.split(f"HandBrakeCLI -i \
                   \"{input_path}\" \
                   -o \"{output_path}\" \
                   --turbo --two-pass --start-at seconds:{start_time} \
                   --stop-at seconds:{stop_time} --quality {quality}")
        return command

    def run(self, command=""):
        if not command:
            command = self._generate_hb_command()
        print(" ".join(command))
        try:
            process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            outvar, err = process.communicate()
            if len(err) != 0:
                return err.decode("utf-8")
            else:
                return outvar.decode('utf-8').strip()
        except KeyboardInterrupt:
            sys.exit(1)
