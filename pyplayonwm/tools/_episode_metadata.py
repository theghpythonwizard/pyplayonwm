from moviepy.video.io.VideoFileClip import VideoFileClip

__all___ = ['EpisodeMetadata']

class VideoMetadata:

    def __init__(self, fpath):
        self.vf = VideoFileClip(fpath)

    def _metadata(self):
        video_info = {
            'duration': self.vf.duration,
            'width': self.vf.size[0],
            'height': self.vf.size[1],
            'fps': self.vf.fps
        }
        self.vf.close()
        return video_info