import os
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

class ConverterLogic:
    def __init__(self, progress_callback=None, success_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.success_callback = success_callback
        self.error_callback = error_callback

    def convert(self, file_path, target_format):
        try:
            ext = f".{target_format.lower()}"
            output_path = os.path.splitext(file_path)[0] + "_converted" + ext
            
            if target_format == "MP3":
                clip = VideoFileClip(file_path)
                clip.audio.write_audiofile(output_path)
                clip.close()
            elif target_format == 'GIF':
                clip = VideoFileClip(file_path)
                clip.write_gif(output_path)
                clip.close()
            else:
                clip = VideoFileClip(file_path)
                if target_format.upper() == "MP4":
                    codec = 'libx264'
                elif target_format.upper() == "AVI":
                    codec = 'mpeg4'
                else:
                    codec = 'libx264'
                clip.write_videofile(output_path, codec=codec)
                clip.close()
            
            if self.success_callback:
                self.success_callback(output_path)
        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))
