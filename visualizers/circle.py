# visualizers/circle.py
import curses
import math
from visualizer_base import VisualizerBase

class CircleVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Circle Spectrum")
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Circular visualizer
        center_y = height // 2
        center_x = width // 2
        
        # Use lower frequencies for radius variations
        base_radius = min(height, width) // 4
        
        # Draw multiple circles
        for circle_idx in range(5):
            radius_variation = spectrum[:20].mean() * base_radius * 1.5
            radius = base_radius - circle_idx * 3 + radius_variation
            
            # Draw the circle
            for angle in range(0, 360, 5):
                rad = math.radians(angle)
                x = int(center_x + radius * math.cos(rad))
                y = int(center_y + radius * math.sin(rad))
                
                if 0 <= y < height - 1 and 0 <= x < width:
                    # Color based on angle and energy
                    hue = (angle / 360 + hue_offset) % 1.0
                    sat = 0.7 + 0.3 * energy
                    val = 0.7 + 0.3 * energy
                    
                    # Choose character based on energy
                    char = "•" if energy < 0.1 else ("*" if energy < 0.2 else "★")
                    
                    # Get color pair and draw
                    color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                    stdscr.addstr(y, x, char, color_attr | curses.A_BOLD)