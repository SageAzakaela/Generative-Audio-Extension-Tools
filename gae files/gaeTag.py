import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pygame

# Initialize pygame for audio playback
pygame.mixer.init()

# Global list to store full file paths
file_paths = []

# Function to play audio
def play_audio(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
# Function to rename and update the file list
def rename_and_refresh():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    selected_index = listbox.curselection()

    if selected_index:
        selected_index = selected_index[0]
        selected_file = file_paths[selected_index]
        selected_tag = tag_var.get()

        if selected_file:
            file_name, file_extension = os.path.splitext(selected_file)
            new_file_name = file_name + selected_tag + file_extension
            try:
                os.rename(selected_file, new_file_name)
            except OSError as e:
                messagebox.showerror("Error", f"Error renaming the file: {e}")
            refresh_file_list()

# Function to refresh the file list
def refresh_file_list():
    listbox.delete(0, tk.END)
    file_paths.clear()
    selected_folder = folder_var.get()

    if selected_folder:
        for root, _, files in os.walk(selected_folder):
            for file in files:
                if file.endswith(".wav"):
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)
                    listbox.insert(tk.END, file)

# Create the main window
root = tk.Tk()
root.title("File Renamer and Tagger")

# Create and place widgets
folder_label = tk.Label(root, text="Select a folder:")
folder_label.pack()

folder_var = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=folder_var)
folder_entry.pack()

select_folder_button = tk.Button(root, text="Browse", command=lambda: folder_var.set(filedialog.askdirectory()))
select_folder_button.pack()

listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50)
listbox.pack()

listen_button = tk.Button(root, text="Listen to Audio", command=lambda: play_audio(file_paths[listbox.curselection()[0]]))
listen_button.pack()

tag_label = tk.Label(root, text="Select a Tag:")
tag_label.pack()

tag_var = tk.StringVar()
tag_dropdown = tk.OptionMenu(root, tag_var, "_A", "_B", "_C", "_D", "_Intro", "_Outro", "_Repeat", "_Mute")
tag_dropdown.pack()

rename_button = tk.Button(root, text="Append Tag and Rename", command=rename_and_refresh)
rename_button.pack()

refresh_button = tk.Button(root, text="Refresh File List", command=refresh_file_list)
refresh_button.pack()

# Start the GUI
root.mainloop()
