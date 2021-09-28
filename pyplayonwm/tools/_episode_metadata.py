from moviepy.editor import VideoFileClip

__all___ = ['EpisodeMetadata']

class EpisodeMetadata:

    def __init__(self, fpath):
        self.cap = VideoFileClip(fpath)

    def _episode_duration(self):
        duration = self.cap.duration
        if duration:
            return duration
        else:
            return 0

    def _episode_frames(self):
        # frame = self.cap.get_frame()
        # if frame:
        #     return frame
        # else:
        #     return 0
        pass