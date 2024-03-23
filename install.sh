#!/bin/bash
apt update
apt upgrade
apt install  libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev python3-scipy
pip install -r requirements.txt
apt install -y gpac