import os
import sys

from pyplayonwm import process_series

def run_cmd(file_path, episode_name, output_dir):
    i = process_series.RunHandbrakeCli(
            file_path,
            episode_name,
            output_dir
        )
    rc = i.run()
    return rc

if __name__ == '__main__':
    fp = '/home/jasschul/share/tvshows/tvshow_files/The_Office/Season_3'
    output_path = '/home/jasschul/tvoutput'
    # rc = run_cmd(fp, "E01_Gay_Witch_Hunt_S03E01.mp4", output_path)
    # print(rc)
    for episode in os.listdir(fp):
        try:
            rc = run_cmd(fp, episode, output_path)
            print(rc)
        except KeyboardInterrupt:
            sys.exit(1)