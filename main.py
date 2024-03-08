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

def generate_echo(note_samples, decay=0.5):
    echo = note_samples
    num_echoes = 2
    for _ in range(num_echoes):
        note_samples = decay * note_samples
        echo = np.append(echo, note_samples)

    return echo

def pitch_shift(audio_data, pitch_factor):
    num_samples = len(audio_data)
    pitch_shifted = np.zeros(num_samples)
    for i in range(num_samples):
        new_sample_index = int(i * pitch_factor)
        if new_sample_index < num_samples:
            pitch_shifted[i] = audio_data[new_sample_index]
    return pitch_shifted

def play(effect, _value):
    playing_notes = set()
    running = True
    piano_notes = {}

    for key, frequency in NOTE_FREQUENCIES.items():
        if effect[0][0] == "Regular":
            piano_notes[key] = generate_piano_note(frequency)
        elif effect[0][0] == "Karplus Strong":
            piano_notes[key] = karplus_strong(frequency)
        elif effect[0][0] == "Reverb":
            piano_notes[key] = generate_reverb(generate_piano_note(frequency))
        elif effect[0][0] == "Echo":
            piano_notes[key] = generate_echo(generate_piano_note(frequency))
        elif effect[0][0] == "Pitch Shift":
            piano_notes[key] = pitch_shift(generate_piano_note(frequency), 0.5)

    play_window = pygame.display.set_mode((700, 500))
    play_window.fill((165,42,42))

    font = pygame.font.Font(None, 36)
    text = font.render("Selected effect: "+effect[0][0], True, (255, 255, 255))
    text_rect = text.get_rect(center = (play_window.get_width() // 2, 200))
    play_window.blit(text, text_rect)

    # https://medium.com/@01one/how-to-create-clickable-button-in-pygame-8dd608d17f1b
    btn_surface = pygame.Surface((150, 50))
    btn_text = font.render("Go back", True, (255, 255, 255))
    text_rect = btn_text.get_rect(center=(btn_surface.get_width() / 2, btn_surface.get_height() / 2))
    btn_rect = pygame.Rect(270, 300, 150, 50)
    btn_surface.blit(btn_text, text_rect)
    play_window.blit(btn_surface, (btn_rect.x, btn_rect.y))

    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    return
            elif event.type == pygame.KEYDOWN:  # https://www.pygame.org/docs/ref/key.html
                key = event.key
                if key in NOTE_FREQUENCIES:
                    playing_notes.add(key)
            elif event.type == pygame.QUIT:
                running = False

        if effect[0][0] == "Echo":
            combined_samples = np.zeros(int(DURATION * SAMPLE_RATE * 3))
        else:
            combined_samples = np.zeros(int(DURATION * SAMPLE_RATE))

        for key in playing_notes:
            combined_samples += piano_notes[key]

        sd.play(combined_samples, SAMPLE_RATE)
        sd.wait()

        playing_notes.clear()

if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode((700, 500))

    # https://pygame-menu.readthedocs.io/en/latest/
    menu = pygame_menu.Menu('Welcome', 600, 500,
                            theme=pygame_menu.themes.THEME_DARK)

    menu.add.dropselect("Effects", [('Regular', 1), ('Karplus Strong', 2), ('Reverb', 3), ('Echo', 4),
                                    ('Pitch Shift', 5)], onchange=play)

    menu.mainloop(window)

    pygame.quit()