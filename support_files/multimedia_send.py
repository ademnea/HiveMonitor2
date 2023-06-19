import paramiko
from os import path
import sqlite3
import  config
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('137.63.185.94',username='hivemonitor', password= '')
print("Connected successfully")
sftp = ssh.open_sftp()
multimedia_urls = {'audio': config.audio_url,
                   'image': config.image_url, 'video': config.video_url}

# paths
database_path = config.base_dir+"/multimedia/database.sqlite"


def send_files():
    if path.isfile(database_path):
        conn = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        # Execute the DELETE statement
        #cursor.execute("DELETE FROM file")

            
        cursor.execute("select * from file where transferred=? limit ?",
                       (0, config.TRANS_LIMIT))
        rows = cursor.fetchall()

        if len(rows) == 0:
            print('...No files to send...')
            conn.close()
            return

        print('attempting sending files')

        for row in rows:
            
            row_dict = dict(row)
            mult_url = multimedia_urls[row_dict['file_type']]
           
            if mult_url == "":
                print("url for "+row_dict['file_type'] +
                      " is blank hence file not transferred.")
                continue
            
            # file = open(row_dict['file_path'], 'rb')
            # payload = {'title': row_dict['file_name'], "node_id": config.node_id,
            #            "longitude": config.logitude, "latitude": config.latitude}
            # files = [(row_dict['file_type'], (row_dict['file_type'],
            #           file, 'application/octet-stream'))]
            # response = requests.request(
            #     "POST", config.server_address+mult_url, headers=None, data=payload, files=files)
            # file.close()
            
            ret= sftp.put(row_dict['file_path'],mult_url+row_dict['file_name'])            
            # if "true" in response.text:
            if (ret):
                conn.execute(
                    "update file set transferred = 1 where id = "+str(row_dict['id']))
                conn.commit()
                print(row_dict['file_name']+" transferred successfully.")
            else:
                print(row_dict['file_name']+" transfer failed!")
        print('closing.....')
        sftp.close()
        conn.close()
        ssh.close()
        exit()
    else:
        print('No files to send')


if __name__ == "__main__":
    send_files()
