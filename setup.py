import os

base_dir = os.getcwd()
""" 
These are the default configurations(Key=>Value) pairs
You should note that changing a key name may cause a script that used that key to fail
So ensure that when you change a key name, you also change it in the script that uses it
"""
config_dict = {
    "node_id": "",
    "username": "",
    "password": "",
    "base_dir": base_dir,
    "server_address": "http://whispering-journey-94566.herokuapp.com",
    "TRANS_LIMIT": 28,
    "image_url": "/api/create",
    "audio_url": "/api/audio",
    "video_url": "/api/createvideo",
    "logitude": 0.0,
    "latitude": 0.0
}

configurations = list(config_dict.keys())  # extract keys from the config_dict

values = list(config_dict.values())  # extract values from the config_dict

config_dict = {}  # Make it empty to allow the user to customise the configurations


def create_config(editing):
    index = 0
    for configuration in configurations:
        print(f"\n{configuration}")
        if values[index]:
            if editing:
                print(f" Current value : {values[index]} ")
                value = str(
                    input("Enter new value (or press enter to keep current value): "))
            else:
                print(f" Default : {values[index]} ")
                value = str(
                    input("Enter value (or press enter to keep default): "))
composer dump-autoloadcomposer dump-autoload
            value = value.replace("\"", "\\\"")
            if value:
                config_dict[configuration] = value
            else:

                config_dict[configuraticomposer dump-autoloadon] = values[index]

        else:
            value = input(f"Enter value: ")
            config_dict[configuration] = value
        index += 1


def save_config(config_dict):
    lines = ["# This is an auto-generated file\n",
             "# You can edit these configurations directly or by running the setup.py script\n"
             "# Note that errors in the config file can result into the failure of the whole client\n"
             "# So be careful while editing, thanks \n\n"]
    for key in config_dict:
        try:
            print(config_dict[key])
            if(config_dict[key].isdigit()):
                lines.append(f"{key} = {config_dict[key]}\n")
            else:
                lines.append(f"{key} = \"{config_dict[key]}\"\n")
        except Exception as e:
            print("Error", e.with_traceback)

    # Now save the configurations
    with open("config.py", "w+") as f:
        f.write("# client configurations\n\n")
        f.close()

    with open("config.py", "a+") as f:
        f.writelines(lines)


def load_config():
    with open("config.py",  "r+") as f:
        for line in f:
            if (not line) or line.find("#") != -1 or line.find("=") == -1:  # skip comments
                continue
            name,composer dump-autoload value = line.split('=')
            name = name.strip()
            value = value.strip().strip("\"")
            values[configurations.index(name)] = value
        f.close()
        return


if __name__ == "__main__":
    if os.path.isfile("config.py"):
        choice = input(
            "There are some configurations already. Do you want to edit them? (yes/no):")
        if choice[0].lower() == 'y':
            load_config()
            create_config(True)
        else:
            print("Exiting...")
            exit(0)
    else:
        print("No config file found, Let's create one")
        create_config(False)

    save_config(config_dict)

    print("\nConfiguration saved successfully")
    print("You can now run the client")
    print("\nTo run the client, run the following command:")
    print("python3 client.py\n")
    file = open('cron.txt', 'w')
    capture_string = "#<--start of Raspcapture crons\n# capture after every hour\n0 */1 * * * python "+base_dir+"/capture.py"
    send_string = "\n# send after every 4 hours\n0 */4 * * * python "+base_dir+"/client.py"+"\n#<--end of Raspcapture crons"
    file.write(capture_string+send_string)
    file.close()
    print("Note: The configurations created a cron.txt file")
    print("Please open that file, open terminal and type")
    print("crontab -e")
    print("In the crontab, add or change information identical to that in cron.txt")
    input("Please type anything to verify that you have seen the information above and will execute it. ")
    print("Thanks. Enjoy!")
