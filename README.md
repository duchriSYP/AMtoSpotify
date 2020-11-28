# AMtoSpotify
Converts Apple Music playlist link to a Spotify playlist

Unfortunately,  due to the way the Client-ID and secret are set up, in order to use the script, one would have to get a client-id and secret from the developer page of Spotify.  I use a constants.py file that sets environment variables to the client id, secret, and a redirect uri (local host works fine). Based on where you are located, you may need to change the market for the searches. The default market is the US. In addition, based on possibly slow computer or slow internet, one may need to change the global sleep time variable. Depending on how fast Selenium can process new songs one can adjust it to their needs. 

TO DO: Add functionality for if the song does not exist. Use appearance of new songs to dictate scrolling down, rather than a set timer.
KNOWN ISSUES: Use of artist to help search for songs has issues, most likely with web scraping from the Apple Music site.