import os
import config
import device_capture_config as device_capture
import config
from datetime import datetime

# define the paths for storing multimedia files
video_dir = os.path.join(config.base_dir, "multimedia/videos/")
audio_dir = os.path.join(config.base_dir, "multimedia/audios/")
image_dir = os.path.join(config.base_dir, "multimedia/images/")

class Capture(device_capture.Capture):
    def __init__(self):
        super().__init__()
        self.files = []

        # check if directories exist and if not create them
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)

if __name__ == "__main__":
    #print empty lines for formatting
    print("\n" * 3)
    
    #create an instance of the capture class
    capture = Capture()
    
    #get the current time and date as a string
    timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print("\nDATE : " + timeString + "\n")

    #take photos
    print("TAKING PHOTOS\n")
    image_path = capture.snap(1)
    print("\nNew image taken at: " + image_path + "\n\n")

    #capture video
    print("CAPTURING VIDEO\n")
    video_path = capture.record_video()
    print("\nNew video taken at: " + video_path + "\n\n")

    #capture audio
    print("CAPTURING AUDIO\n")
    audio_path = capture.record_audio()
    print("\nNew audio taken at: " + audio_path + "\n\n")

