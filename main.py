import numpy as np
import sounddevice as sd
import pygame
import pygame_menu

# https://muted.io/note-frequencies/
NOTE_FREQUENCIES = {
    pygame.K_a: 440.00, # A4
    pygame.K_s: 493.88, # B4
    pygame.K_d: 523.25, # C4
    pygame.K_f: 587.33, # D4
    pygame.K_g: 659.25, # E4
    pygame.K_h: 698.46, # F4
    pygame.K_j: 783.99, # G4
    pygame.K_k: 880.00  # A5
}

SAMPLE_RATE = 44100
DURATION = 1

# https://www.math.drexel.edu/~dp399/musicmath/Karplus-Strong.html
def karplus_strong(note_frequency):
    length = int(SAMPLE_RATE / note_frequency)
    signal = np.random.uniform(-1, 1, length)
    new_samples = []
    current_sample = 0
    previous_value = 0

    while len(new_samples) < int(DURATION * SAMPLE_RATE):
        signal[current_sample] = 0.5 * (signal[current_sample] + previous_value)
        new_samples.append(signal[current_sample])
        previous_value = new_samples[-1]
        current_sample += 1
        current_sample = current_sample % signal.size
    return np.array(new_samples)

def generate_piano_note(freq):
    time = np.linspace(0, DURATION, SAMPLE_RATE, endpoint=False)
    frequencies = [freq, freq * 1.5, freq * 0.5]
    sine_waves = [np.sin(2*np.pi*f*time) for f in frequencies]
    combined_wave = np.sum(sine_waves, axis=0)

    attack_time = 0.01
    decay_time = 0.01
    release_time = 0.6
    sustain_level = 0.2

    # https://en.wikipedia.org/wiki/Envelope_(music)
    envelope = np.concatenate([
        np.linspace(0, 1, int(attack_time * SAMPLE_RATE), endpoint=False),
        np.linspace(1, sustain_level, int(decay_time * SAMPLE_RATE), endpoint=False),
        np.full(int((DURATION - attack_time - decay_time - release_time) * SAMPLE_RATE), sustain_level),
        np.linspace(sustain_level, 0, int(release_time * SAMPLE_RATE), endpoint=False)
    ])

    piano_note = combined_wave * envelope
    return piano_note

def generate_reverb(note_samples, reverb_gain=0.7, feedback=0.8):
    num_samples = len(note_samples)
    reverb_buffer = np.zeros(SAMPLE_RATE)
    reverb = np.zeros(num_samples)

    for i in range(num_samples):
        reverb_buffer[:-1] = reverb_buffer[1:]
        reverb_buffer[-1] = note_samples[i] + feedback * reverb_buffer[-1]
        reverb[i] = note_samples[i] + reverb_gain * reverb_buffer[-1]

    return reverb

def play():
    pygame.init()
    pygame.display.set_mode((600, 400))
    playing_notes = set()
    running = True
    piano_notes = {}

    for key, frequency in NOTE_FREQUENCIES.items():
        piano_notes[key] = generate_piano_note(frequency)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:  # https://www.pygame.org/docs/ref/key.html
                key = event.key
                if key in NOTE_FREQUENCIES:
                    playing_notes.add(key)
            elif event.type == pygame.QUIT:
                running = False

        combined_samples = np.zeros(int(DURATION * SAMPLE_RATE))

        for key in playing_notes:
            combined_samples += piano_notes[key]

        sd.play(combined_samples, SAMPLE_RATE)
        sd.wait()

        playing_notes.clear()

if __name__ == '__main__':
    pygame.init()
    surface = pygame.display.set_mode((600, 400))

    # https://pygame-menu.readthedocs.io/en/latest/
    menu = pygame_menu.Menu('Welcome', 500, 400,
                            theme=pygame_menu.themes.THEME_DARK)

    menu.add.dropselect("Effects", [('Regular', 1), ('Karplus Strong', 2), ('Reverb', 3)])
    menu.add.button("Select", play)

    menu.mainloop(surface)

    pygame.quit()