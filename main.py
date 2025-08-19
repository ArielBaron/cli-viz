import sys
import os
import numpy as np
import pyaudio
import curses
import time

from visualizers.bars import BarsVisualizer

# --- Suppress ALSA warnings ---
sys.stderr = open(os.devnull, 'w')

class TerminalAudioVisualizer:
    def __init__(self):
        # Audio setup
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.pause = False

        self.spectrum = np.zeros(self.CHUNK)
        self.smoothed_spectrum = np.zeros(self.CHUNK // 2)
        self.previous_spectrum = np.zeros(self.CHUNK // 2)
        self.smoothing = 0.8
        self.energy = 0

        self.sensitivity = 1.0
        self.sensitivity_step = 0.1

        # Use only BarsVisualizer
        self.visualizer = BarsVisualizer()

        # Initialize audio stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK
        )

    def get_audio_data(self):
        data = np.frombuffer(self.stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.int16)
        spectrum = np.abs(np.fft.fft(data)[:self.CHUNK // 2])
        spectrum = spectrum / (128 * self.CHUNK)
        self.previous_spectrum = self.smoothed_spectrum
        self.smoothed_spectrum = self.previous_spectrum * self.smoothing + spectrum * (1 - self.smoothing)
        adjusted_spectrum = self.smoothed_spectrum * self.sensitivity
        self.energy = np.mean(adjusted_spectrum[:self.CHUNK//4]) * 2
        return adjusted_spectrum

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.timeout(0)
        stdscr.erase()

        try:
            while True:
                try:
                    key = stdscr.getkey()
                    if key == 'q':
                        break
                    elif key == ' ':
                        self.pause = not self.pause
                    elif key in ('+', '='):
                        self.sensitivity += self.sensitivity_step
                    elif key == '-':
                        self.sensitivity = max(0.1, self.sensitivity - self.sensitivity_step)
                    else:
                        self.visualizer.handle_keypress(key)
                except:
                    pass

                if not self.pause:
                    height, width = stdscr.getmaxyx()
                    spectrum = self.get_audio_data()
                    stdscr.erase()
                    stdscr.addstr(0, 0, f"YTMCLI Visualizer | Spectrum Bars | Sensitivity: {self.sensitivity:.1f} | [Q] Quit | [+/-] Sensitivity | [Space] Pause")
                    self.visualizer.draw(stdscr, spectrum, height, width, self.energy, 0)
                    stdscr.refresh()
                    time.sleep(0.016)
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

if __name__ == "__main__":
    visualizer = TerminalAudioVisualizer()
    curses.wrapper(visualizer.run)
