# Copyright 2024 Allie Law <allie@cloverleaf.app>
# SPDX-License-Identifier: GPL-3.0-or-later
from pythorhead import Lemmy
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

username = os.getenv("LEMMY_USERNAME")
password = os.getenv("LEMMY_PASSWORD")

lemmy = Lemmy("https://lemmy.blahaj.zone",request_timeout=5)
lemmy.log_in(username, password)
dropout_community = lemmy.discover_community("dropout")


serial_title_template = "{title} - {series} S{season}E{episode:02}"
one_off_title_template = "{title}"


with open('videos_metadata.json', 'r') as file:
    videos = json.load(file)
    
    for video in videos:        
        
        search_results = lemmy.search(video['title'], community_id=dropout_community)
        posted_already = False
        
        for result in search_results['posts']:            
            # If this search result has the same url
            if result['post']['url'] == video['url']: 
                print("Skip {}, already posted: {}".format(video['title'], result['post']['ap_id']))
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
        

        print("Title:", title)
        print("Description:", description)
        response = input ("Post? (Y/N)")
        
        if response.lower()[:1] == "y":
            lemmy.post.create(dropout_community, name=title, body=description, url=video['url'])
            print("posted")
        else:
            print("not posting")
        
        # Check if this has already been posted
        
            