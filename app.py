import os
import sys
import argparse

from pyplayonwm import process_series
from pyplayonwm import rename_episode

def run_cmd(file_path, episode_name, output_dir):
    i = process_series.RunHandbrakeCli(
            file_path,
            episode_name,
            output_dir
        )
    output = i.run()
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input_dir', help='file path', required=True)
    parser.add_argument('-o', '--output_dir', help='episode name', required=True)
    parser.add_argument('-r', '--rename', help='rename episodes', type=bool, required=False)

    args = parser.parse_args()

    fp = args.input_dir
    output_path = args.output_dir
    # output = run_cmd(fp, "E02_The_Convention_S03E02.mp4", output_path)
    # print(output)
    # if args.rename:
    #     rename_episode(output_path)
    for episode in os.listdir(fp):
        print(episode)
        try:
            output = run_cmd(fp, episode, output_path)
            print(output)
            if args.rename:
                rename_episode.rename(os.path.join(output_path, episode))
        except KeyboardInterrupt:
            sys.exit(1)

    