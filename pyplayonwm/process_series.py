import os
import shlex
import subprocess
import sys

class RunHandbrakeCli():

    def __init__(self, fpath="", ename="", output_path=""):
        self.fpath = fpath
        self.ename = ename
        self.output_path = output_path

    def _get_length_in_seconds(self, fpath):
        pass

    def _generate_hb_command(self):
        self.ename = self.ename.replace("'","\'")
        input_path = os.path.join(self.fpath, self.ename)
        output_path = os.path.join(self.output_path, self.ename)
        command = shlex.split(f"HandBrakeCLI -i \
                   \"{input_path}\" \
                   -o \"{output_path}\" \
                   --turbo --two-pass --start-at frames:200 --quality 22.0") #--stop-at frames:1000
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
