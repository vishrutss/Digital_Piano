import numpy as np
import sounddevice as sd

# https://muted.io/note-frequencies/
NOTE_FREQUENCIES = {
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00
}

SAMPLE_RATE = 44100
DURATION = 1

def generate_sine_wave(frequency):
    time = np.linspace(0, DURATION, SAMPLE_RATE, endpoint=False)
    sine_wave = np.sin(2*np.pi*frequency*time)
    out_sample=np.floor(sine_wave*32767).astype(np.int16)
    return out_sample

for freq in NOTE_FREQUENCIES.values():
    samples = generate_sine_wave(freq)
    sd.play(samples, SAMPLE_RATE)
    sd.wait()