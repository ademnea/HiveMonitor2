import time
import config
import datetime
import subprocess
import soundfile as sf
import sounddevice as sd
from os import path, mkdir
from subprocess import call
from datetime import datetime
from picamera import PiCamera

class Capture:
    def __init__(self):
        self.camera = None
        self.picamera_version = config.picamera_version

        # setting  file paths for storing media files
        self.video_dir = config.base_dir+"multimedia/videos/"
        self.audio_dir = config.base_dir+"multimedia/audios/"
        self.image_dir = config.base_dir+"multimedia/images/"

        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        # Ensure multimedia directories exist or create them
        self.recursive_mkdir(self.video_dir)
        self.recursive_mkdir(self.audio_dir)
        self.recursive_mkdir(self.image_dir)

    def recursive_mkdir(self, given_path):
        # Recursive directory creation
        directories = given_path.split("/")
        length = len(directories)
        given_path, start_index = ("/" + directories[1], 2) if given_path[0] == '/' else (directories[0], 1)
        if not path.isdir(given_path):
            mkdir(given_path)

        for index in range(start_index, length):
            if len(directories[index]) > 0:
                given_path = given_path + '/' + directories[index]
                if not path.isdir(given_path):
                    mkdir(given_path)

    def change_format(self, file_path):
        new_file_path = file_path
        if file_path.endswith(".h264"):
            new_file_path = file_path[:-5] + ".mp4"
            call("MP4Box -fps 30 -add " + file_path + " " + new_file_path, shell=True)
            call("rm " + file_path, shell=True)

        return new_file_path
    

    def init_camera(self):
        if self.camera is None:
            self.camera = PiCamera()
            self.camera.resolution = (640, 480)

    def capture_photo(self):
        time.sleep(2)
        img_path = self.image_dir + str(config.node_id) + '_' + config.timeString + '.jpg'
        if(config.picamera_version == 2):
            self.init_camera()
            self.camera.capture(img_path)
        elif(config.picamera_version == 3):
            image_result = subprocess.run(["libcamera-jpeg", "-o", img_path, "--width", "1920", "--height", "1080", "-n"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(image_result.stdout.decode("utf-8")) # Print the output as camera takes photo(if any)
            print(image_result.stderr.decode("utf-8"))   # Print the errors (if any)
        self.change_format(img_path)
        return img_path

    def capture_video(self, capture_duration=10):
        vid_path = self.video_dir + str(config.node_id) + '_' + config.timeString + ".h264"
        if(config.picamera_version == 2):
            self.init_camera()
            self.camera.start_recording(vid_path)
            self.camera.wait_recording(capture_duration)
            self.camera.stop_recording()
        elif(config.picamera_version == 3):
            video_result = subprocess.run(["libcamera-vid", "-t",str(capture_duration * 1000), "-o", vid_path , "--width", "1280", "--height", "720", "-n"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(video_result.stdout.decode("utf-8")) # Print the output as camera takes videos(if any)
            print(video_result.stderr.decode("utf-8"))   # Print the errors (if any)
        print(vid_path)
        self.change_format(vid_path)
        vid_path = self.video_dir + str(config.node_id) + '_' + config.timeString + '.mp4'
        return vid_path

    def capture_audio(self, capture_seconds=10):
        sample_rate = 44100  # Sample rate (Hz)
        channels = 2  # Number of audio channels
        duration = capture_seconds  # Duration of the recording (seconds)
        frames = int(duration * sample_rate)  # Number of frames
        recording = sd.rec(frames, samplerate=sample_rate, channels=channels) # Start the recording
        sd.wait()   # Wait for the recording to complete
        aud_path = self.audio_dir + str(config.node_id) + '_' + config.timeString + '.wav'   # Generate a unique filename based on the current timestamp
        sf.write(aud_path, recording, sample_rate)  # Save the recorded audio to a WAV file
        return aud_path
    
    #for pi zero
    # def record_audio(self, record_seconds=10): 
    #     audio_dir = "/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/audios/"
    #     filename = f"{audio_dir}{config.node_id}_{time.strftime('%Y%m%d_%H%M%S')}.wav"
    #     command = f"arecord -r 44100 -d {record_seconds} -f S16_LE {filename}"
        
    #     try:
    #         subprocess.run(command, shell=True, check=True)
    #         self.files.append([self.change_format(filename), "audio"])
    #         return filename
    #     except subprocess.CalledProcessError as e:
    #         print(f"Failed to record audio: {e}")
    #         return None
    

    def run_capture(self):
        print("\n\n")

        timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        print("DATE:", timeString)
        print()

        try:
            print("TAKING PHOTOS")
            print()
            image_path = self.capture_photo()
            print("New image taken at:", image_path)
            print()
        except Exception as e:
            print("Error capturing photos:", e)
        
        try:
            print("CAPTURING VIDEO")
            print()
            video_path = self.capture_video()
            print("New video taken at:", video_path)
            print()
        except Exception as e:
            print("Error capturing video:", e)
        
        try:
            print("CAPTURING AUDIO")
            print()
            audio_path = self.capture_audio()
            print("New audio taken at:", audio_path)
            print()
        except Exception as e:
            print("Error capturing audio:", e)
        
        print("\n\n")



if __name__ == "__main__":
    capture = Capture()
    capture.run_capture()
