# Digital Piano
## Submitted by: Vishrut Sharma

## Note:
Please install the following libraries before running main.py
```
pip install sounddevice
pip install scipy
pip install pygame
pip install pygame-menu -U
```

## Description:
This project is a Digital Piano application that simulates the notes of a Piano. It has 8 keys which are mapped to the notes in the
A4 minor scale of a Piano. By pressing keys from A-K the corresponding notes will be played:

* A - A4
* S - B4
* D - C4
* F - D4
* G - E4
* H - F4
* J - G4
* K - A5

The user can also combine notes by pressing multiple keys at once.

The application provides the following modes that the user can change to:

* Regular Piano: The user can play the notes without any effects.
* Karplus-Strong: The user can play the notes with the Karplus-Strong algorithm which simulates the sound of a guitar.
* Reverb: The user can play the notes with a reverb effect.
* Echo: The user can play the notes with an echo effect.
* Pitch Shift (Low): The user can play the notes with a low pitch shift effect.
* Pitch Shift (High): The user can play the notes with a high-pitch shift effect.

The piano notes are generated by first getting the frequency from the key press by the user and then generating 1 sine
wave with the given frequency and 2 others which are 1.5 times and 0.5 times the provided frequency respectively.
Then all 3 waves are combined and the ADSR (Attack, Decay, Sustain, Release) envelope is applied to it. Bart's 
suggestion for the project proposal gave me the idea to combine 3 sine waves with 3 different but close to each other 
frequencies to make the sound more realistic. It still doesn't sound exactly like a piano but more like a keyboard.

I also implemented the Karplus-Strong algorithm as an effect as Bart suggested in the response to the project proposal.

The application also saves the played notes in a wav file called `output.wav`. But if the effect is changed the `output_sample`
array gets reset and the played notes of the previous effect will get overwritten. Notes of a single effect can be saved in the wav file.

## Challenges:

I had some issues with the Reverb effect in the beginning and couldn't get the reverb correct and the sound produced 
would just be too loud, so I decided to take a look at the class repository and implemented the reverb effect using the 
code from the repository and the effect improved significantly.

One issue that persists is the delay between the key press and the sound produced. I tried to reduce the latency slightly
by creating an audio array for each key beforehand for all the effects but the latency still exists. The delay is awful
for the echo effect.

Another thing I would have liked to improve is that right now when a note is played it cannot be interrupted until the 
ADSR envelope is complete and if another note is played while a note is currently playing it combines both notes. 
It would have been a difficult task to be able to interrupt notes on keypress, but it would have made the application more
realistic.

## Here is an example of the application running:

**Note:** I used a free video recording software that did not allow the computer audio to be recorded so the sounds produced
by the application are from my laptop speaker which caused the sounds to not come across very well in this video. (Apologies🙇)

https://github.com/vishrutss/Digital_Piano/assets/104886007/418d144a-59a1-49bd-a5f7-da5db63181a0

Another cool thing I just wanted to share. This is a screenshot of the notes G4 and A5 and it's really interesting to see
the ADSR envelope in action.

![image](https://github.com/vishrutss/Digital_Piano/assets/104886007/8a7db7bc-6075-4b82-9cc7-0e0ba45a30f4)


## Testing:
* For `karplus_strong` and `generate_piano_note`, I tested that the functions return an array of length equal to the sample
rate times the duration of the note.  
* For `generate_reverb`, `generate_echo`, and `pitch_shift`, I tested that the functions return an array equal to the length
of the input array.

All the tests are present in the `test.py` file.

## Sources:
* Frequencies for each note: https://muted.io/note-frequencies/
* Karplus-Strong implementation: https://www.math.drexel.edu/~dp399/musicmath/Karplus-Strong.html
* ADSR envelope: https://en.wikipedia.org/wiki/Envelope_(music)
* Reverb implementation: https://github.com/pdx-cs-sound/effects/blob/master/reverb.py
* PyGame UI (buttons): https://medium.com/@01one/how-to-create-clickable-button-in-pygame-8dd608d17f1b
* PyGame UI: https://www.pygame.org/docs/ref/key.html
* PyGame-Menu: https://pygame-menu.readthedocs.io/en/latest/
