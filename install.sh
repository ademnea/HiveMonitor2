#!/bin/bash
apt update
apt install  libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
pip install -r requirements.txt
apt install -y gpac