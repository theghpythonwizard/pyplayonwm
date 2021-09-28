import subprocess
import shlex
import os

__all__ = ['HandBrakeInstaller']

class HandBrakeInstaller:

    def __init__(self):
        apt_repository_cmd = 'sudo add-apt-repository ppa:stebbins/handbrake-git-snapshots -y'
        apt_update_cmd = 'sudo apt-get update -y'
        handbrake_install_cmd = 'sudo apt install handbrake-cli handbrake-gtk -y'
        carriage_return = shlex.split('echo -e -n "\n"')
        self.apt_repository_cmd = shlex.split(apt_repository_cmd)
        self.apt_update_cmd = shlex.split(apt_update_cmd)
        self.handbrake_install_cmd = shlex.split(handbrake_install_cmd)
        self.carriage_return = carriage_return

    def handbrake_installed(self):
        hb_path = '/usr/bin/HandBrakeCLI'
        if os.path.exists(hb_path):
            return True
        return False

    def install_handbrake(self):
        subprocess.Popen(self.apt_update_cmd).wait()
        subprocess.Popen(self.apt_repository_cmd).wait()
        subprocess.Popen(self.handbrake_install_cmd).wait()



