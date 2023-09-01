import os
from datetime import datetime
import socket
import config

from ssh2.session import Session
from ssh2.sftp import LIBSSH2_FXF_CREAT, LIBSSH2_FXF_WRITE, \
    LIBSSH2_SFTP_S_IRUSR, LIBSSH2_SFTP_S_IRGRP, LIBSSH2_SFTP_S_IWUSR, \
    LIBSSH2_SFTP_S_IROTH

# paths
video_dir = config.base_dir + "multimedia/videos/"
audio_dir = config.base_dir + "multimedia/audios/"
image_dir = config.base_dir + "/multimedia/images/"

# Server details
ssh_hostname = '137.63.185.94'
ssh_username = 'hivemonitor'
ssh_password = ''

host = '137.63.185.94'
port = 22
user = 'hivemonitor'
password = ''
destination = '/var/www/html/ademnea_website/public/arriving_hive_media/'

def send_file(source):
    buf_size = 1024 * 1024
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        s = Session()
        s.handshake(sock)
        s.userauth_password(user, password)
        sftp = s.sftp_init()
        mode = LIBSSH2_SFTP_S_IRUSR | \
            LIBSSH2_SFTP_S_IWUSR | \
            LIBSSH2_SFTP_S_IRGRP | \
            LIBSSH2_SFTP_S_IROTH
        f_flags = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE
        fileinfo = os.stat(source)
        print("Starting copy of local file %s to remote %s:%s" % (
            source, host, destination))
        now = datetime.now()
        with open(source, 'rb') as local_fh, \
                sftp.open(destination + os.path.basename(source), f_flags, mode) as remote_fh:
            data = local_fh.read(buf_size)
            while data:
                remote_fh.write(data)
                data = local_fh.read(buf_size)
        taken = datetime.now() - now
        rate = (fileinfo.st_size / 1024000.0) / taken.total_seconds()
        print(f"Finished writing remote file in {taken}, transfer rate {rate} MB/s")

        # Delete the local file if the transfer was successful
        #os.remove(source)
        #print(f'Deleted local file: {source}')
    except Exception as e:
        print("An error occurred: %s" % e)

# Send images
image_files = os.listdir(image_dir)
if len(image_files) > 0:
    print("Sending image files...")
    for file in image_files:
        file_path = os.path.join(image_dir, file)
        send_file(file_path)

# Send audio
audio_files = os.listdir(audio_dir)
if len(audio_files) > 0:
    print("Sending audio files...")
    for file in audio_files:
        file_path = os.path.join(audio_dir, file)
        send_file(file_path)

# Send videos
video_files = os.listdir(video_dir)
if len(video_files) > 0:
    print("Sending video files...")
    for file in video_files:
        file_path = os.path.join(video_dir, file)
        send_file(file_path)
