# Copyright 2024 Allie Law <allie@cloverleaf.app>
# SPDX-License-Identifier: GPL-3.0-or-later
import yt_dlp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import json
import re

# Load cookies from a Netscape cookie file and only set those matching the current URL
def load_cookies_from_netscape(file_path, current_url):
    cookies = []
    with open(file_path, 'r') as file:
        for line in file:
            if not line.startswith("#") and line.strip():  # Skip comments and empty lines
                parts = line.strip().split("\t")
                if len(parts) == 7:
                    cookie = {
                        "domain": parts[0],
                        "httpOnly": parts[1] == "TRUE",
                        "path": parts[2],
                        "secure": parts[3] == "TRUE",
                        "expiry": int(parts[4]),
                        "name": parts[5],
                        "value": parts[6]
                    }
                    # Adjust the domain if necessary
                    if cookie["domain"].startswith("."):
                        cookie["domain"] = cookie["domain"][1:]
                    
                    # Only add cookies that match the current domain
                    if current_url.find(cookie["domain"]) != -1:
                        cookies.append(cookie)
    return cookies

def get_video_info(video_url, driver):
    # Open the URL
    driver.get(video_url)
    # Wait a second for the page to load more
    sleep(1)
    
    info = {'url':video_url}

    # Select the element using a query string and extract its text
    title_query_string = '.head.video-title'
    title_element = driver.find_element(By.CSS_SELECTOR, title_query_string)
    title_text = title_element.text
    info['title'] = title_text

    date_query_string = '[data-meta-field-name="release_dates"]' 
    date_element = driver.find_element(By.CSS_SELECTOR, date_query_string)
    date_text = date_element.get_attribute("data-meta-field-value")
    info['date'] = date_text
    
    description_query_string = '[data-text-show-less="Show less"]'
    description_element = driver.find_element(By.CSS_SELECTOR, description_query_string)
    # Need to use textContent to get stuff hidden by "show more"
    description_text = description_element.get_attribute("textContent")
    info['description'] = description_text.strip() # Strip of whitespace on either end
    
    try:
        series_query_string = 'h3.series-title > a'
        series_element = driver.find_element(By.CSS_SELECTOR, series_query_string)
        series_text = series_element.text
        info['series'] = series_text
    except (NoSuchElementException):
        # No series
        pass

    try:
        season_episode_query_string = 'h5 >a.site-font-secondary-color'
        season_episode_element = driver.find_element(By.CSS_SELECTOR, season_episode_query_string)
        season_episode_text = season_episode_element.get_attribute("textContent")
        season = re.search("Season (\\d+)", season_episode_text).group(1)
        info['season'] = int(season)
        episode = re.search("Episode (\\d+)", season_episode_text).group(1)
        info['episode'] = int(episode)
            
    # Errors caused by not having a season, episode
    except (NoSuchElementException, AttributeError):
        # No season/episode
        pass
    

    return info

def download_playlist_info(playlist_url):
    
    videos = []
    
    # Path to Netscape cookies file
    cookies_file_path = "../dropout_cookies.txt"

    # Configure options for yt-dlp
    ydl_opts = {
        'skip_download': True,    # Don't download the video
        'extract_flat': 'in_playlist',  # Extract metadata without downloading
        'cookiefile': cookies_file_path, # Cookies to make it work
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract playlist info
        playlist_dict = ydl.extract_info(playlist_url, download=False)
        # print(playlist_dict)

        # Initialize the WebDriver (you might need to specify the path to the WebDriver executable)
        driver = webdriver.Firefox()  # or use Chrome, Edge, etc.

        # Load the playlist page so we can set cookies
        driver.get(playlist_url)

        # Load cookies from Netscape file that match the current domain
        cookies = load_cookies_from_netscape(cookies_file_path, playlist_url)
        
        # Add cookies to the browser session
        for cookie in cookies:
            driver.add_cookie(cookie)
        
        # Iterate over each entry (video) in the playlist
        for video in playlist_dict['entries']:
            video_url = video.get('url').replace('/new-releases', '') # Use the proper page so the Season/Episode loads
            metadata = get_video_info(video_url, driver)
            videos.append(metadata)

        # Close the browser
        driver.quit()
        
    return videos
    

# Example URLs
video = "https://www.dropout.tv/new-releases/videos/either-nothing-or-ube"
new_videos_playlist = "https://www.dropout.tv/new-releases"

# Download playlist info
videos_metadata = download_playlist_info(new_videos_playlist)


with open('videos_metadata.json', 'w') as f:
    json.dump(videos_metadata, f)
