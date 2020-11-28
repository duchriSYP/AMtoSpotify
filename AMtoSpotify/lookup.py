import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import constants
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

SCROLL_PAUSE_TIME = 2


# creates a playlist with the name and creator from the original playlist and  and the given songs, no duplicates
def create_playlist(sp, playlist_name, song_ids):
    now = datetime.datetime.now()
    user_id = sp.me()['id']
    playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False,
                                          description='Created by script on ' + now.strftime("%m/%d/%Y"))['id']

    num_total = 0
    tracks = []
    for song_id in song_ids:
        # can only add 100 items at a time based on Spotify API
        if len(tracks) < 100:
            tracks.append(song_id)
        else:
            sp.playlist_add_items(playlist_id, ['spotify:track:' + track for track in tracks])
            tracks = [song_id]
        num_total += 1
    # if there are extra remaining tracks, add them to playlist
    if len(tracks) > 0:
        sp.playlist_add_items(playlist_id, ['spotify:track:' + track for track in tracks])

    return num_total


# removes any trailing details from song name (i.e. "(prod. by ...)" or "feat ...")
def get_true_song_name(song_name):
    true_song_name = song_name[:song_name.index(' (')] if '(' in song_name else song_name
    true_song_name = true_song_name[:true_song_name.index(' feat')] if 'feat' in true_song_name else true_song_name
    # it seems that apostrophes do not search correctly in the API, so changes all to spaces instead
    true_song_name = true_song_name.replace('\'', ' ')
    return true_song_name


# gets song id using Spotify search endpoint using the name and artist of song
# lots of issues with extracting artists info from html
'''def find_song(sp, song_name, artists):
    #query = "artist: " + ", ".join(artists) + " track: " + song_name
    query = "track: " + song_name
    return sp.search(q=query, type='track', market='US')['tracks']['items'][0]['id']'''


# gets song id using Spotify search endpoint using the name and artist of song
def find_song(sp, song_name):
    query = "track: " + song_name
    return sp.search(q=query, limit=1, type='track', market='US')['tracks']['items'][0]['id']


# gets the html of the entire playlist based on url
def load_html(url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    try:
        driver.get(url)
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
        return last_source


def main():
    playlist_from_AM = input("Enter URL of playlist: ")
    scope = 'user-read-private playlist-read-private playlist-modify-private'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    now = datetime.datetime.now()
    user_id = sp.me()['id']

    # gets all html from the fully loaded page
    soup = BeautifulSoup(load_html(playlist_from_AM), 'html.parser')
    # gets general html of all the songs
    songs_html = soup.find_all('div', class_='col col-song')
    # gets all song names
    song_names = [song.find('div', class_="song-name typography-label").text for song in songs_html]
    song_names = [get_true_song_name(song_name) for song_name in song_names]
    # gets all artists and puts them into list of strings
    #song_artists = [song.find_all('a', class_="dt-link-to") for song in songs_html]
    #song_artists = [[artist.text for artist in artists] for artists in song_artists]
    playlist_name = soup.find('title').text

    # gets song id of every song using song_names and song_artists
    #song_ids = [find_song(sp, song[0], song[1]) for song in list(zip(song_names, song_artists))]
    song_ids = [find_song(sp, song_name) for song_name in song_names]

    # see if expected is equal to number fo actual, also creates the playlist here
    print("Expected Number of Songs: " + str(len(song_names)))
    print("Actual Number of Songs: " + str(create_playlist(sp, playlist_name, song_ids)))
    #print(sp.search(q='artist: ' + 'Juice WRLD' + ' track: ' + 'I\'ll Be Fine', type='track', market='US'))


if __name__ == "__main__":
    main()
