from flask import Flask, render_template, request
from deepface import DeepFace
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Your Spotify developer credentials (create from https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID = "86c47302d7e14b7b8fc82c4819737052"
SPOTIFY_CLIENT_SECRET = "3a81c3d7169b4b678602aa6a5a1365b5"

# Set up Spotify authentication
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Fetch Spotify songs based on emotion
def get_spotify_tracks(emotion):
    query_map = {
        "happy": "happy mood",
        "sad": "sad songs",
        "angry": "rage playlist",
        "neutral": "lofi beats",
        "fear": "dark ambient",
        "disgust": "emotional cleanse",
        "surprise": "party hits"
    }
    query = query_map.get(emotion.lower(), "mood playlist")
    results = sp.search(q=query, type='track', limit=5)
    songs = []
    for track in results['tracks']['items']:
        name = track['name']
        artist = track['artists'][0]['name']
        url = track['external_urls']['spotify']
        songs.append({"name": name, "artist": artist, "url": url})
    return songs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        image = request.files["image"]
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], "input.jpg")
        image.save(img_path)

        try:
            result = DeepFace.analyze(img_path=img_path, actions=["emotion"], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            songs = get_spotify_tracks(emotion)
            return render_template("index.html", emotion=emotion, songs=songs)
        except Exception as e:
            return render_template("index.html", emotion="Could not detect", songs=[])

    return render_template("index.html", emotion=None, songs=[])

if __name__ == "__main__":
    app.run(debug=True)
