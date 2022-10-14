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
async def SearchSpotify(url : str):
    result = spotify.track(url)
    song_name = result['name']
    artist = result['artists'][0]['name']
    final = f"{song_name} {artist}"
    print (final)
    return final

# Uses the youtube library to get all songs from a playlist.
async def GetPlaylist(url : str):
    return Playlist(url)