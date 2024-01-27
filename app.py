import argparse
import logging
import os
import platform
import sys


from pprint import pprint as pp  # noqa: F401
from pyplayonwm.logger_default import LoggerDefault
from time import sleep

from pyplayonwm import (
    helpers,
    playon_downloader,
    plex_tools,
    process_series,
    strip_playon_watermarks as spm
)

from pyplayonwm.string_tools import StringColor

logger = logging.getLogger(__name__)
logger = LoggerDefault(log_file="pyplayonwm.log").set_logger(logger)

PLATFORM = platform.platform().split("-")[0]


def run_cmd(file_path, episode_name, output_dir):
    if "macOS" not in PLATFORM:
        i = process_series.RunHandbrakeCli(file_path, episode_name, output_dir)
        output = i.run()
        return output


class ApiDownloader:
    def __init__(self, downloader, playon_token):
        self.downloader = downloader
        self.playon_token = ""
        self.h = helpers.HelperTools()
        self.headers = {"Authorization": f"Bearer {playon_token}"}

    def download_files_from_api(self):
        """this function will get a list of recorded files
        from the playon api and compare it to files that have
        already been processed in the local file data/processed_files.txt.
        If there are files from the api that are not in the processed_files.txt
        it will add those file name to a new file
        pyplayonwm/data/unprocessed_files.txt
        and then use those names to determine the download url and download
        each file to pyplayonwm/unprocessed/
        """

        self.playon_token = self.downloader.playon_token()

        logger.info(
            string_color.cyan_string(
                "Retreiving list of recorded files from PlayOn API"
            )
        )
        video_entries = self.downloader.recorded_list(self.playon_token)

        processed_files = h.processed_files()

        files_names_from_api = []
        try:
            for i in video_entries["data"]["entries"]:
                full_recording_name = h.recording_name(i)
                files_names_from_api.append(full_recording_name)
        except KeyError:
            logger.info(
                string_color.red_string("Failed to retreive list of \
                                        recorded files from PlayOn API"))
            logger.info(string_color.red_string("Waiting 5 minutes \
                                                before trying again."))
            sleep(300)
            self.playon_token = self.downloader.playon_token()
            self.download_files_from_api()

        logger.info(
            string_color.yellow_string("Determining which files need processing"))
        files_to_process = self.h.files_to_process(
            processed_files, files_names_from_api)
        if files_to_process:
            logger.info(
                string_color.green_string("Writing files to process to pyplayonwm/data/unprocessed_files.txt"))
            self.h.write_files_to_process(files_to_process)
        else:
            logger.info(string_color.yellow_string("No files to process."))

        all_download_data = []
        for file in files_to_process:
            temp_data = {"url": "", "file_name": ""}
            file_name_with_extension = f"{file}.mp4"
            id = self.h.get_id(file, video_entries["data"]["entries"])
            url = self.h.library_url(id)
            logger.info(
                string_color.cyan_string(
                    f'Attempting retreival of download url data for "{file_name_with_extension}"'
                )
            )
            download_data = self.downloader.download_data(
                url, self.headers, logger)
            if download_data["success"]:
                url = download_data["data"]["url"]
                cloudfront_data = download_data["data"]["data"]
                logger.info(
                    string_color.green_string(
                        f'Generating download url for "{file_name_with_extension}" with Playon Api data'
                    )
                )
                cloudfront_url = self.h.download_url(
                    url,
                    cloudfront_data["CloudFront-Expires"],
                    cloudfront_data["CloudFront-Signature"],
                    cloudfront_data["CloudFront-Key-Pair-Id"],
                )
                download_file_path = os.path.join(
                    self.h.git_root(), "unprocessed", file_name_with_extension
                )
                temp_data["file_name"] = download_file_path
                temp_data["url"] = cloudfront_url
                all_download_data.append(temp_data)

        for data in all_download_data:
            fp = data["file_name"]
            url = data["url"]
            logger.info(
                string_color.cyan_string(
                    f'Attempting Download of "{os.path.split(fp)[-1]}" to "{os.path.split(fp)[0]}"'
                )
            )
            status_code, downloaded = self.downloader.download_content(
                url, fp, logger)
            if status_code == 200:
                if downloaded is True:
                    logger.info(
                        string_color.green_string(
                            f'Download for "{fp}" complete.')
                    )
            elif status_code != 200 or downloaded is False:
                logger.info(string_color.red_string(
                    f'Download for "{fp}" failed.'))

    def process_downloaded_files(
        self, video_to_process="", start_time_offset=None
    ):
        if start_time_offset:
            trimmer = spm.StripPlayonWatermarks(
                video_to_process, start_remove_time=start_time_offset
            )
            try:
                trimmer.trim_video()
                self.h.remove_file_from_unprocessed_tracker(video_to_process)
                self.h.delete_after_processing(video_to_process)
            except KeyboardInterrupt:
                sys.exit(1)
            except:
                logger.info(
                    string_color.red_string(
                        f"Failed to trim {video_to_process}")
                )

        else:
            trimmer = spm.StripPlayonWatermarks(video_to_process)
            try:
                trimmer.trim_video()
                self.h.remove_file_from_unprocessed_tracker(video_to_process)
                self.h.delete_after_processing(video_to_process)
            except KeyboardInterrupt:
                sys.exit(1)
            except:
                logger.info(
                    string_color.red_string(
                        f"Failed to trim {video_to_process}")
                )


def debug():
    pass

    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "-i",
        "--input_path",
        help="file path for the video we want the water mark stripped from",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help='the name of the file you want to use. If none is defined. \
                        The file will be stripped of white space and placed a "processed" directory',
        required=False,
    )
    parser.add_argument(
        "-so",
        "--start_offset",
        help="start time offset. number of seconds to strip at the beginning.",
        type=int,
        required=False,
    )
    parser.add_argument(
        "-r", "--rename", help="rename episodes", type=bool, required=False
    )
    parser.add_argument(
        "-fp", "--files_to_process", help="a list of files to process.", required=False
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="turn on debug logging",
        required=False,
        action="store_true"
    )

    args = parser.parse_args()

    video_input_path = args.input_path
    video_output_path = args.output_path
    start_time_offset = args.start_offset
    files_to_process = args.files_to_process

    if args.debug:
        debug()

    string_color = StringColor()

    h = helpers.HelperTools()
    git_root = h.git_root()

    downloader = playon_downloader.PlayOnDownloader()
    playon_token = downloader.playon_token()
    api_downloader = ApiDownloader(downloader, playon_token)

    if not video_input_path and not files_to_process:
        while True:
            api_downloader.download_files_from_api()
            unprocessed_files_path = os.path.join(git_root, "unprocessed")
            for file in sorted(os.listdir(unprocessed_files_path)):
                video_to_process = os.path.join(unprocessed_files_path, file)
                api_downloader.process_downloaded_files(
                    video_to_process=video_to_process,
                    start_time_offset=start_time_offset,
                )

            logger.info(
                string_color.yellow_string(
                    "Waiting for 30 minutes before checking for available downloads."
                )
            )
            sleep(1800)

    if video_input_path and files_to_process:
        logger.info(
            string_color.red_string(
                "You can only specify one of the following: video_input_path or files_to_process."
            )
        )
        sys.exit(1)

    if files_to_process:
        with open("files_to_process.txt") as f:
            file_paths = [line.strip() for line in f.readlines()]
            for file_path in file_paths:
                video_input_path = os.path.join(git_root, "unprocessed", file_path)
                api_downloader.process_downloaded_files(
                    video_to_process=video_input_path,
                    start_time_offset=start_time_offset,
                )

    elif video_input_path:
        file_path_to_process = os.path.join(git_root, "unprocessed", video_input_path)
        api_downloader.process_downloaded_files(
            video_to_process=file_path_to_process, start_time_offset=start_time_offset
        )
