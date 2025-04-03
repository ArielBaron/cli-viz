# visualizer_base.py
import curses

class VisualizerBase:
    """Base class for audio visualizers"""
    
    def __init__(self, name="Base Visualizer"):
        self.name = name
    
    def setup(self):
        """Initialize any visualizer-specific state"""
        pass
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        """
        Draw the visualization
        
        Args:
            stdscr: curses screen object
            spectrum: audio frequency spectrum data
            height: screen height
            width: screen width
            energy: current audio energy level
            hue_offset: current color hue offset
        """
        raise NotImplementedError("Visualizers must implement the draw method")
    
    def handle_keypress(self, key):
        """
        Handle visualizer-specific keypresses
        
        Args:
            key: key that was pressed
            
        Returns:
            True if the key was handled, False otherwise
        """
        return False
    
    def get_color_pair(self, stdscr, r, g, b):
        """Helper method to get color pair for RGB values"""
        # Map r,g,b (0-255) to a predefined color pair
        # Convert to 0-5 range for r,g,b
        r_idx = min(5, r * 6 // 256)
        g_idx = min(5, g * 6 // 256)
        b_idx = min(5, b * 6 // 256)
        
        # Calculate color index
        color_idx = 36 * r_idx + 6 * g_idx + b_idx + 1
        
        return curses.color_pair(color_idx)
    
    def hsv_to_color_pair(self, stdscr, h, s, v):
        """Helper method to get color pair for HSV values"""
        # Convert HSV to RGB
        h = h % 1.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return self.get_color_pair(stdscr, r, g, b)