from flask import Flask, jsonify, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.client import SpotifyException
import json

app = Flask(__name__)

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print("Error: Config file not found.")
        return None

def authenticate_spotify():
    config = load_config()
    if config:
        spotify_config = config.get('spotify', {})
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=spotify_config.get('client_id'),
            client_secret=spotify_config.get('client_secret'),
            redirect_uri=spotify_config.get('redirect_uri'),
            scope=["user-modify-playback-state",'user-read-playback-state']
        ))
    else:
        return None

def do_request(func):
    def wrapper(*args, **kwargs):
        sp = authenticate_spotify()
        try:
            return func(sp, *args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 401:
                # Refresh the access token and retry the request
                sp = authenticate_spotify()  # Re-authenticate
                return func(sp, *args, **kwargs)
            else:
                # Handle other errors
                print(f"Spotify API Error: {e}")
                return f"Spotify API Error: {e}"
    return wrapper

@do_request
def play_next_track(sp):
    sp.next_track()
    return "Playing next track"

@do_request
def play_previous_track(sp):
    sp.previous_track()
    return "Playing previous track"

@do_request
def toggle_pause_resume(sp):
    playback_state = sp.current_playback()
    
    if playback_state is not None:
        if playback_state['is_playing']:
            sp.pause_playback()
        else:
            sp.start_playback()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Unable to retrieve playback state'})
    
@do_request
def get_playback_state(sp):
    playback_state = sp.current_playback()

    if playback_state is not None:
        is_playing = playback_state.get('is_playing', False)
        return jsonify({'is_playing': is_playing})
    else:
        return jsonify({'error': 'Unable to retrieve playback state'})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/next")
def next_track():
    return play_next_track()

@app.route("/previous")
def previous_track():
    return play_previous_track()

@app.route("/toggle-pause-resume")
def toggle_pause_resume_route():
    return toggle_pause_resume()

@app.route("/get-playback-state")
def get_playback_state_route():
    return get_playback_state()

if __name__ == "__main__":
    app.run(debug=True)
