import config
import time
import sounddevice as sd
import soundfile as sf
from subprocess import call
from datetime import datetime
import subprocess
import os
import shutil
from moviepy.editor import VideoFileClip

# define paths for multimedia files using os.path.join for better cross-platform compatibility
video_dir = os.path.join(config.base_dir,"multimedia","videos")
audio_dir = os.path.join(config.base_dir,"multimedia","audios")
image_dir = os.path.join(config.base_dir, "multimedia","images")

timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
#print(timeString)



class Capture:
    def __init__(self):
        self.files = []
        self.camera = None

    def generate_file_path(self, directory, extension):
        """
        Generate a file path based on the given directory and extension.

        Args:
            directory (str): The directory where the file will be stored.
            extension (str): The file extension.

        Returns:
            str: The generated file path.
        """
        return f"{directory}{config.node_id}_{timeString}.{extension}"

    def change_format(self, file_path):
        """
        Change the format of the given file path.

        Args:
            file_path (str): The path of the file to be converted.

        Returns:
            str: The path of the converted file.
        """
        if file_path.endswith(".h264"):
            new_file_path = file_path.replace(".h264", ".mp4")
            clip = VideoFileClip(file_path)
            clip.write_videofile(new_file_path)
            os.remove(file_path)
            return new_file_path
        return file_path

    def record_video(self, capture_duration=10000):
        """
        Record a video for the specified duration.

        Args:
            capture_duration (int): The duration of the video capture in milliseconds.

        Returns:
            str: The path of the recorded video file.
        """
        vid_path = self.generate_file_path(video_dir, 'h264')
        video_result = subprocess.run(["libcamera-vid", "-t", str(capture_duration), "-o", vid_path, "--width", "1280", "--height", "720", "-n"], capture_output=True, text=True)
        print(video_result.stdout)
        print(video_result.stderr)
        self.files.append([self.change_format(vid_path), "video"])
        return self.generate_file_path(video_dir, 'mp4')

    def record_audio(self, record_seconds=10):
        """
        Record audio for the specified duration.

        Args:
            record_seconds (int): The duration of the audio recording in seconds.

        Returns:
            str: The path of the recorded audio file.
        """
        sample_rate = 44100
        channels = 2
        duration = record_seconds
        frames = int(duration * sample_rate)
        recording = sd.rec(frames, samplerate=sample_rate, channels=channels)
        sd.wait()
        aud_path = self.generate_file_path(audio_dir, 'wav')
        sf.write(aud_path, recording, sample_rate)
        self.files.append([self.change_format(aud_path), "audio"])
        return aud_path

    def snap(self, num=1):
        """
        Capture an image.

        Args:
            num (int): The number of images to capture.

        Returns:
            str: The path of the captured image file.
        """
        time.sleep(2)
        img_path = self.generate_file_path(image_dir, 'jpg')
        image_result = subprocess.run(["libcamera-jpeg", "-o", img_path, "--width", "1920", "--height", "1080", "-n"], capture_output=True, text=True)
        print(image_result.stdout)
        print(image_result.stderr)
        self.files.append([self.change_format(img_path), "image"])
        return img_path


# class Capture:
#     def __init__(self):
#         self.files = []
#         self.camera = None

#     def change_format(self, file_path):
#         new_file_path = file_path
#         if file_path.endswith(".h264"):
#             new_file_path = file_path[:-5]+".mp4"
#             call("MP4Box -fps 30 -add "+file_path+" "+new_file_path, shell=True)
#             call("rm "+file_path, shell=True)

#         return new_file_path

#     def record_video(self, capture_duration=10000):
        
#         #capture video
#         vid_path = video_dir + str(config.node_id)+  '_' + timeString  +  '.h264'
#         video_result = subprocess.run(["libcamera-vid", "-t",str(capture_duration), "-o", vid_path, "--width", "1280", "--height", "720", "-n"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#         # Print the output and errors (if any)
#         print(video_result.stdout.decode("utf-8"))
#         print(video_result.stderr.decode("utf-8"))

#         # convert vid from h264 to mp4
#         self.files.append([self.change_format(vid_path), "video"])

#         vid_path = video_dir + str(config.node_id)+  '_' + timeString  +  '.mp4'
#         return vid_path
       

#     def record_audio(self, record_seconds=10):
#         sample_rate = 44100  # Sample rate (Hz)
#         channels = 2  # Number of audio channels

#         duration = record_seconds  # Duration of the recording (seconds)
#         frames = int(duration * sample_rate)  # Number of frames

#         # Start the recording
#         recording = sd.rec(frames, samplerate=sample_rate, channels=channels)

#         # Wait for the recording to complete
#         sd.wait()

#         # Generate a unique filename based on the current timestamp
#         aud_path = audio_dir + str(config.node_id)+  '_' + timeString  +  '.wav'

#         # Save the recorded audio to a WAV file
#         sf.write(aud_path, recording, sample_rate)

#         self.files.append([self.change_format(aud_path), "audio"])

#         return aud_path

#     def snap(self, num=1):

#         time.sleep(2)

#         for i in range(num):

#             img_path = image_dir + str(config.node_id)+  '_' + timeString  +  '.jpg'

#             # Run the command and capture the output and errors

#             #result = subprocess.run(["libcamera-jpeg", "-o", "/home/pi/Desktop/Intergrated-System/Adafruit_Python_DHT/test2.jpg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             image_result = subprocess.run(["libcamera-jpeg", "-o", img_path, "--width", "1920", "--height", "1080", "-n"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
#             # Print the output and errors (if any)
#             print(image_result.stdout.decode("utf-8"))
#             print(image_result.stderr.decode("utf-8"))

#             # self.camera.capture(img_path)
#             self.files.append([self.change_format(img_path), "image"])

#             return img_path
         
    

