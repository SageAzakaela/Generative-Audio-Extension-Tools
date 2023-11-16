import tkinter as tk
from tkinter import filedialog
import os
import shutil
import zipfile

def browse_layer_path(layer_num):
    path = filedialog.askdirectory()
    if path:
        layer_paths[layer_num].set(path)
        layer_path_labels[layer_num].config(text=f"Layer {layer_num}: {path}")

def browse_cover_art():
    cover_art_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if cover_art_path:
        cover_art_entry.delete(0, tk.END)
        cover_art_entry.insert(0, cover_art_path)

def create_gae_file():
    name = file_name_entry.get()
    duration = int(duration_entry.get())
    bpm = bpm_entry.get()
    key = key_entry.get()
    artist = artist_entry.get()
    track_name = track_name_entry.get()

    directory = os.path.join(os.getcwd(), name)
    os.makedirs(directory)

    num_layers = 0
    for layer_num, path in enumerate(layer_paths):
        if path.get():
            num_layers += 1
            layer_name = f"L{layer_num}_{os.path.basename(path.get())}"
            shutil.copytree(path.get(), os.path.join(directory, layer_name))
            loaded_files_labels[layer_num].config(text=f"Loaded: {layer_name}")

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

    cover_art_path = cover_art_entry.get()
    if cover_art_path:
        cover_art_filename = "cover_art.png"
        cover_art_dest_path = os.path.join(directory, cover_art_filename)
        shutil.copy(cover_art_path, cover_art_dest_path)

    with zipfile.ZipFile(f"{name}.gae", 'w', zipfile.ZIP_STORED) as gae_zip:
        for root, _, files in os.walk(directory):
            for file in files:
                gae_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))

    shutil.rmtree(directory)

    for i in range(num_layers, len(layer_paths)):
        loaded_files_labels[i].config(text="")

app = tk.Tk()
app.title("GAE File Creator")

# Create a canvas with a vertical scrollbar
canvas = tk.Canvas(app)
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor='nw')

# Elements go inside the frame
file_name_label = tk.Label(frame, text="File Name:")
file_name_label.grid(row=0, column=0, sticky="w")
file_name_entry = tk.Entry(frame)
file_name_entry.grid(row=0, column=1, sticky="w")

layer_paths = []
layer_path_labels = []
loaded_files_labels = []  # Define loaded_files_labels here

max_layers = 18

for i in range(max_layers):
    layer_path = tk.StringVar()
    layer_paths.append(layer_path)
    layer_path_label = tk.Label(frame, text=f"Layer {i} Path:")
    layer_path_label.grid(row=i + 1, column=0, sticky="w")
    layer_path_labels.append(layer_path_label)

    browse_button = tk.Button(frame, text="Browse", command=lambda i=i: browse_layer_path(i))
    browse_button.grid(row=i + 1, column=1, sticky="w")

    # Label to display the loaded file for each layer
    loaded_files_label = tk.Label(frame, text="")
    loaded_files_labels.append(loaded_files_label)
    loaded_files_label.grid(row=i + 1, column=2, sticky="w")

duration_label = tk.Label(frame, text="Duration (bars):")
duration_label.grid(row=max_layers + 1, column=0, sticky="w")
duration_entry = tk.Entry(frame)
duration_entry.grid(row=max_layers + 1, column=1, sticky="w")

bpm_label = tk.Label(frame, text="BPM:")
bpm_label.grid(row=max_layers + 2, column=0, sticky="w")
bpm_entry = tk.Entry(frame)
bpm_entry.grid(row=max_layers + 2, column=1, sticky="w")

key_label = tk.Label(frame, text="Key:")
key_label.grid(row=max_layers + 3, column=0, sticky="w")
key_entry = tk.Entry(frame)
key_entry.grid(row=max_layers + 3, column=1, sticky="w")

artist_label = tk.Label(frame, text="Artist:")
artist_label.grid(row=max_layers + 4, column=0, sticky="w")
artist_entry = tk.Entry(frame)
artist_entry.grid(row=max_layers + 4, column=1, sticky="w")

track_name_label = tk.Label(frame, text="Track Name:")
track_name_label.grid(row=max_layers + 5, column=0, sticky="w")
track_name_entry = tk.Entry(frame)
track_name_entry.grid(row=max_layers + 5, column=1, sticky="w")

cover_art_label = tk.Label(frame, text="Select Cover Art (PNG):")
cover_art_label.grid(row=max_layers + 6, column=0, sticky="w")
cover_art_entry = tk.Entry(frame)
cover_art_entry.grid(row=max_layers + 6, column=1, sticky="w")

cover_art_browse_button = tk.Button(frame, text="Browse", command=browse_cover_art)
cover_art_browse_button.grid(row=max_layers + 7, column=0, columnspan=2, sticky="w")

# Add vertical scrollbar to the canvas
scrollbar = tk.Scrollbar(app, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

# Configure the canvas to scroll properly
frame.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the canvas to the scrollbar
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Add a button to create .gae file
create_button = tk.Button(app, text="Create .gae File", command=create_gae_file)
create_button.pack()

app.mainloop()
