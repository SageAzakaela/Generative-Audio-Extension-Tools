import os
import random
import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
from pydub import AudioSegment
import shutil
import zipfile
import uuid
from PIL import Image, ImageTk
import time
import atexit
import threading  # Import the threading module


## THIS VERSION DOESN'T SUPPORT SEEDS ##

# Variable to store the temporary directory path
temp_dir = "TEMP"
metadata = {}  # Store metadata globally
progress = None  # Progress bar widget
composition_thread = None  # Thread for composition generation

# Function to update the progress bar
def update_progress(step, total_steps):
    if progress is not None:
        progress["value"] = step
        app.update_idletasks()

# Function to create a random composition from layers
def generate_random_composition():
    global temp_dir, metadata, progress, composition_thread

    # Ensure a composition thread is not running
    if composition_thread and composition_thread.is_alive():
        return

    # Create a new thread for composition generation
    composition_thread = threading.Thread(target=generate_composition_in_thread)
    composition_thread.start()

# Function to generate composition in a separate thread
def generate_composition_in_thread():
    global temp_dir, metadata, progress
    gae_file_path = gae_file_entry.get()

    # Delete the temporary directory if it exists
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    # Ensure the temporary directory exists or create it
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Extract the contents of the .gae file into the temporary directory
    with zipfile.ZipFile(gae_file_path, 'r') as gae_zip:
        gae_zip.extractall(temp_dir)

    # Get a list of folders in the temporary directory, each folder represents a layer
    layer_folders = [os.path.join(temp_dir, name) for name in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, name))]

    if not layer_folders:
        print("No layers found in the .gae file.")
        return

    # Load metadata from the settings file
    metadata = {}
    for root, _, files in os.walk(temp_dir):
        for file in files:
            if file == "settings.txt":
                with open(os.path.join(root, file), "r") as settings_file:
                    for line in settings_file:
                        key, value = line.strip().split(": ")
                        metadata[key] = value

    artist_name = metadata.get("artist", "Unknown Artist")
    track_name = metadata.get("track_name", "Unknown Track")
    bpm = metadata.get("bpm", "Unknown BPM")
    key = metadata.get("key", "Unknown Key")

    # Create a "Composition" folder within the TEMP folder
    composition_folder = os.path.join(temp_dir, "Composition")
    if not os.path.exists(composition_folder):
        os.makedirs(composition_folder)

    # Display metadata
    display_metadata_and_cover_art()

    # Create empty layers for the composition
    layers = [AudioSegment.silent(duration=0) for _ in range(len(layer_folders))]

    total_steps = len(layer_folders)
    progress = Progressbar(app, orient="horizontal", length=100, mode="determinate")
    progress.pack()
    progress["maximum"] = total_steps

    for i, layer_folder in enumerate(layer_folders):
        # Get a list of WAV files in each layer folder
        wav_files = [f for f in os.listdir(layer_folder) if f.endswith(".wav")]
        if not wav_files:
            print(f"No WAV files found in layer {i + 1}. Skipping this layer.")
            update_progress(i + 1, total_steps)
            continue

        # Shuffle the list of WAV files to create a random arrangement for each layer
        random.shuffle(wav_files)

        # Append each WAV file to the corresponding layer
        for wav_file in wav_files:
            audio = AudioSegment.from_wav(os.path.join(layer_folder, wav_file))
            layers[i] += audio

        update_progress(i + 1, total_steps)

    # Overlay all layers to create the composition
    composition = layers[0]
    for layer in layers[1:]:
        composition = composition.overlay(layer)

    # Generate a unique ID for the filename
    unique_id = uuid.uuid4().hex

    # Save the resulting composition as a temporary WAV file in the "Composition" folder
    composition.export(os.path.join(composition_folder, f"RandomComposition_{unique_id}.wav"), format="wav")

    # Initialize pygame mixer and play the composition
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.load(os.path.join(composition_folder, f"RandomComposition_{unique_id}.wav"))
    pygame.mixer.music.play()
    print("Playing composition...")

    # Hide and remove the progress bar
    if progress is not None:
        progress.pack_forget()
        progress.destroy()
    progress = None

# Function to stop the currently playing composition and clean up the temporary directory
def stop_composition():
    # Check if pygame mixer is initialized and music is playing
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    # Clean up the temporary folder
    cleanup_temp_folder()
    print("Composition stopped and temporary files deleted")

# Function to display metadata and cover art after selecting a file
def display_metadata_and_cover_art():
    global metadata
    artist_name = metadata.get("artist", "Unknown Artist")
    track_name = metadata.get("track_name", "Unknown Track")
    bpm = metadata.get("bpm", "Unknown BPM")
    key = metadata.get("key", "Unknown Key")

    # Display metadata
    metadata_artist_label.config(text="Artist:")
    metadata_artist_value.config(text=artist_name)
    metadata_track_label.config(text="Track:")
    metadata_track_value.config(text=track_name)
    metadata_bpm_label.config(text="BPM:")
    metadata_bpm_value.config(text=bpm)
    metadata_key_label.config(text="Key:")
    metadata_key_value.config(text=key)

    # Load and display cover art (PNG)
    cover_art_path = os.path.join(temp_dir, "cover_art.png")

    if os.path.exists(cover_art_path):
        cover_art_image = Image.open(cover_art_path)
        cover_art_photo = ImageTk.PhotoImage(cover_art_image)
        cover_art_label.config(image=cover_art_photo)
        cover_art_label.image = cover_art_photo
        cover_art_label.pack()
    else:
        print("Cover art image not found.")

# Function to stop all playback and clean up when the window is closed

# Function to stop all playback and clean up when the window is closed
def on_closing():
    # Stop Pygame playback
    pygame.mixer.music.stop()
    # Clean up the temporary folder
    cleanup_temp_folder()
    app.destroy()


def cleanup_temp_folder():
    if os.path.exists(temp_dir):
        # Close any active Pygame mixer instances
        pygame.mixer.quit()
        # Delete the temporary folder and its contents
        shutil.rmtree(temp_dir)

# Register the cleanup_temp_folder function to run on exit
atexit.register(cleanup_temp_folder)

# Create the main application window
app = tk.Tk()
app.title("gaePlayer")

# Connect the on_closing function to the window's closing event
app.protocol("WM_DELETE_WINDOW", on_closing)

# Create and place input fields, labels, and buttons
gae_file_label = tk.Label(app, text="Select a .gae file:")
gae_file_label.pack()
gae_file_entry = tk.Entry(app)
gae_file_entry.pack()

browse_button = tk.Button(app, text="Browse", command=lambda: gae_file_entry.insert(0, filedialog.askopenfilename(filetypes=[("GAE files", "*.gae")])))
browse_button.pack()

generate_button = tk.Button(app, text="Generate Random Composition", command=generate_random_composition)
generate_button.pack()

stop_button = tk.Button(app, text="Stop Composition", command=stop_composition)
stop_button.pack()

metadata_frame = tk.Frame(app)
metadata_frame.pack()

metadata_artist_label = tk.Label(metadata_frame, text="Artist:")
metadata_artist_label.pack(side="left")
metadata_artist_value = tk.Label(metadata_frame, text="", wraplength=200)
metadata_artist_value.pack(side="left")

metadata_track_label = tk.Label(metadata_frame, text="Track:")
metadata_track_label.pack(side="left")
metadata_track_value = tk.Label(metadata_frame, text="", wraplength=200)
metadata_track_value.pack(side="left")

metadata_bpm_label = tk.Label(metadata_frame, text="BPM:")
metadata_bpm_label.pack(side="left")
metadata_bpm_value = tk.Label(metadata_frame, text="", wraplength=200)
metadata_bpm_value.pack(side="left")

metadata_key_label = tk.Label(metadata_frame, text="Key:")
metadata_key_label.pack(side="left")
metadata_key_value = tk.Label(metadata_frame, text="", wraplength=200)
metadata_key_value.pack(side="left")

cover_art_label = tk.Label(app)
cover_art_label.pack()

app.mainloop()
