from pydub import AudioSegment
from pydub.generators import Sine

# Generate a 1-second test tone
tone = Sine(440).to_audio_segment(duration=1000)  # 440 Hz for 1 second

# Export to test file
tone.export("test_tone.mp3", format="mp3")
print("Test tone generated successfully!")
