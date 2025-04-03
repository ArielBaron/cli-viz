# visualizers/bars.py
import curses
from visualizer_base import VisualizerBase

class BarsVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Spectrum Bars")
        self.bars = 50  # Number of bars in visualization
        self.boost = 1.5  # Bass boost factor
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Classic spectrum analyzer with bars
        bar_width = max(1, width // self.bars)
        for i in range(min(self.bars, width // bar_width)):
            # Get frequency amplitude
            freq_index = int(i ** 1.3) + 1  # Non-linear mapping for better visualization
            freq_index = min(freq_index, len(spectrum) - 1)
            amplitude = spectrum[freq_index] * (1 + self.boost * (1 - i / self.bars))
            
            # Calculate bar height
            bar_height = int(amplitude * (height - 4) * 3)
            bar_height = min(bar_height, height - 4)
            
            # Draw bar with color gradient
            for j in range(bar_height):
                # Calculate color (HSV: hue based on frequency, saturation and value based on amplitude)
                hue = (i / self.bars + hue_offset) % 1.0
                sat = 0.8 + 0.2 * (j / bar_height if bar_height > 0 else 0)
                val = 0.7 + 0.3 * (j / bar_height if bar_height > 0 else 0)
                
                # Get color pair and draw
                color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                stdscr.addstr(height - 3 - j, i * bar_width, "█" * bar_width, color_attr | curses.A_BOLD)
    
    def handle_keypress(self, key):
        if key == 'b':
            self.boost = max(0.5, min(5.0, self.boost + 0.1))
            return True
        elif key == 'B':
            self.boost = max(0.5, min(5.0, self.boost - 0.1))
            return True
        return False