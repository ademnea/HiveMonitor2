import paramiko
import os

# create an SSH client object
ssh = paramiko.SSHClient()

# set policy to auto-add the remote server's host key
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# connect to the remote server using SSH
print()
print()
try:
    ssh.connect(hostname='', username='', password='')
    print('Connected to server successfully')
except Exception as e:
    print(f'Failed to connect to server: {str(e)}. Will try again later')

# create an SFTP client object using the SSH connection
sftp = ssh.open_sftp()

# set the local folder path of the files to upload
local_folder_path = 'E:/mango_images'

# set the remote folder path where the files will be uploaded on the server
remote_folder_path = '/var/www/html/ademnea_website/public/mango_images/'

# use os.listdir to get the list of files in the local folder
files = os.listdir(local_folder_path)

# loop through the files and use sftp.put to upload each file to the remote server
for file in files:
    print()
    print("Sending " + file)
    # set the local path of the file to upload
    local_path = os.path.join(local_folder_path, file)
    # set the remote path where the file will be uploaded on the server
    remote_path = remote_folder_path + file
    # use sftp.put to upload the file to the remote server

    try:
        sftp.put(local_path, remote_path)
        print('Sent successfully')
    except Exception as e:
        print(f'Failed: {str(e)}. Will try again later')


print()
print()

# close the SFTP and SSH client objects
sftp.close()
ssh.close()

# close the SFTP and SSH client objects
sftp.close()
ssh.close()
