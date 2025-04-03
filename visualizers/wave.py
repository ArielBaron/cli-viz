# visualizers/wave.py
import curses
import math
import time
from visualizer_base import VisualizerBase

class WaveVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Wave")
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Sinusoidal wave visualization
        mid_y = height // 2
        samples = width
        
        wave = [0] * samples
        for i in range(min(20, len(spectrum))):
            # Add sine waves with amplitudes from spectrum
            freq = (i + 1) * 2
            amp = spectrum[i] * 10 * (height / 4)
            phase = time.time() * (i + 1) * 1.5
            
            # Generate sine wave
            for x in range(samples):
                wave[x] += amp * math.sin(2 * math.pi * freq * x / samples + phase)
        
        # Draw wave
        for x in range(samples):
            if x < width:
                y = int(mid_y + wave[x])
                if 0 <= y < height - 1:
                    # Calculate color based on amplitude and position
                    hue = (x / width + hue_offset) % 1.0
                    sat = 0.8 + 0.2 * (abs(wave[x]) / (height / 4) if height > 0 else 0)
                    val = 0.7 + 0.3 * (abs(wave[x]) / (height / 4) if height > 0 else 0)
                    
                    # Get color pair and draw
                    color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                    stdscr.addstr(y, x, "•", color_attr | curses.A_BOLD)