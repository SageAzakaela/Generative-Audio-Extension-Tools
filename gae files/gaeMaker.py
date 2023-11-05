import tkinter as tk
from tkinter import filedialog
import os
import shutil
import zipfile
from PIL import Image

# Function to open a file dialog for a layer
def browse_layer_path(layer_num):
    path = filedialog.askdirectory()
    if path:
        layer_paths[layer_num].set(path)
        layer_path_labels[layer_num].config(text=f"Layer {layer_num}: {path}")

# Function to open a file dialog to browse for cover art (PNG) file
def browse_cover_art():
    cover_art_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if cover_art_path:
        cover_art_entry.delete(0, tk.END)
        cover_art_entry.insert(0, cover_art_path)

# Function to create the .gae file
def create_gae_file():
    name = file_name_entry.get()
    duration = int(duration_entry.get())
    bpm = bpm_entry.get()
    key = key_entry.get()
    artist = artist_entry.get()
    track_name = track_name_entry.get()

    # Create a directory for the .gae file
    directory = os.path.join(os.getcwd(), name)
    os.makedirs(directory)

    num_layers = 0  # Count the number of valid layers
    for layer_num, path in enumerate(layer_paths):
        if path.get():
            num_layers += 1
            layer_name = f"L{layer_num}_{os.path.basename(path.get())}"
            shutil.copytree(path.get(), os.path.join(directory, layer_name))
            loaded_files_labels[layer_num].config(text=f"Loaded: {layer_name}")
            loaded_files_labels[layer_num].pack()

    # Create the settings file
    settings = {
        "duration": duration,
        "bpm": bpm,
        "key": key,
        "artist": artist,
        "track_name": track_name,
    }
    with open(os.path.join(directory, "settings.txt"), "w") as settings_file:
        for key, value in settings.items():
            settings_file.write(f"{key}: {value}\n")

    # Include cover art in the .gae directory
    cover_art_path = cover_art_entry.get()
    if cover_art_path:
        cover_art_filename = "cover_art.png"  # Change the filename as needed
        cover_art_dest_path = os.path.join(directory, cover_art_filename)
        shutil.copy(cover_art_path, cover_art_dest_path)

    # Create the .gae file by zipping the directory without compression
    with zipfile.ZipFile(f"{name}.gae", 'w', zipfile.ZIP_STORED) as gae_zip:
        for root, _, files in os.walk(directory):
            for file in files:
                gae_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))

    # Clean up the temporary directory
    shutil.rmtree(directory)

    # Clear loaded files labels for layers without valid paths
    for i in range(num_layers, len(layer_paths)):
        loaded_files_labels[i].config(text="")

# Create the main application window
app = tk.Tk()
app.title("GAE File Creator")

# Create and place input fields, labels, and browse buttons
file_name_label = tk.Label(app, text="File Name:")
file_name_label.pack()
file_name_entry = tk.Entry(app)
file_name_entry.pack()

layer_paths = []
layer_path_labels = []
browse_buttons = []
loaded_files_labels = []

# Maximum number of layers (1 to 10)
max_layers = 10

for i in range(max_layers):
    layer_path = tk.StringVar()
    layer_paths.append(layer_path)
    layer_path_label = tk.Label(app, text=f"Layer {i} Path:")
    layer_path_label.pack()
    layer_path_labels.append(layer_path_label)

    # Add a "Browse" button for each layer
    browse_button = tk.Button(app, text="Browse", command=lambda i=i: browse_layer_path(i))
    browse_button.pack()
    browse_buttons.append(browse_button)

    # Label to display the loaded file for each layer
    loaded_files_label = tk.Label(app, text="")
    loaded_files_labels.append(loaded_files_label)

duration_label = tk.Label(app, text="Duration (bars):")
duration_label.pack()
duration_entry = tk.Entry(app)
duration_entry.pack()

bpm_label = tk.Label(app, text="BPM:")
bpm_label.pack()
bpm_entry = tk.Entry(app)
bpm_entry.pack()

key_label = tk.Label(app, text="Key:")
key_label.pack()
key_entry = tk.Entry(app)
key_entry.pack()

artist_label = tk.Label(app, text="Artist:")
artist_label.pack()
artist_entry = tk.Entry(app)
artist_entry.pack()

track_name_label = tk.Label(app, text="Track Name:")
track_name_label.pack()
track_name_entry = tk.Entry(app)
track_name_entry.pack()

cover_art_label = tk.Label(app, text="Select Cover Art (PNG):")
cover_art_label.pack()
cover_art_entry = tk.Entry(app)
cover_art_entry.pack()

cover_art_browse_button = tk.Button(app, text="Browse", command=browse_cover_art)
cover_art_browse_button.pack()

create_button = tk.Button(app, text="Create .gae File", command=create_gae_file)
create_button.pack()

app.mainloop()
