import os
import sys

from pyplayonwm import process_series

def run_cmd(file_path, episode_name, output_dir):
    i = process_series.RunHandbrakeCli(
            file_path,
            episode_name,
            output_dir
        )
    output = i.run()
    return output

if __name__ == '__main__':
    fp = '/home/jasschul/share/tvshows/tvshow_files/The_Office/Season_3'
    output_path = '/home/jasschul/tvoutput'
    # output = run_cmd(fp, "E02_The_Convention_S03E02.mp4", output_path)
    # print(output)
    for episode in os.listdir(fp):
        try:
            output = run_cmd(fp, episode, output_path)
            print(output)
        except KeyboardInterrupt:
            sys.exit(1)