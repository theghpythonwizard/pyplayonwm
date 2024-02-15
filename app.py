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

git_root = helpers.HelperTools().git_root()
log_file_path = os.path.join(git_root, "logging", "pyplayonwm.log")
logger = logging.getLogger(__name__)
logger = LoggerDefault(log_file=log_file_path).set_logger(logger)

PLATFORM = platform.platform().split("-")[0]


def run_cmd(file_path, episode_name, output_dir):
    if "macOS" not in PLATFORM:
        i = process_series.RunHandbrakeCli(file_path, episode_name, output_dir)
        output = i.run()
        return output


class MetaDataUpdater:

    def __init__(self, series="", season="", movie=""):
        self.plex = plex_tools.PlexTools()
        self.plex_token = self.plex.get_plex_token()
        self.base_url = self.plex.base_url
        self.series = series
        self.season = season
        self.movie = movie

    def libraries(self):
        libraries = self.plex.get_library(self.plex_token, self.base_url)
        return libraries

    def movie_library(self):
        libararies = self.libraries()
        movie_libary = self.plex.get_movie_library(self.plex_token, self.base_url, libararies)
        return movie_libary

    def series_library(self):
        libararies = self.libraries()
        series_library = self.plex.get_series_library(self.plex_token, self.base_url, libararies)
        return series_library

    def season_library(self):
        series_library = self.series_library()
        season_library = self.plex.get_seasons_library_from_series(
            self.plex_token, self.base_url, self.series, series_library
        )
        return season_library

    def single_season_library(self, season_library=None):
        if season_library is None:
            season_library = self.season_library()
        single_season_library = self.plex.get_episodes_from_season(self.plex_token, self.base_url, self.season, season_library)
        return single_season_library

    def update_single_season_metadata(self, library):
        single_season_library = library
        metadata_correct = self.plex.is_metadata_correct(single_season_library)
        logger.info(f"Is Metadata Correct: {metadata_correct}")
        if not metadata_correct:
            fields_for_update = self.plex.filter_episodes_for_update(self.plex_token, self.base_url, single_season_library)
        if not args.dry_run:
            logger.info("Updating Metadata on Plex Server.")
            try:
                for i in fields_for_update:
                    pass
                    update_metadata = self.plex.change_series_episode_title(self.plex_token,
                                                                            self.base_url,
                                                                            i['episode_id'],
                                                                            i['title'],
                                                                            i['sort_title'],
                                                                            i['originally_available'],
                                                                            i['episode_summary'])
                    if update_metadata:
                        logger.info(string_color.green_string("Metadata Updated."))
            except UnboundLocalError as e:
                if "fields_for_update" in str(e):
                    print("No metadata to update.")
                    exit(0)
                else:
                    print(e)
                    exit(1)

    # I don't really need this right now, but I'm keeping it for reference in case I need it later.
    # pp(fields_for_update)
    # season_needs_metadata_update = plex.filter_episodes_for_update(plex_token, base_url, single_season_library)
    # print(response)
    # response = plex.refresh_episode_metadata(plex_token, base_url, ep1)
    # print(response)
    # print(movie_libary.text)
    # import xmltodict
    # import xml.dom.minidom
    # xml_output = xml.dom.minidom.parseString(xmltodict.unparse(library)) \
    #     .toprettyxml(encoding='UTF-8').decode('utf-8')
    # print(xml_output)
    # exit(0)


class CloudRecordingRemoval:

    def __init__(self):
        self.cloud_recording_removal = playon_downloader.PlayOnDownloader()

    def delete_recordings(self):
        recordings_to_delete_path = os.path.join(git_root, "data", "recordings_to_delete_from_cloud.txt")
        with open(recordings_to_delete_path, "r") as f:
            logger.info("Gathering list of recordings to delete from cloud storage.")
            recordings_to_delete = [i.rstrip() for i in f.readlines()]
        if recordings_to_delete:
            self.cloud_recording_removal.delete_cloud_recording(logger, video_list_to_delete=recordings_to_delete)
            exit(0)
        else:
            logger.info(string_color.yellow_string("No recordings to delete."))
            exit(0)

    def delete_single_recording(self, video_name):
        self.cloud_recording_removal.delete_cloud_recording(logger, video_name_to_delete=video_name)
        exit(0)


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
        # logger.info(f"{self.playon_token} before generation")
        self.playon_token = self.downloader.playon_token()
        # logger.info(f"{self.playon_token} after generation")

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
            else:
                logger.info(
                    string_color.red_string(
                        f'Failed to retreive download url data for "{file_name_with_extension}"'
                    )
                )
                logger.info(download_data)
                exit(1)

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
    logger.info("Debugging")
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
        '-cm',
        '--check_metadata',
        help='check metadata on plex server for series and episodes and update with local info if incorrect.',
        required=False,
        action="store_true"
    )
    parser.add_argument(
        '-s',
        '--series',
        help='Series Name e.g. "The Office (US)", must match what is on the plex server',
        required=False
    )
    parser.add_argument(
        '-se',
        '--season',
        help='Season Number e.g. "Season 6", must match what is on the plex server',
        required=False
    )
    parser.add_argument(
        '-m',
        '--movie',
        help='Movie Name e.g. "The Matrix", must match what is on the plex server',
        required=False
    )
    parser.add_argument(
        "-crr",
        "--cloud_recording_removal",
        help="delete cloud recordings",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-vf",
        "--video_file",
        help="Name video file to delete from cloud storage",
        required=False
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="turn on debug logging",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-dr",
        "--dry_run",
        help="dry run. no changes will be made to the plex server",
        required=False,
        action="store_true"
    )

    args = parser.parse_args()

    video_input_path = args.input_path
    video_output_path = args.output_path
    start_time_offset = args.start_offset
    files_to_process = args.files_to_process
    check_metadata = args.check_metadata

    if args.debug:
        debug()

    if check_metadata:
        if args.movie:
            logger.info(
                StringColor().red_string(
                    "This code is not implemented yet. Please try again later."
                )
            )
            sys.exit(1)
        if not args.series or not args.season:
            if not args.series:
                print("You must specify a series to check metadata.")
            if not args.season:
                print("You must specify a season to check metadata.")
            parser.print_help()
            sys.exit(1)

        if args.series and args.season:
            # metatdata updater
            mu = MetaDataUpdater(series=args.series, season=args.season)
            # single_season_library = mu.single_season_library()
            season_library = mu.season_library()
            single_season_library = mu.single_season_library(season_library)
            mu.update_single_season_metadata(single_season_library)

        sys.exit(0)

    if args.cloud_recording_removal:
        crr = CloudRecordingRemoval()
        if args.video_file:
            crr.delete_single_recording(args.video_file)
        else:
            crr.delete_recordings()

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
