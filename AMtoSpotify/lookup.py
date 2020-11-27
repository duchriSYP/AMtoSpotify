import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import datetime

CLIENT_ID = '6f86ac325ffb4fbaa4c5a786ab1dada8'
CLIENT_SECRET = 'c666a92747d645ebac45e3cd882aff85'

AUTH_URL = 'https://accounts.spotify.com/api/token'
AUTH_HEADER = {'Authorization': 'Bearer {}'.format(spotifyToken)}

SCROLL_PAUSE_TIME = 2


# code start from /u/Hairshorts
class SpotifyDB:
    def __init__(self):
        self.conn = sqlite3.connect('spotify.db')
        self.c = self.conn.cursor()

    def insert_playlist(self, newPlaylistId, playlistName):
        self.c.execute("INSERT INTO playlists_created (spotify_playlist_id, playlist_name) VALUES (?, ?)", (newPlaylistId, playlistName))
        self.conn.commit()

    def get_access_token(self):
        self.c.execute("SELECT value FROM tokens WHERE token_type = 'access_token'")
        spotify_token = c.fetchone()[0]
        test_request = requests.get('https://api.spotify.com/v1/me', headers=AUTH_HEADER)
        if test_request.status_code in [401, 403]:
            spotify_token = self._get_new_access_token()
        return spotify_token

    def _get_new_access_token(self):
        self.c.execute("SELECT value FROM tokens WHERE token_type = 'encoded_basic_token'")
        basic_token = self.c.fetchone()[0]
        self.c.execute("SELECT value FROM tokens WHERE token_type = 'refresh_token'")
        refresh_token = self.c.fetchone()[0]

        req_header = {'Authorization': 'Basic {}'.format(basic_token)}
        req_body = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
        r = requests.post('https://accounts.spotify.com/api/token', headers=req_header, data=req_body)
        res_json = r.json()

        new_token = res_json['access_token']
        # update token in db
        self.c.execute("UPDATE tokens SET value = ? WHERE token_type = 'access_token'", (new_token,))
        self.conn.commit()

        return new_token

    def close(self):
        self.c.close()
        self.conn.close()


# creates a playlist with the name and creator from the original playlist and  and the given songs, no duplicates
def create_playlist(name, song_id):
    find_song()

# removes excess info (feat or prod), unsure if useful
# def true_song_name(song_name):


# gets song id using Spotify search endpoint using the name and artist of song
def find_song(song_name, artist):
    song_ID = ''

    query_params = '?q={}&type=track&market=US&limit=5'.format(urllib.parse.quote(song_name))
    request = requests.get('https://api.spotify.com/v1/search' + query_params, headers=AUTH_HEADER)
    results = request.json()

    # iterate through results
    for result in results['tracks']['items']:
        # if at least one artist matches and names are approx. equal, set songId
        if  song_name.lower() in result['name'].lower():
            song_ID = result['id']
            break

    return song_ID


# gets the html of the entire playlist based on url
def load_html(url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    try:
        driver.get('https://music.apple.com/us/playlist/pl.u-d2b0kXXCDZ01JK')
        time.sleep(.5)
        driver.find_element_by_tag_name('body').click()
        last_source = driver.page_source
        while True:
            driver.find_element_by_tag_name('body').send_keys(Keys.END)
            time.sleep(SCROLL_PAUSE_TIME)
            new_source = driver.page_source
            if len(new_source) == len(last_source):
               break
            last_source = new_source
    finally:
        driver.quit()
        return driver.page_source


def main():
    playlist_from_AM = input("Enter URL of playlist: ")
    db = SpotifyDB()
    spotify_token = db.get_access_token()

    soup = BeautifulSoup(load_html(playlist_from_AM), 'html.parser')

    # close database connection, including cursor
    db.close()


if __name__ == "__main__":
    main()