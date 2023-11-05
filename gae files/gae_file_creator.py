import tkinter as tk
from tkinter import filedialog
import os
import shutil
import zipfile

# Function to open a file dialog for a layer
def browse_layer_path(layer_num):
    path = filedialog.askdirectory()
    if path:
        layer_paths[layer_num].set(path)

# Function to create the .gae file
def create_gae_file():
    name = file_name_entry.get()
    bars = int(bars_entry.get())

    # Create a directory for the .gae file
    directory = os.path.join(os.getcwd(), name)
    os.makedirs(directory)

    for layer_num, path in enumerate(layer_paths):
        if path.get():
            layer_name = f"L{layer_num}_{os.path.basename(path.get())}"
            shutil.copytree(path.get(), os.path.join(directory, layer_name))

    # Create the settings file
    settings = {
        "bars": bars
    }
    with open(os.path.join(directory, "settings.txt"), "w") as settings_file:
        for key, value in settings.items():
            settings_file.write(f"{key}: {value}\n")

    # Create the .gae file by zipping the directory without compression
    with zipfile.ZipFile(f"{name}.gae", 'w', zipfile.ZIP_STORED) as gae_zip:
        for root, _, files in os.walk(directory):
            for file in files:
                gae_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))

    # Clean up the temporary directory
    shutil.rmtree(directory)
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
for i in range(5): # Change Number Here to change the number of layers within .gae!
    layer_path = tk.StringVar()
    layer_paths.append(layer_path)
    layer_path_label = tk.Label(app, text=f"Layer {i} Path:")
    layer_path_label.pack()
    layer_path_labels.append(layer_path_label)
    
    # Add a "Browse" button for each layer
    browse_button = tk.Button(app, text="Browse", command=lambda i=i: browse_layer_path(i))
    browse_button.pack()
    browse_buttons.append(browse_button)

bars_label = tk.Label(app, text="Number of Bars:")
bars_label.pack()
bars_entry = tk.Entry(app)
bars_entry.pack()

create_button = tk.Button(app, text="Create .gae File", command=create_gae_file)
create_button.pack()

app.mainloop()
