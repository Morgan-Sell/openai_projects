import argparse

import spotipy
from dotenv import dotenv_values
import openai
import json

config = dotenv_values(".env")

openai.api_key = config["OPENAI_API_KEY"]

parser = argparse.ArgumentParser(description="Simple command line playlist utility")
parser.add_argument("-p", type=str, help="The prompt to describe the playlist")
parser.add_argument("-n", type=int, default=8, help="The number of songs to add to the playlist")

args = parser.parse_args()

def get_playlist(prompt, count):
    example_json = """
    [
      {"song": "Everybody Hurts", "artist": "R.E.M."},
      {"song": "Hurt", "artist": "Johnny Cash"},
      {"song": "Someone Like You", "artist": "Adele"},
      {"song": "Nothing Compares 2 U", "artist": "Sinéad O'Connor"},
      {"song": "Tears in Heaven", "artist": "Eric Clapton"}
    ]
    """

    messages = [
        {"role": "system", "content": """You are a helpful playlist generating assistant. 
        You should generate a list of songs and their artists according to a text prompt.
        Your should return a JSON array, where each element follows this format: {"song": <song_title>, "artist": <artist_name>}
        Respond with only json. Do not include any text outside of the brackets.
        """
        },
        {"role": "user", "content": "Generate a playlist of songs based on this prompt: super super sad songs"},
        {"role": "assistant", "content": example_json},
        {"role": "user", "content": f"Generate a playlist of {count} songs based on this prompt: {prompt}"},
    ]

    response = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=400,
    )

    playlist = json.loads(response["choices"][0]["message"]["content"])
    return playlist


playlist = get_playlist(args.p, args.n)
print(playlist)



sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config["SPOTIFY_CLIENT_ID"],
        client_secret=config["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="http://localhost:9999",
        scope="playlist-modify-private",
    )
)

current_user = sp.current_user()

assert current_user is not None

track_ids = []
for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}"

    search_results = sp.search(q=query, type="track", limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])

created_playlist = sp.user_playlist_create(
    current_user["id"],
    public=False,
    name=args.p,
)

sp.user_playlist_add_tracks(
    current_user["id"],
    created_playlist["id"],
    track_ids,
)