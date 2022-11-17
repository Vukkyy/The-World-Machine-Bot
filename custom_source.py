import spotipy
from pytube import Playlist
from spotipy.oauth2 import SpotifyClientCredentials
from os import getenv

credentials = SpotifyClientCredentials(
    client_id=getenv('CLIENTID'),
    client_secret=getenv('CLIENT-SECRET')
)

spotify = spotipy.Spotify(client_credentials_manager=credentials)
# Uses the URL the user puts in, searches spotify and then uses the name and artist to search youtube.
async def SearchSpotify(url : str, is_url : bool = True):
    result = None
    
    if is_url:
        result = spotify.track(url)
    else:
        result = spotify.search(url)
        result = result['tracks']['items'][0]
    song_name = result['name']
    artist = result['artists'][0]['name']
    art = result['album']['images'][0]['url']
    final = {'name' : song_name, 'artist' : artist, 'art' : art}
    return final

# Uses the youtube library to get all songs from a playlist.
async def GetPlaylist(url : str):
    return Playlist(url)