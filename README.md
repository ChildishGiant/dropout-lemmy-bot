# Dropout Bot for Lemmy

A quickly cobbled-together script that keeps [lemmy.blahaj.zone/c/dropout](https://lemmy.blahaj.zone/c/dropout) up to date.

Currently the way to use this is:
```sh
# Create a python venv and install the required libs
python -m venv env && . ./env/bin/activate 
python -m pip install -r requirements.txt
# Download the 20 latest videos and store their metadata in videos_metadata.json
python new_video_metadata.py
# Parse that data, checking if it's already been posted and asking to post it if not
python lemmy_poster.py
```