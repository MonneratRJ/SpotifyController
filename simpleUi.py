import tkinter as tk
from tkinter import ttk
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import json
from PIL import Image, ImageTk  # Make sure to install Pillow: pip install Pillow

# Load Spotify API credentials from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

spotify_config = config.get('spotify', {})
SPOTIPY_CLIENT_ID = spotify_config.get('client_id', 'your_client_id')
SPOTIPY_CLIENT_SECRET = spotify_config.get('client_secret', 'your_client_secret')
SPOTIPY_REDIRECT_URI = spotify_config.get('redirect_uri', 'your_redirect_uri')

# Set up Spotify authentication
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=["user-modify-playback-state"])
token_info = sp_oauth.get_cached_token()

# Set up Spotipy with the authentication token
sp = spotipy.Spotify(auth=token_info['access_token'])

def get_playback_state():
    playback_state = sp.current_playback()
    if playback_state is not None:
        return playback_state.get('is_playing', False)
    return False

def update_play_pause_button():
    is_playing = get_playback_state()
    button_image = pause_icon if is_playing else play_icon
    play_pause_button.configure(image=button_image)
    play_pause_button.image = button_image  # Keep a reference to prevent garbage collection

def play_pause():
    playback_state = get_playback_state()
    if playback_state:
        sp.pause_playback()
    else:
        sp.start_playback()
    update_play_pause_button()

def next_track():
    sp.next_track()
    update_play_pause_button()

def previous_track():
    sp.previous_track()
    update_play_pause_button()

# Tkinter GUI
root = tk.Tk()
root.title("Spotify Controller")
root.attributes('-topmost', True)  # Always on top

# Load icons
play_icon = ImageTk.PhotoImage(Image.open("templates/img/play_icon.png"))  # Replace with your actual file name
pause_icon = ImageTk.PhotoImage(Image.open("templates/img/pause_icon.png"))  # Replace with your actual file name
next_icon = ImageTk.PhotoImage(Image.open("templates/img/next_icon.png"))  # Replace with your actual file name
previous_icon = ImageTk.PhotoImage(Image.open("templates/img/previous_icon.png"))  # Replace with your actual file name

# Create buttons with icons
previous_button = ttk.Button(root, image=previous_icon, command=previous_track)
play_pause_button = ttk.Button(root, image=play_icon, command=play_pause)
next_button = ttk.Button(root, image=next_icon, command=next_track)

# Grid layout
previous_button.grid(row=0, column=0, padx=10, pady=10)
play_pause_button.grid(row=0, column=1, padx=10, pady=10)
next_button.grid(row=0, column=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
