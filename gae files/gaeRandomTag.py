import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import random


# Global list to store full file paths
file_paths = []

# Variables to track if "_I" and "_O" tags have been used
_i_used = False
_o_used = False



# Function to rename and update the file list
def rename_and_refresh():

    selected_folder = folder_var.get()

    if selected_folder:
        # Clear the existing file_paths list
        file_paths.clear()

        # Reset the "_I" and "_O" used flags
        global _i_used, _o_used
        _i_used = False
        _o_used = False

        for root, _, files in os.walk(selected_folder):
            for file in files:
                if file.endswith(".wav"):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)

                    file_name, file_extension = os.path.splitext(file_path)

                    # Randomly choose between "_I" and "_O" (only once)
                    if not _i_used and not _o_used:
                        selected_tag = random.choice(["_I", "_O"])
                        if selected_tag == "_I":
                            _i_used = True
                        else:
                            _o_used = True
                    else:
                     #    Randomly choose between "_A", "_B", "_C", "_D"
                        selected_tag = random.choice(["_A", "_B", "_C", "_D"])

                      #   Randomly append "_R" (1/10 chance for "_R")
                    if random.randint(1, 10) == 1:
                        selected_tag += "_R"

                    new_file_name = file_name + selected_tag + file_extension
                    try:
                        os.rename(file_path, new_file_name)
                    except OSError as e:
                        messagebox.showerror("Error", f"Error renaming the file: {e}")

        refresh_file_list()

# Function to refresh the file list
def refresh_file_list():
    listbox.delete(0, tk.END)
    for file_path in file_paths:
        listbox.insert(tk.END, os.path.basename(file_path))

# Function to clear file_paths and reset flags when selecting a new folder
def clear_and_reset():
    global _i_used, _o_used
    _i_used = False
    _o_used = False
    file_paths.clear()

# Create the main window
root = tk.Tk()
root.title("Gae Random Tagger")

# Create and place widgets
folder_label = tk.Label(root, text="Select a folder:")
folder_label.pack()

folder_var = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=folder_var)
folder_entry.pack()

select_folder_button = tk.Button(root, text="Browse", command=lambda: [clear_and_reset(), folder_var.set(filedialog.askdirectory()), rename_and_refresh()])
select_folder_button.pack()

listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50)
listbox.pack()


# Start the GUI
root.mainloop()
