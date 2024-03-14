import numpy as np
import sounddevice as sd
import pygame
import pygame_menu

# https://muted.io/note-frequencies/
# Dictionary of note frequencies for each key
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
    """
    Function to generate a note using the Karplus-Strong algorithm.
    :param note_frequency: The frequency of the note to be generated.
    :return: A numpy array representing the audio data of the modified note.
    """
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

def generate_piano_note(note_frequency):
    """
    Function to generate a piano note.
    :param note_frequency: The frequency of the note to be generated.
    :return: A numpy array representing the audio data of the note.
    """
    time = np.linspace(0, DURATION, SAMPLE_RATE, endpoint=False)
    frequencies = [note_frequency, note_frequency * 1.5, note_frequency * 0.5]
    sine_waves = [np.sin(2*np.pi*f*time) for f in frequencies]
    combined_wave = np.sum(sine_waves, axis=0)

    attack_time = 0.01
    decay_time = 0.01
    release_time = 0.5
    sustain_level = 0.2

    # https://en.wikipedia.org/wiki/Envelope_(music)
    envelope = np.concatenate([
        np.linspace(0, 0.5, int(attack_time * SAMPLE_RATE), endpoint=False),
        np.linspace(0.5, sustain_level, int(decay_time * SAMPLE_RATE), endpoint=False),
        np.full(int((DURATION - attack_time - decay_time - release_time) * SAMPLE_RATE), sustain_level),
        np.linspace(sustain_level, 0, int(release_time * SAMPLE_RATE), endpoint=False)
    ])

    piano_note = combined_wave * envelope
    return piano_note


# https://github.com/pdx-cs-sound/effects/blob/master/reverb.py
def generate_reverb(audio_array, delay_ms=50.0, wet_fraction=0.5, reverb_fraction=0.8):
    """
    Function to generate a reverb effect.
    :param audio_array: The original audio data.
    :param delay_ms: The delay for the reverb in milliseconds.
    :param wet_fraction: The fraction of the reverb signal in the output.
    :param reverb_fraction: The fraction of the reverb signal fed back into the buffer.
    :return: A list representing the audio data with the reverb effect.
    """
    delay = int(delay_ms * 0.001 * SAMPLE_RATE)
    buffer = [0] * delay
    head, tail = 0, 0

    out_signal = []

    for i, sample in enumerate(audio_array):
        if i < delay:
            delayed_sample = 0
        else:
            delayed_sample = buffer[head]
            head = (head + 1) % delay

        out_signal.append((1 - wet_fraction) * sample + wet_fraction * delayed_sample)
        buffer[tail] = (1 - reverb_fraction) * sample + reverb_fraction * delayed_sample
        tail = (tail + 1) % delay

    return out_signal

def generate_echo(audio_array, decay=0.5):
    """
    Function to generate an echo effect.
    :param audio_array: The original audio data.
    :param decay: The decay factor for the echo.
    :return: A numpy array representing the audio data with the echo effect.
    """
    echo = audio_array
    num_echoes = 2
    for _ in range(num_echoes):
        audio_array = decay * audio_array
        echo = np.append(echo, audio_array)

    return echo

def pitch_shift(audio_array, pitch_factor):
    """
    Function to shift the pitch of the audio data.
    :param audio_array: The original audio data.
    :param pitch_factor: The factor by which to shift the pitch.
    :return: A numpy array representing the audio data with the pitch shifted.
    """
    num_samples = len(audio_array)
    pitch_shifted = np.zeros(num_samples)
    for i in range(num_samples):
        new_sample_index = int(i * pitch_factor)
        if new_sample_index < num_samples:
            pitch_shifted[i] = audio_array[new_sample_index]
    return pitch_shifted

def play(effect, _value):
    """
    Function to play the notes with the selected effect.
    :param effect: The selected effect.
    :param _value: Unused parameter received from dropselect function of pygame_menu.
    """
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
        elif effect[0][0] == "Pitch Shift (Low)":
            piano_notes[key] = pitch_shift(generate_piano_note(frequency), 0.5)
        elif effect[0][0] == "Pitch Shift (High)":
            piano_notes[key] = pitch_shift(generate_piano_note(frequency), 1.8)

    play_window = pygame.display.set_mode((700, 500))
    play_window.fill((165,42,42))

    font = pygame.font.Font(None, 36)
    text = font.render("Selected effect: "+effect[0][0], True, (255, 255, 255))
    info_text = font.render("Press keys A-K to play the piano notes", True, (255, 255, 255))
    text_rect = text.get_rect(center = (play_window.get_width() // 2, 200))
    info_text_rect = info_text.get_rect(center = (play_window.get_width() // 2, 250))
    play_window.blit(text, text_rect)
    play_window.blit(info_text, info_text_rect)

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
                                    ('Pitch Shift (Low)', 5), ('Pitch Shift (High)', 6)], onchange=play)

    menu.mainloop(window)

    pygame.quit()