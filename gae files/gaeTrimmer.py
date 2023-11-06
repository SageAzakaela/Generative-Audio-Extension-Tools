import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
import os

def calculate_duration():
    bpm = float(bpm_entry.get())
    bars = int(bars_var.get())
    duration = (bars * 60000) / (bpm / beats_per_bar)
    result_label.config(text=f"Duration: {int(duration)} milliseconds")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def trim_audio():
    input_file = file_entry.get()
    bpm = float(bpm_entry.get())
    bars = int(bars_var.get())
    duration = int((bars * 60000) / (bpm / beats_per_bar))  # Convert to an integer
    output_folder = folder_entry.get()

    os.makedirs(output_folder, exist_ok=True)
    audio = AudioSegment.from_file(input_file)
    interval = duration  # milliseconds

    for start_time in range(0, len(audio), interval):
        end_time = start_time + interval
        if end_time > len(audio):
            end_time = len(audio)

        trimmed_audio = audio[start_time:end_time]
        output_file = os.path.join(output_folder, f"segment_{start_time}_{end_time}.wav")
        trimmed_audio.export(output_file, format="wav")

    result_label.config(text="Trimming complete")

beats_per_bar = 4

app = tk.Tk()
app.title("Loop Trimmer")

frame = tk.Frame(app)
frame.pack(padx=20, pady=20)

file_label = tk.Label(frame, text="Input Audio File:")
file_label.grid(row=0, column=0)
file_entry = tk.Entry(frame)
file_entry.grid(row=0, column=1)
browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2)

bpm_label = tk.Label(frame, text="BPM:")
bpm_label.grid(row=1, column=0)
bpm_entry = tk.Entry(frame)
bpm_entry.grid(row=1, column=1)

bars_label = tk.Label(frame, text="Bars:")
bars_label.grid(row=2, column=0)
bars_var = tk.StringVar(value="4")
bars_menu = tk.OptionMenu(frame, bars_var, "4", "8")
bars_menu.grid(row=2, column=1)

folder_label = tk.Label(frame, text="Output Folder:")
folder_label.grid(row=3, column=0)
folder_entry = tk.Entry(frame)
folder_entry.grid(row=3, column=1)

calculate_button = tk.Button(frame, text="Calculate Duration", command=calculate_duration)
calculate_button.grid(row=4, column=0, columnspan=2)

trim_button = tk.Button(frame, text="Trim Audio", command=trim_audio)
trim_button.grid(row=5, column=0, columnspan=2)

result_label = tk.Label(frame, text="")
result_label.grid(row=6, column=0, columnspan=2)

app.mainloop()
