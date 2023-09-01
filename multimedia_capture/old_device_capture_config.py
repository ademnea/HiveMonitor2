import config
import time
from picamera import PiCamera
import config
from subprocess import call
from datetime import datetime
import sounddevice as sd
import soundfile as sf

timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")


# paths
video_dir = config.base_dir+"/multimedia/videos/"
audio_dir = config.base_dir+"/multimedia/audios/"
image_dir = config.base_dir+"/multimedia/images/"
database_path = config.base_dir+"/multimedia/database.sqlite"


class Capture:
    def __init__(self):
        self.files = []
        self.camera = None

    def change_format(self, file_path):
        new_file_path = file_path
        if file_path.endswith(".h264"):
            new_file_path = file_path[:-5]+".mp4"
            call("MP4Box -fps 30 -add "+file_path+" "+new_file_path, shell=True)
            call("rm "+file_path, shell=True)

        return new_file_path

    def record_video(self, capture_duration=10):
        self.init_camera()
        vid_path = video_dir + str(config.node_id)+  '_' + timeString  +  '.h264'
        self.camera.start_recording(vid_path)
        self.camera.wait_recording(capture_duration)
        self.camera.stop_recording()
        self.files.append([self.change_format(vid_path), "video"])
        vid_path = video_dir + str(config.node_id)+  '_' + timeString  +  '.mp4'
        return vid_path

    def record_audio(self, record_seconds=10):
        sample_rate = 44100  # Sample rate (Hz)
        channels = 2  # Number of audio channels

        duration = record_seconds  # Duration of the recording (seconds)
        frames = int(duration * sample_rate)  # Number of frames

        # Start the recording
        recording = sd.rec(frames, samplerate=sample_rate, channels=channels)

        # Wait for the recording to complete
        sd.wait()

        # Generate a unique filename based on the current timestamp
        aud_path = audio_dir + str(config.node_id)+  '_' + timeString  +  '.wav'

        # Save the recorded audio to a WAV file
        sf.write(aud_path, recording, sample_rate)
        
        self.files.append([self.change_format(aud_path), "audio"])

        return aud_path
     
    def init_camera(self):
        if self.camera is None:
            self.camera = PiCamera()
            self.camera.resolution = (640, 480)

    def snap(self, num=1):
        self.init_camera()
        time.sleep(2)
        for i in range(num):
            img_path = image_dir + str(config.node_id)+  '_' + timeString  +  '.jpg'
            self.camera.capture(img_path)
            self.files.append([self.change_format(img_path), "image"])
        return img_path
