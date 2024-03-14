import unittest
import numpy as np
from main import karplus_strong, generate_piano_note, generate_reverb, generate_echo, pitch_shift

SAMPLE_RATE = 44100
DURATION = 0.9

class TestMain(unittest.TestCase):
    def test_karplus_strong(self):
        result = karplus_strong(440.00)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), SAMPLE_RATE * DURATION)

    def test_generate_piano_note(self):
        result = generate_piano_note(440.00)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), SAMPLE_RATE * DURATION)

    def test_generate_reverb(self):
        audio_array = generate_piano_note(440.00)
        result = generate_reverb(audio_array)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(audio_array))

    def test_generate_echo(self):
        audio_array = generate_piano_note(440.00)
        result = generate_echo(audio_array)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), len(audio_array) * 3)

    def test_pitch_shift(self):
        audio_array = generate_piano_note(440.00)
        result = pitch_shift(audio_array, 0.5)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), len(audio_array))

if __name__ == '__main__':
    unittest.main()