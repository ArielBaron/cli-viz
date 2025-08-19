from visualizer_base import VisualizerBase
import curses

class BarsVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Spectrum Bars")
        self.bars = 50
        self.boost = 1.5

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        bar_width = max(1, width // self.bars)
        for i in range(min(self.bars, width // bar_width)):
            freq_index = int(i ** 1.3) + 1
            freq_index = min(freq_index, len(spectrum) - 1)
            amplitude = spectrum[freq_index] * (1 + self.boost * (1 - i / self.bars))

            bar_height = int(amplitude * (height - 4) * 3)
            bar_height = min(bar_height, height - 4)

            for j in range(bar_height):
                stdscr.addstr(height - 3 - j, i * bar_width, "█" * bar_width, curses.A_BOLD)

    def handle_keypress(self, key):
        if key == 'b':
            self.boost = max(0.5, min(5.0, self.boost + 0.1))
            return True
        elif key == 'B':
            self.boost = max(0.5, min(5.0, self.boost - 0.1))
            return True
        return False
