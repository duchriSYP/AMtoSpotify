import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import urllib.parse

def main():
    '''try:
        hnhhRequest = requests.get('https://music.apple.com/us/playlist/pl.u-d2b0kXXCDZ01JK', params={"offset": 200})
        topSongsHtml = hnhhRequest.text
    except:
        print('error getting html')
    soup = BeautifulSoup(topSongsHtml, 'html.parser')
    songs = soup.find_all('div', class_='col col-song')
    print(len(songs))
    print(songs[0].find('div', class_="song-name typography-label").text)

    artists = songs[0].find_all('a', class_="dt-link-to")
    print([artist.text for artist in artists])'''
    SCROLL_PAUSE_TIME = 2
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

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        songs = soup.find_all('div', class_='col col-song')
        print(len(songs))
        print(songs[0].find('div', class_="song-name typography-label").text)

        artists = songs[0].find_all('a', class_="dt-link-to")
        print([artist.text for artist in artists])
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

