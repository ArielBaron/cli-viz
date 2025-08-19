class VisualizerBase:
    """Minimal base class for audio visualizers"""

    def __init__(self, name="Base Visualizer"):
        self.name = name

    def setup(self):
        pass

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        raise NotImplementedError("Visualizers must implement the draw method")

    def handle_keypress(self, key):
        return False
