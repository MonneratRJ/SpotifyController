import tkinter as tk
from tkinter import ttk, scrolledtext
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import json
import requests
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

def update_track_info():
    current_playback = sp.current_playback()
    if current_playback is not None:
        # Update track information
        artist_name = current_playback.get('item', {}).get('artists', [{}])[0].get('name', 'Unknown Artist')
        song_name = current_playback.get('item', {}).get('name', 'Unknown Song')
        track_info = f"{artist_name} - {song_name}"
        track_info_label.delete(1.0, tk.END)  # Clear previous content
        track_info_label.insert(tk.END, track_info)

        # Update album cover
        album_cover_url = current_playback.get('item', {}).get('album', {}).get('images', [{}])[0].get('url')
        if album_cover_url:
            album_cover = ImageTk.PhotoImage(Image.open(requests.get(album_cover_url, stream=True).raw).resize((100, 100)))
            album_cover_image.configure(image=album_cover)
            album_cover_image.image = album_cover  # Keep a reference to prevent garbage collection
        else:
            # Display a default image if no album cover is available
            default_image = ImageTk.PhotoImage(Image.open("templates/img/default_album_cover.png"))  # Replace with your default image
            album_cover_image.configure(image=default_image)
            album_cover_image.image = default_image  # Keep a reference to prevent garbage collection

def update_play_pause_button():
    is_playing = get_playback_state()
    update_track_info()
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

# Function to handle keyboard shortcuts
def on_key(event):
    if event.keysym.lower() == 'q' and event.state == 4:
        print('Previous track.')
        previous_track()
    elif event.keysym.lower() == 'w' and event.state == 4:
        print('Pause/Resume.')
        play_pause()
    elif event.keysym.lower() == 'e' and event.state == 4:
        print('Next track.')
        next_track()
    # else:
    #    print('Keypressed: '+event.keysym.lower())

# Tkinter GUI
root = tk.Tk()
root.title("Spotify Controller")
root.attributes('-topmost', True)  # Always on top

# Create a scrolledtext widget for displaying current track information
track_info_label = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=30, height=3)
track_info_label.grid(row=1, column=0, columnspan=3, pady=0, padx=5)

# Create an Image widget for displaying the album cover
album_cover_image = tk.Label(root)
album_cover_image.grid(row=0, column=0, columnspan=3, pady=10)

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
previous_button.grid(row=2, column=0, padx=10, pady=10)
play_pause_button.grid(row=2, column=1, padx=10, pady=10)
next_button.grid(row=2, column=2, padx=10, pady=10)

# Call the update_play_pause_button() to set the initial button state
update_play_pause_button()

# Call the update_track_info() to update player state
update_track_info()

# Bind keyboard shortcuts to functions
root.bind("<Control-q>", lambda event: previous_track())
root.bind("<Control-w>", lambda event: play_pause())
root.bind("<Control-e>", lambda event: next_track())

# Bind additional keyboard shortcuts (for testing purposes)
# root.bind("<Control-a>", lambda event: print("Ctrl+A pressed"))

# Bind the general on_key function to handle all keyboard events
root.bind("<Key>", on_key)

# Start the Tkinter event loop
root.mainloop()
