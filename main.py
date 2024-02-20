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

def generate_sine_wave(frequency):
    time = np.linspace(0, DURATION, SAMPLE_RATE, endpoint=False)
    sine_wave = np.sin(2*np.pi*frequency*time)
    out_sample=np.floor(sine_wave*32767).astype(np.int16)
    return out_sample

pygame.init()
pygame.display.set_mode((100, 100))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:  # https://www.pygame.org/docs/ref/key.html
            key = event.key
            if key in NOTE_FREQUENCIES:
                freq = NOTE_FREQUENCIES[key]
                samples = generate_sine_wave(freq)
                sd.play(samples, SAMPLE_RATE)
        elif event.type == pygame.QUIT:
            running = False

pygame.quit()