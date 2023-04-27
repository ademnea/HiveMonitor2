from os import path, mkdir
from hashlib import md5
import config
import old_device_capture_config as device_capture_config
import datetime 
from datetime import datetime

# paths
video_dir = config.base_dir+"/multimedia/videos/"
audio_dir = config.base_dir+"/multimedia/audios/"
image_dir = config.base_dir+"/multimedia/images/"


def recursive_mkdir(given_path):
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


class Capture(device_capture_config.Capture):
    def __init__(self):
        super().__init__()
        self.files = []

        # check if directories exist and if not create them
        if not path.isdir(video_dir):
            recursive_mkdir(video_dir)
        if not path.isdir(audio_dir):
            recursive_mkdir(audio_dir)
        if not path.isdir(image_dir):
            recursive_mkdir(image_dir)
     

        # check if directories exist and if not create them
        if not path.isdir(video_dir):
            recursive_mkdir(video_dir)
        if not path.isdir(audio_dir):
            recursive_mkdir(audio_dir)
        if not path.isdir(image_dir):
            recursive_mkdir(image_dir)


if __name__ == "__main__":
    
    print()
    print()
    print()

    capture = Capture()

    timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print()


    print("DATE : " + timeString)
    print()

    print("TAKING PHOTOS")
    print()
    image_path = capture.snap(1)
    print()
    print("New image taken at: " + image_path)
    print()
    print()

    print("CAPTURING VIDEO")
    print()
    video_path = capture.record_video()
    print()
    print("New video taken at: " + video_path)
    print()
    print()

    print("CAPTURING AUDIO")
    print()
    audio_path = capture.record_audio()
    print()
    print("New audio taken at: " + audio_path)
    print()
    print()
    print()
