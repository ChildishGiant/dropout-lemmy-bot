# Copyright 2024 Allie Law <allie@cloverleaf.app>
# SPDX-License-Identifier: GPL-3.0-or-later
from pythorhead import Lemmy
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime, timedelta

load_dotenv()

username = os.getenv("LEMMY_USERNAME")
password = os.getenv("LEMMY_PASSWORD")

lemmy = Lemmy("https://lemmy.blahaj.zone",request_timeout=5)
lemmy.log_in(username, password)
dropout_community = lemmy.discover_community("dropout")


serial_title_template = "{title} - {series} S{season}E{episode:02}"
one_off_title_template = "{title}"

mode = "automatic" # "manual"
recency = 5 # How many videos back do we want to check

def to_post (video, index):
    
    if mode == "automatic":
        # If it's one of the x most recent videos
        if index < 5:
            return True
        else:
            print ("Skipping {}, too long ago".format(video['title']))
            return False

    elif mode == "manual":
        print("Title:", video['title'])
        print("Description:", video['description'])
        response = input ("Post? (Y/N)")
        if response.lower()[:1] == "y":
            return True
        else:
            return False

with open('videos_metadata.json', 'r') as file:
    videos = json.load(file)
    
    for index in range(0, len(videos)):        

        video = videos[index]
        
        # Check if we want to post the video before searching for it etc
        if to_post(video, index):
            
            # Search for a post with this title
            search_results = lemmy.search(video['title'], community_id=dropout_community)
            posted_already = False
            
            for result in search_results['posts']:            
                # If this search result has the same url
                if result['post']['url'] == video['url']: 
                    print("Skipping {}, already posted: {}".format(video['title'], result['post']['ap_id']))
                    posted_already = True # skip it
            
            if posted_already:
                continue # Skip already posted
            
            description = video['description']

            tags_header = description.find("Tags") # Get the position for the "Tags" text
            description = description[:tags_header].strip() # Cut off tags
            
            title = ""
            
            
            try:
                # Set title to have the series season:episode in
                title = serial_title_template.format_map(video)
            except KeyError:
                # If it's not got a series, season or episode just use the title
                title = one_off_title_template.format_map(video)
            
            outcome = lemmy.post.create(
                dropout_community, # Community to post to 
                name=title, 
                body=description, 
                url=video['url'], 
                language_id=0 # Undefined language so that people actually see it
                )
            print("Posted {}: {}".format(video['title'], outcome['post_view']['post']['ap_id']))