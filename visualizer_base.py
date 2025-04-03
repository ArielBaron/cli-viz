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
        # Check if we're in limited color mode
        if curses.COLORS < 256:
            # Map RGB to one of the 8 basic colors
            # Basic approximation: use brightness to choose between colors
            brightness = (r + g + b) / 3
            if brightness < 85:  # Dark
                if r > g and r > b: return curses.color_pair(1)  # Red
                if g > r and g > b: return curses.color_pair(2)  # Green
                if b > r and b > g: return curses.color_pair(4)  # Blue
                return curses.color_pair(0)  # Black
            else:  # Bright
                if r > g and r > b: return curses.color_pair(1) | curses.A_BOLD  # Bright Red
                if g > r and g > b: return curses.color_pair(2) | curses.A_BOLD  # Bright Green
                if b > r and b > g: return curses.color_pair(4) | curses.A_BOLD  # Bright Blue
                if r > 200 and g > 200 and b > 200: return curses.color_pair(7) | curses.A_BOLD  # White
                return curses.color_pair(3)  # Yellow
        else:
            # Original 256-color logic
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