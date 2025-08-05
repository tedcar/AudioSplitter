import os
import sys
import subprocess
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment
from pydub.utils import mediainfo
import threading
import time

# Constants
duration_limit = 14 * 60  # 14 minutes in seconds

# Format mappings for FFmpeg
FORMAT_MAPPING = {
    '.m4a': 'mp4',  # M4A uses MP4 container
    '.ogg': 'ogg',
    '.mp3': 'mp3',
    '.wav': 'wav',
    '.flac': 'flac',
    '.aac': 'aac',
    '.wma': 'asf',
    '.opus': 'opus'
}

# Codec mappings for lossless copy
CODEC_MAPPING = {
    '.m4a': 'aac',
    '.mp3': 'mp3',
    '.ogg': 'libvorbis',
    '.wav': 'pcm_s16le',
    '.flac': 'flac',
    '.opus': 'libopus'
}

# Initialize GUI
class AudioSplitterApp:
    def __init__(self, master):
        self.master = master
        master.title("Audio Splitter")

        self.label = tk.Label(master, text="Select an audio file to split and set duration (minutes):")
        self.label.pack()

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        self.duration_label = tk.Label(master, text="Max Duration per Split (minutes):")
        self.duration_label.pack()

        self.duration_var = tk.StringVar(value="14")
        self.duration_entry = tk.Entry(master, textvariable=self.duration_var)
        self.duration_entry.pack()

        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Audio Files", "*.mp3;*.wav;*.flac;*.ogg;*.m4a")])
        if file_path:
            def run_splitting():
                try:
                    max_duration = int(self.duration_var.get()) * 60
                    self.progress['maximum'] = 100
                    split_audio_file(file_path, max_duration, self.progress)
                    messagebox.showinfo("Success", "Splitting complete!")
                    os.startfile(os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + "_splits"))
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            threading.Thread(target=run_splitting).start()

# Main logic
def split_audio_file(file_path, duration_limit, progress=None):
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
    output_dir = os.path.join(os.path.dirname(file_path), file_name + "_splits")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get audio duration
    info = mediainfo(file_path)
    duration = float(info['duration'])

    # Calculate segments
    num_segments = math.ceil(duration / duration_limit)

    for i in range(num_segments):
        start = i * duration_limit
        end = min((i + 1) * duration_limit, duration)
        
        output_file = os.path.join(output_dir, f"{file_name}_{i+1:03d}{file_ext}")

        ffmpeg_args = [
            'ffmpeg', '-y', '-i', file_path,
            '-ss', str(start), '-to', str(end),
            '-c', 'copy', '-copyts', output_file
        ]

        subprocess.run(ffmpeg_args, check=True, capture_output=True)
        
        if progress:
            progress['value'] = (i + 1) * 100 / num_segments
            progress.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitterApp(root)
    root.mainloop()
