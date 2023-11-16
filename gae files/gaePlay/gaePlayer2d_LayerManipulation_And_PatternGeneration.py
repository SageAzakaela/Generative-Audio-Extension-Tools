import os
import random
import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
from pydub import AudioSegment
import shutil
import zipfile
from PIL import Image, ImageTk
import atexit
import threading  # Import the threading module

# Variable to store the temporary directory path
seed = None
temp_dir = "TEMP"
metadata = {}  # Store metadata globally
progress = None  # Progress bar widget
composition_thread = None  # Thread for composition generation

# Global variable to store the indices of disabled layers
disabled_layers = []
layer_folders = []

# Function to open the layer control window
def open_layer_control_window():
    global layer_folders

    # Get the .gae file path
    gae_file_path = gae_file_entry.get()

    # Extract the contents of the .gae file into the temporary directory
    with zipfile.ZipFile(gae_file_path, 'r') as gae_zip:
        gae_zip.extractall(temp_dir)
        print(f"Extracted contents of {gae_file_path} to {temp_dir}")

    # Get a list of folders in the temporary directory, each folder represents a layer
    layer_folders = [os.path.join(temp_dir, name) for name in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, name))]

    layer_control_window = tk.Toplevel(app)
    layer_control_window.title("Layer Control")

    # Create checkboxes for each layer
    layer_checkboxes = []
    for i, layer_folder in enumerate(layer_folders):
        layer_name = os.path.basename(layer_folder)
        var = tk.IntVar()
        checkbox = tk.Checkbutton(layer_control_window, text=layer_name, variable=var)
        checkbox.grid(row=i, column=0, sticky=tk.W)
        layer_checkboxes.append(var)

    # Button to apply and close the layer control window
    apply_button = tk.Button(layer_control_window, text="Apply", command=lambda: apply_layer_settings(layer_checkboxes, layer_control_window))
    apply_button.grid(row=len(layer_folders), column=0, columnspan=2)

# Function to apply layer settings and close the layer control window
def apply_layer_settings(layer_checkboxes, layer_control_window):
    global disabled_layers
    disabled_layers = [i for i, var in enumerate(layer_checkboxes) if var.get() == 0]
    layer_control_window.destroy()



# Function to update the progress bar
def update_progress(step, total_steps):
    if progress is not None:
        progress["value"] = step
        app.update_idletasks()


# Function to create a random composition from layers
def generate_random_composition():
    stop_composition()
    global temp_dir, metadata, progress, composition_thread, seed

    # Ensure a composition thread is not running
    if composition_thread and composition_thread.is_alive():
        print("Composition thread is already running. Aborting.")
        return

    # Get the seed from the seed entry field
    seed_str = seed_entry.get()

    if seed_str.strip():  # Check if the seed entry field is not empty
        seed = int(seed_str)
        print(f"Using user-provided seed: {seed}")
    elif use_seed_var.get():  # Check if "Use Seed" checkbox is checked
        seed = random.randint(1, 1000000)  # Generate a random seed
        seed_entry.delete(0, tk.END)
        seed_entry.insert(0, str(seed))  # Display the generated seed
        print(f"Generated random seed: {seed}")

    # Get the generation pattern from the user
    generation_pattern = pattern_entry.get()
    print(f"User-defined generation pattern: {generation_pattern}")

    # Create a new thread for composition generation
    composition_thread = threading.Thread(target=generate_composition_in_thread, args=(seed, generation_pattern))
    composition_thread.start()


# Function to generate a composition based on user-defined pattern
def generate_composition_in_thread(seed, generation_pattern):
    global temp_dir, metadata, progress
    print("Generating composition in a separate thread...")
    seed_str = seed_entry.get()
    seed = int(seed_str) if seed_str.isdigit() else None

    random.seed(seed)

    gae_file_path = gae_file_entry.get()

    # Delete the temporary directory if it exists
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print("Deleted existing temporary directory.")
    # Ensure the temporary directory exists or create it
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print(f"Created temporary directory: {temp_dir}")

    # Extract the contents of the .gae file into the temporary directory
    with zipfile.ZipFile(gae_file_path, 'r') as gae_zip:
        gae_zip.extractall(temp_dir)
        print(f"Extracted contents of {gae_file_path} to {temp_dir}")

    # Get a list of folders in the temporary directory, each folder represents a layer
    layer_folders = [os.path.join(temp_dir, name) for name in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, name))]

    if not layer_folders:
        print("No layers found in the .gae file. Aborting.")
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

    # Create a "Composition" folder within the TEMP folder
    composition_folder = os.path.join(temp_dir, "Composition")
    if not os.path.exists(composition_folder):
        os.makedirs(composition_folder)

    # Display metadata
    display_metadata_and_cover_art()

     # Create empty layers for the composition
    layers = [AudioSegment.silent(duration=0) for _ in range(len(layer_folders))]

    total_steps = len(layer_folders) * len(generation_pattern)  # Total steps for progress bar
    progress = Progressbar(app, orient="horizontal", length=100, mode="determinate")
    progress.pack()
    progress["maximum"] = total_steps

    # Define tags for layer processing based on the user-defined pattern
    processing_order = ["_I"] + list(generation_pattern)
    processed_files = set()

# ...
    # Flag to track if the user-defined pattern is exhausted
    pattern_exhausted = False

    # Iterate through the pattern until all phrases are exhausted
    while any(len([f for f in os.listdir(layer) if f.endswith(".wav") and tag in f and f not in processed_files]) > 0
            for tag in processing_order for i, layer in enumerate(layer_folders) if i not in disabled_layers):
        for tag in processing_order:
            for i, layer_folder in enumerate(layer_folders):
                # Skip processing if the layer is disabled
                if i in disabled_layers:
                    continue

                # Get a list of WAV files in each layer folder with the specified tag
                wav_files = [f for f in os.listdir(layer_folder) if f.endswith(".wav") and tag in f and f not in processed_files]
                if not wav_files:
                    continue

                # Process one file with the specified tag
                wav_file = random.choice(wav_files)
                audio = AudioSegment.from_wav(os.path.join(layer_folder, wav_file))

                # Mute sections tagged with "_M"
                if "_M" in wav_file:
                    audio = AudioSegment.silent(duration=len(audio))

                # Append sections tagged with "_R" twice
                if "_R" in wav_file:
                    layers[i] += audio
                    layers[i] += audio

                    # Mark file as processed
                    processed_files.add(wav_file)
                else:
                    layers[i] += audio

                    # Mark file as processed
                    processed_files.add(wav_file)

                update_progress((len(processing_order) * i) + processing_order.index(tag) + 1, total_steps)

                # If the user-defined pattern is exhausted, reset the processed files for "_O" processing
                if all(len([f for f in os.listdir(layer) if f.endswith(".wav") and tag in f and f not in processed_files]) == 0
                    for tag in processing_order[1:] for layer in layer_folders):
                    pattern_exhausted = True

        print("Processed Files:", processed_files)  # Print the processed files for debugging
        print("Pattern Exhausted:", pattern_exhausted)  # Print the pattern exhausted flag for debugging

    # ...


    # Append the outro after the user-defined pattern is exhausted and if it hasn't been appended before
    if pattern_exhausted and not any("_O" in f for f in processed_files):
        print("Appending Outro...")
        for i, layer_folder in enumerate(layer_folders):
            outro_files = [f for f in os.listdir(layer_folder) if f.endswith(".wav") and "_O" in f and f not in processed_files]
            for outro_file in outro_files:
                audio = AudioSegment.from_wav(os.path.join(layer_folder, outro_file))
                layers[i] += audio

                # Mark outro file as processed
                processed_files.add(outro_file)
                update_progress((len(processing_order) * i) + processing_order.index(tag) + 1, total_steps)

#...

    # Overlay all layers to create the composition
    composition = layers[0]
    for layer in layers[1:]:
        composition = composition.overlay(layer)

    # Generate a unique ID for the filename
    unique_id = seed_entry.get() + pattern_entry.get()

    # Save the resulting composition as a temporary WAV file in the "Composition" folder
    composition.export(os.path.join(composition_folder, f"RandomComposition_{unique_id}.wav"), format="wav")

    # Hide and remove the progress bar
    if progress is not None:
        progress.pack_forget()
        progress.destroy()
    progress = None

    # Initialize pygame mixer and play the composition
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.load(os.path.join(composition_folder, f"RandomComposition_{unique_id}.wav"))
    pygame.mixer.music.play()
    print("Playing composition...")



# Function to stop the currently playing composition and clean up the temporary directory
def stop_composition():
    # Check if pygame mixer is initialized and music is playing
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    # Clean up the temporary folder
    cleanup_temp_folder()
    print("Composition stopped and temporary files deleted")

# Function to display metadata and seed value
def display_metadata_and_cover_art():
    global metadata, seed
    seed_str = seed_entry.get()
    metadata_seed_value.config(text=seed_str)

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
        # Open the cover art image
        cover_art_image = Image.open(cover_art_path)

        # Calculate the new width while maintaining the aspect ratio
        original_width, original_height = cover_art_image.size
        new_height = 500
        new_width = int((original_width / original_height) * new_height)

        # Resize the image
        cover_art_image = cover_art_image.resize((new_width, new_height))

        # Convert the resized image to PhotoImage format
        cover_art_photo = ImageTk.PhotoImage(cover_art_image)

        # Update the label with the resized image
        cover_art_label.config(image=cover_art_photo)
        cover_art_label.image = cover_art_photo
        cover_art_label.pack()
    else:
        print("Cover art image not found.")

#Generate a random generation pattern
def randomize_pattern():
    pattern_chars = ["A", "B", "C", "D"]
    random.shuffle(pattern_chars)
    random_pattern = "".join(pattern_chars)
    pattern_entry.delete(0, tk.END)
    pattern_entry.insert(0, random_pattern)

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

# Button to open the layer control window
layer_control_button = tk.Button(app, text="Layer Control", command=open_layer_control_window)
layer_control_button.pack()

# Create and place a checkbox for seed usage
use_seed_var = tk.IntVar()
use_seed_checkbox = tk.Checkbutton(app, text="Use Seed", variable=use_seed_var)
use_seed_checkbox.pack()
# Create and place widgets for seed entry
seed_label = tk.Label(app, text="Random Seed:")
seed_label.pack()
seed_entry = tk.Entry(app)
seed_entry.pack()

# Create and place a text box for the generation pattern
pattern_label = tk.Label(app, text="Generation Pattern:")
pattern_label.pack()
pattern_entry = tk.Entry(app)
pattern_entry.pack()

# Create and place a button to randomize the generation pattern
randomize_button = tk.Button(app, text="Randomize Pattern", command=randomize_pattern)
randomize_button.pack()

generate_button = tk.Button(app, text="Generate Random Composition", command=generate_random_composition)
generate_button.pack()

stop_button = tk.Button(app, text="Stop Composition", command=stop_composition)
stop_button.pack()

metadata_frame = tk.Frame(app)
metadata_frame.pack()

metadata_seed_label = tk.Label(metadata_frame, text="Seed:")
metadata_seed_label.pack(side="left")
metadata_seed_value = tk.Label(metadata_frame, text="", wraplength=200)
metadata_seed_value.pack(side="left")

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

def save_composition():
    global metadata
    # Stop the composition if it's currently playing
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Ask the user for the destination directory
    destination_dir = filedialog.askdirectory(title="Select Destination Directory")

    if not destination_dir:
        print("Save operation canceled by the user.")
        return

    # Construct the source path of the current composition
    composition_folder = os.path.join(temp_dir, "Composition")
    composition_path = os.path.join(composition_folder, f"RandomComposition_{(seed_entry.get() + pattern_entry.get())}.wav")

    if not os.path.exists(composition_path):
        print("No composition to save. Generate a composition first.")
        return

    artist_name = metadata.get("artist", "Unknown Artist")
    track_name = metadata.get("track_name", "Unknown Track")

    # Construct the destination path
    destination_path = os.path.join(destination_dir, f"{artist_name}_{track_name}_{(seed_entry.get() + pattern_entry.get())}.wav")

    try:
        # Copy the composition to the user-defined location
        shutil.copy2(composition_path, destination_path)
        print(f"Composition saved to: {destination_path}")
    except Exception as e:
        print(f"Error saving composition: {e}")

    stop_composition()


save_composition_button = tk.Button(app, text="Save Composition", command=save_composition)
save_composition_button.pack()

app.mainloop()
