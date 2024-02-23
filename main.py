import numpy as np
import sounddevice as sd
import pygame

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

def generate_piano_note(frequency):
    time = np.linspace(0, DURATION, SAMPLE_RATE, endpoint=False)
    sine_wave = np.sin(2*np.pi*frequency*time)

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

    piano_note = sine_wave * envelope

    return piano_note

pygame.init()
pygame.display.set_mode((100, 100))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:  # https://www.pygame.org/docs/ref/key.html
            key = event.key
            if key in NOTE_FREQUENCIES:
                freq = NOTE_FREQUENCIES[key]
                samples = generate_piano_note(freq)
                sd.play(samples, SAMPLE_RATE)
        elif event.type == pygame.QUIT:
            running = False

pygame.quit()