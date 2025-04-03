# visualizers/flame.py
import curses
import random
import numpy as np
from visualizer_base import VisualizerBase

class FlameVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Flame")
        self.flame_width = 80
        self.flame_height = 30
        self.flame_grid = np.zeros((self.flame_height, self.flame_width))
        self.flame_cooling = np.zeros((self.flame_height, self.flame_width))
        
    def setup(self):
        # Initialize flame grid
        self.flame_grid = np.zeros((self.flame_height, self.flame_width))
        self.flame_cooling = np.zeros((self.flame_height, self.flame_width))
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Flame simulation
        # Adjust flame simulation dimensions to fit the screen
        flame_height = min(height - 2, self.flame_height)
        flame_width = min(width, self.flame_width)
        
        # Reset flame grid if dimensions have changed
        if self.flame_grid.shape != (flame_height, flame_width):
            self.flame_grid = np.zeros((flame_height, flame_width))
            self.flame_cooling = np.zeros((flame_height, flame_width))
        
        # Create cooling effect (random values to make flame flicker)
        for i in range(flame_width):
            # More cooling at the edges
            edge_cooling = 0.2 * (1.0 - min(i, flame_width - i - 1) / (flame_width / 2.0))
            for j in range(flame_height):
                # More cooling at the top
                height_cooling = 0.1 * (j / flame_height)  # More cooling at the top (low j)
                self.flame_cooling[j, i] = random.random() * 0.2 + edge_cooling + height_cooling
        
        # Apply cooling
        self.flame_grid -= self.flame_cooling
        self.flame_grid = np.clip(self.flame_grid, 0, 1)
        
        # Generate new heat at the bottom based on audio
        bass = np.mean(spectrum[:10]) * 3  # Use bass frequencies
        mids = np.mean(spectrum[10:30]) * 2  # Use mid frequencies
        
        # Add audio-reactive heat sources
        for i in range(flame_width):
            # Center bias (more heat in the middle)
            center_bias = 1.0 - 0.5 * abs(i - flame_width/2) / (flame_width/2)
            
            # Add random fluctuations for natural look
            fluctuation = random.random() * 0.3 + 0.7
            
            # Calculate heat intensity
            heat = bass * center_bias * fluctuation
            
            # Add extra heat at random positions for crackling effect
            if random.random() < 0.1 * (bass + mids):
                heat += random.random() * 0.5
                
            # Apply heat at the bottom row
            if flame_height > 0:
                self.flame_grid[flame_height-1, i] = min(1.0, heat)
        
        # Propagate heat upwards (fix the direction)
        for y in range(1, flame_height):
            target_y = flame_height - y - 1
            source_y = target_y + 1
            
            if 0 <= source_y < flame_height and 0 <= target_y < flame_height:
                for x in range(flame_width):
                    # Get surrounding cells for diffusion
                    left = max(0, x - 1)
                    right = min(flame_width - 1, x + 1)
                    
                    # Calculate new heat from cells below with some diffusion
                    left_val = self.flame_grid[source_y, left] * 0.2
                    center_val = self.flame_grid[source_y, x] * 0.6
                    right_val = self.flame_grid[source_y, right] * 0.2
                    
                    # Apply upward drift with audio reactivity
                    drift = 0.95 + 0.05 * bass
                    new_val = (left_val + center_val + right_val) * drift
                    
                    # Apply the new heat value
                    self.flame_grid[target_y, x] = min(1.0, new_val)
        
        # Render the flame
        flame_chars = ' .,:;=+*#%@'  # Characters from least to most intense
        
        for y in range(flame_height):
            for x in range(flame_width):
                # Correctly map the flame grid to screen coordinates
                screen_y = height - flame_height + y - 1  # Flame starts at bottom of screen
                screen_x = (width - flame_width) // 2 + x
                
                if 0 <= screen_y < height and 0 <= screen_x < width:
                    # Get heat value at this cell
                    heat = self.flame_grid[y, x]
                    
                    if heat > 0.01:  # Only draw if visible
                        # Map heat to character
                        char_idx = min(len(flame_chars) - 1, int(heat * len(flame_chars)))
                        char = flame_chars[char_idx]
                        
                        # Color based on heat (red->orange->yellow)
                        h = 0.05 + (1.0 - heat) * 0.08  # Hue: red to yellow
                        s = 0.8 + heat * 0.2  # Saturation
                        v = 0.6 + heat * 0.4  # Value/brightness
                        
                        # Get color and draw
                        color_attr = self.hsv_to_color_pair(stdscr, h, s, v)
                        stdscr.addstr(screen_y, screen_x, char, color_attr)
        
        # Draw logs at the bottom
        log_y = height - 1
        log_width = flame_width // 2
        log_start = (width - log_width) // 2
        
        for x in range(log_width):
            # Draw log with brown color
            brown_color = self.get_color_pair(stdscr, 139, 69, 19)  # RGB for brown
            stdscr.addstr(log_y, log_start + x, "▄", brown_color)
            
        # Add some red embers in the log
        for _ in range(5):
            ember_x = log_start + random.randint(0, log_width - 1)
            ember_color = self.hsv_to_color_pair(stdscr, 0.05, 1.0, 0.8)  # Bright red-orange
            stdscr.addstr(log_y, ember_x, "▄", ember_color)
    
    def handle_keypress(self, key):
        if key == 'w':
            self.flame_width = min(200, self.flame_width + 5)
            self.setup()
            return True
        elif key == 'W':
            self.flame_width = max(20, self.flame_width - 5)
            self.setup()
            return True
        elif key == 'h':
            self.flame_height = min(50, self.flame_height + 2)
            self.setup()
            return True
        elif key == 'H':
            self.flame_height = max(10, self.flame_height - 2)
            self.setup()
            return True
        return False