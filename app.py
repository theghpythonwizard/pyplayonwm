from pyplayonwm import _install_handbrake, process_series
import os
import sys


def hb_installer():
    runner = _install_handbrake.HandBrakeInstaller()
    if runner.handbrake_installed():
        pass
    else:
        runner.install_handbrake()

def run_cmd(file_path, episode_name, output_dir):
    i = process_series.RunHandbrakeCli(
            file_path,
            episode_name,
            output_dir
        )
    rc = i.run()
    return rc
    

if __name__ == '__main__':
    hb_installer()
    fp = '/home/jasschul/share/tvshows/tvshow_files/The_Office/Season_3'
    output_path = '/home/jasschul/tvoutput'
    # rc = run_cmd(fp, "E15_Phyllis's_Wedding_S03E15.mp4", output_path)
    # print(rc)
    for episode in os.listdir(fp):
        try:
            rc = run_cmd(fp, episode, output_path)
            print(rc)
        except KeyboardInterrupt:
            sys.exit(1)