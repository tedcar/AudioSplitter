import os
import sys
import subprocess
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import warnings

# Configure FFmpeg paths before importing pydub
if getattr(sys, 'frozen', False):
    # If running as compiled executable
    application_path = os.path.dirname(sys.executable)
    ffmpeg_path = os.path.join(application_path, 'ffmpeg', 'ffmpeg.exe')
    ffprobe_path = os.path.join(application_path, 'ffmpeg', 'ffprobe.exe')
else:
    # If running as Python script
    application_path = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(application_path, 'ffmpeg', 'ffmpeg.exe')
    ffprobe_path = os.path.join(application_path, 'ffmpeg', 'ffprobe.exe')

# Suppress FFmpeg warnings from pydub
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pydub import AudioSegment
    from pydub.utils import mediainfo
    
# Set FFmpeg paths for pydub
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Also set the paths in pydub.utils which mediainfo uses
from pydub import utils
utils.which = lambda x: ffmpeg_path if x == "ffmpeg" else ffprobe_path if x == "ffprobe" else None

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
            # Check if file exists
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return
                
            def run_splitting():
                try:
                    max_duration = int(self.duration_var.get()) * 60
                    self.progress['maximum'] = 100
                    split_audio_file(file_path, max_duration, self.progress)
                    messagebox.showinfo("Success", "Splitting complete!")
                    os.startfile(os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + "_splits"))
                except subprocess.CalledProcessError as e:
                    error_msg = f"FFmpeg error: {e}\n"
                    if e.stderr:
                        error_msg += f"Error output: {e.stderr.decode('utf-8', errors='ignore')}"
                    messagebox.showerror("Error", error_msg)
                except Exception as e:
                    import traceback
                    error_msg = f"Error: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
                    messagebox.showerror("Error", error_msg)

            threading.Thread(target=run_splitting).start()

# Main logic
def split_audio_file(file_path, duration_limit, progress=None):
    print(f"Starting to split file: {file_path}")
    print(f"FFmpeg path: {ffmpeg_path}")
    print(f"FFprobe path: {ffprobe_path}")
    
    # Check if FFmpeg executables exist
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"FFmpeg not found at: {ffmpeg_path}")
    if not os.path.exists(ffprobe_path):
        raise FileNotFoundError(f"FFprobe not found at: {ffprobe_path}")
    
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
    output_dir = os.path.join(os.path.dirname(file_path), file_name + "_splits")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get audio duration
    print(f"Getting media info for: {file_path}")
    try:
        info = mediainfo(file_path)
        duration = float(info['duration'])
        print(f"Duration: {duration} seconds")
    except Exception as e:
        print(f"Error getting media info: {e}")
        # Try alternative method using ffprobe directly
        ffprobe_args = [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(ffprobe_args, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFprobe failed: {result.stderr}")
        duration = float(result.stdout.strip())

    # Calculate segments
    num_segments = math.ceil(duration / duration_limit)

    for i in range(num_segments):
        start = i * duration_limit
        end = min((i + 1) * duration_limit, duration)
        
        output_file = os.path.join(output_dir, f"{file_name}_{i+1:03d}{file_ext}")

        ffmpeg_args = [
            ffmpeg_path, '-y', '-i', file_path,
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
