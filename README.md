# AudioSplitter

A Python program that splits an audio file into multiple files with a length of no more than 14 minutes per file. The original file can be as long as possible.

## Features

- Split any audio file into 14-minute segments
- Progress bar visualization during processing
- Simple GUI interface for easy file selection
- Automatic output organization in the source directory
- Support for various audio formats (MP3, WAV, FLAC, etc.)

## Quick Start (For Users)

Download the latest release from the [Releases](https://github.com/tedcar/AudioSplitter/releases) page and run the executable. No installation required!

## Development Setup (For Technical Users)

### Prerequisites

- Python 3.11 or higher (64-bit)
- FFmpeg

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tedcar/AudioSplitter.git
cd AudioSplitter
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Unix/macOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install pydub tqdm pyinstaller
```

4. Download FFmpeg:
   - Download the static Windows build from [FFmpeg official site](https://ffmpeg.org/download.html)
   - Extract the contents to the `ffmpeg` folder in the project root
   - The `ffmpeg/bin` folder should contain `ffmpeg.exe`

### Usage

Run the application:
```bash
python audio_splitter.py
```

### Building the Executable

To create a standalone executable:
```bash
pyinstaller --onefile --windowed --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" --icon=icon.ico audio_splitter.py
```

## How It Works

1. Select an audio file using the file dialog
2. The program automatically creates an output directory in the same location as the source file
3. Audio is split into 14-minute segments (or less for the final segment)
4. Progress is displayed in real-time
5. Split files are saved with sequential numbering (e.g., `filename_001.mp3`, `filename_002.mp3`, etc.)

## Technical Details

- Built with Python using `pydub` for audio processing
- GUI interface using `tkinter`
- Progress tracking with `tqdm`
- Bundled with FFmpeg for maximum compatibility
