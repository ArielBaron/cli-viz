# visualizers/fractal_universe.py
import curses
import numpy as np
import cmath
import random
import time
from visualizer_base import VisualizerBase

class FractalUniverseVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Fractal Universe")
        # Core fractal parameters
        self.max_iterations = 30  # Detail level
        self.zoom = 2.5  # Starting zoom level
        self.center_x = 0
        self.center_y = 0
        self.julia_mode = False  # Start in Mandelbrot mode
        self.fractal_shift_factor = 0.02
        
        # Audio influence parameters
        self.zoom_target = 2.5
        self.zoom_speed = 0.05
        self.color_cycle_speed = 0.1
        self.julia_seed = complex(-0.8, 0.156)
        self.julia_seed_history = []  # Track past positions for trails
        
        # Animation and transition state
        self.beat_intensity = 0
        self.last_beat_time = 0
        self.rotation = 0
        self.pattern_complexity = 1.0  # Multiplier for iterations
        self.last_big_beat = 0
        self.warp_active = False
        self.warp_progress = 0
        
        # Rendering characters (from most dense to least)
        self.density_chars = " .'`^\",:;Il!i><~+_-?][}{1)(|/\\tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.render_mode = 0  # 0=normal, 1=gradient, 2=psychedelic
        
    def setup(self):
        self.start_time = time.time()
        # Initialize seed history with current seed
        for i in range(20):
            self.julia_seed_history.append(self.julia_seed)
    
    def compute_fractal(self, width, height, spectrum, energy):
        # Create buffer for fractal data
        buffer = np.zeros((height, width), dtype=float)
        
        # Adjust complexity based on mid frequencies
        mid_energy = np.mean(spectrum[10:30])
        self.pattern_complexity = 1.0 + mid_energy * 3.0
        current_max_iter = int(self.max_iterations * self.pattern_complexity)
        
        # Calculate aspect ratio correction
        aspect_ratio = height / width
        
        # Calculate zoom based on bass frequencies
        bass = np.mean(spectrum[:10]) * 2
        self.zoom_target = max(0.5, min(10.0, 2.5 - bass * 5.0))
        self.zoom += (self.zoom_target - self.zoom) * self.zoom_speed
        
        # Affect rotation based on treble frequencies
        treble = np.mean(spectrum[30:])
        self.rotation += treble * 0.1
        
        # Determine if a beat has occurred
        current_time = time.time()
        beat_detected = False
        big_beat_detected = False
        
        if energy > 0.2 and current_time - self.last_beat_time > 0.2:
            beat_detected = True
            self.last_beat_time = current_time
            self.beat_intensity = min(1.0, energy * 2)
            
            # Check for big beats (stronger and less frequent)
            if energy > 0.4 and current_time - self.last_big_beat > 1.5:
                big_beat_detected = True
                self.last_big_beat = current_time
                self.warp_active = True
                self.warp_progress = 0
        
        # Update beat intensity decay
        self.beat_intensity *= 0.9
        
        # Update warp effect
        if self.warp_active:
            self.warp_progress += 0.05
            if self.warp_progress >= 1.0:
                self.warp_active = False
                
                # After warp, toggle between Mandelbrot and Julia modes
                if big_beat_detected or random.random() < 0.3:
                    self.julia_mode = not self.julia_mode
                
                # Sometimes change render mode on big beats
                if big_beat_detected and random.random() < 0.4:
                    self.render_mode = (self.render_mode + 1) % 3
        
        # Update Julia seed based on bass and beat
        if self.julia_mode:
            # Create orbital motion with audio influence
            angle = current_time * (0.2 + bass * 0.5)
            radius = 0.7 + 0.2 * np.sin(current_time * 0.25) + bass * 0.3
            
            target_seed = complex(
                radius * np.cos(angle), 
                radius * np.sin(angle)
            )
            
            # Move seed toward target
            seed_diff = target_seed - self.julia_seed
            self.julia_seed += seed_diff * (0.1 + bass * 0.3)
            
            # Add current seed to history and remove oldest
            self.julia_seed_history.append(self.julia_seed)
            if len(self.julia_seed_history) > 20:
                self.julia_seed_history.pop(0)
        
        # Compute the fractal
        for y in range(height):
            for x in range(width):
                # Map pixel coordinates to complex plane
                real = (x - width/2) * (4.0 / width) * self.zoom + self.center_x
                imag = (y - height/2) * (4.0 / width) * aspect_ratio * self.zoom + self.center_y
                c = complex(real, imag)
                
                # Apply rotation if active
                if self.rotation != 0:
                    rot = cmath.exp(complex(0, self.rotation))
                    c = c * rot
                
                # Apply warp effect
                if self.warp_active:
                    # Spiral warp
                    warp_factor = self.warp_progress * 2 * np.pi
                    c = c * cmath.exp(complex(0, warp_factor * self.beat_intensity))
                
                # Initialize z based on mode
                if self.julia_mode:
                    z = c
                    c = self.julia_seed
                else:  # Mandelbrot mode
                    z = complex(0, 0)
                
                # Iterate to determine if point is in set
                iteration = 0
                escape_radius = 4.0 + self.beat_intensity * 12.0  # Dynamic escape radius
                
                while abs(z) < escape_radius and iteration < current_max_iter:
                    # Apply variations based on render mode
                    if self.render_mode == 1:  # Gradient mode
                        z = z*z + c + complex(0, 0.01 * np.sin(current_time))
                    elif self.render_mode == 2:  # Psychedelic mode
                        # Fractal variations
                        z = z*z*z/(z*z+c) + c
                    else:  # Normal mode
                        z = z*z + c
                    
                    iteration += 1
                
                # If point escapes, calculate smoothed iteration count
                if iteration < current_max_iter:
                    # Smooth coloring formula
                    smooth_iteration = iteration + 1 - np.log(np.log(abs(z))) / np.log(2)
                    buffer[y, x] = smooth_iteration / current_max_iter
                else:
                    buffer[y, x] = 0
        
        return buffer, beat_detected
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Compute the fractal field
        fractal_field, beat_detected = self.compute_fractal(width, height, spectrum, energy)
        
        # Get additional audio metrics
        bass = np.mean(spectrum[:10]) * 2
        mids = np.mean(spectrum[10:30])
        treble = np.mean(spectrum[30:])
        
        # Draw title with information
        mode_name = "Julia" if self.julia_mode else "Mandelbrot"
        render_names = ["Classic", "Gradient", "Psychedelic"]
        title = f"Fractal Universe | {mode_name} | {render_names[self.render_mode]} | Zoom: {1/self.zoom:.2f}x"
        title_color = self.hsv_to_color_pair(stdscr, hue_offset, 0.8, 1.0)
        stdscr.addstr(0, width//2 - len(title)//2, title, title_color | curses.A_BOLD)
        
        # Draw the fractal field
        for y in range(min(height-1, fractal_field.shape[0])):
            for x in range(min(width, fractal_field.shape[1])):
                value = fractal_field[y, x]
                
                if value == 0:  # Inside the set
                    if self.julia_mode:
                        # For Julia sets, use inner coloring based on position
                        inner_hue = ((x / width + y / height) / 2 + hue_offset + bass * 0.2) % 1.0
                        inner_sat = 0.7 + 0.3 * mids
                        inner_val = 0.5 + 0.5 * bass
                        color = self.hsv_to_color_pair(stdscr, inner_hue, inner_sat, inner_val)
                        stdscr.addstr(y+1, x, "●", color)
                    else:
                        # Void character for Mandelbrot inside
                        stdscr.addstr(y+1, x, " ")
                else:
                    # Outside the set - map to colors and characters based on iteration count
                    
                    # Adjust hue based on value and audio
                    point_hue = (value + hue_offset + treble * 0.3) % 1.0
                    
                    # Dynamic saturation and value
                    sat = 0.7 + 0.3 * max(0, min(1, value * 2))
                    val = 0.7 + 0.3 * value
                    
                    # Add beat pulse to brightness
                    if beat_detected or self.beat_intensity > 0.1:
                        val = min(1.0, val + self.beat_intensity * 0.3)
                    
                    # Get the color
                    color = self.hsv_to_color_pair(stdscr, point_hue, sat, val)
                    
                    # Map value to character density
                    char_idx = min(len(self.density_chars)-1, 
                                 int(value * len(self.density_chars)))
                    char = self.density_chars[char_idx]
                    
                    # Apply bold attribute for higher values
                    attrs = curses.A_BOLD if value > 0.7 else 0
                    
                    # Draw the character
                    try:
                        stdscr.addstr(y+1, x, char, color | attrs)
                    except curses.error:
                        pass
        
        # If in Julia mode, draw the seed trail
        if self.julia_mode:
            for i, seed in enumerate(self.julia_seed_history):
                # Map complex position to screen coordinates
                screen_x = int(width/2 + (seed.real / self.zoom) * (width/4))
                screen_y = int(height/2 + (seed.imag / self.zoom) * (width/4))
                
                # Skip if out of bounds
                if 0 <= screen_x < width and 1 <= screen_y < height:
                    # Fade opacity based on age
                    opacity = i / len(self.julia_seed_history)
                    trail_hue = (hue_offset + 0.5) % 1.0  # Complementary color
                    trail_color = self.hsv_to_color_pair(stdscr, trail_hue, 1.0, opacity)
                    
                    # Use different characters for trail based on position
                    trail_chars = "·•●★✧"
                    char_idx = min(len(trail_chars)-1, int(opacity * len(trail_chars)))
                    
                    try:
                        stdscr.addstr(screen_y, screen_x, trail_chars[char_idx], 
                                     trail_color | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Draw controls help at bottom
        controls = "J: Toggle Mode | R: Reset | 1-3: Rendering Style | Arrow Keys: Navigate"
        stdscr.addstr(height-1, width//2 - len(controls)//2, controls, title_color)
        
        # Draw beat indicator
        if beat_detected or self.beat_intensity > 0.1:
            beat_size = int((width-2) * self.beat_intensity)
            beat_bar = "█" * beat_size
            beat_color = self.hsv_to_color_pair(stdscr, (hue_offset + 0.3) % 1.0, 1.0, 1.0)
            stdscr.addstr(height-2, 1, beat_bar, beat_color | curses.A_BOLD)
        
        # Create corner effects on big beats or warp transitions
        if self.warp_active:
            corner_chars = ["╔", "╗", "╚", "╝"]
            corners = [(1, 1), (1, width-2), (height-2, 1), (height-2, width-2)]
            for i, (y, x) in enumerate(corners):
                if 0 <= y < height and 0 <= x < width:
                    corner_color = self.hsv_to_color_pair(stdscr, 
                                                        (hue_offset + self.warp_progress) % 1.0, 
                                                        1.0, 1.0)
                    try:
                        stdscr.addstr(y, x, corner_chars[i], corner_color | curses.A_BOLD)
                    except curses.error:
                        pass
    
    def handle_keypress(self, key):
        # Toggle fractal mode
        if key == 'j' or key == 'J':
            self.julia_mode = not self.julia_mode
            return True
        
        # Reset view
        elif key == 'r' or key == 'R':
            self.zoom = 2.5
            self.zoom_target = 2.5
            self.center_x = 0
            self.center_y = 0
            self.rotation = 0
            return True
        
        # Change rendering style
        elif key in ['1', '2', '3']:
            self.render_mode = int(key) - 1
            return True
        
        # Navigation
        elif key == 'KEY_UP':
            self.center_y -= 0.1 * self.zoom
            return True
        elif key == 'KEY_DOWN':
            self.center_y += 0.1 * self.zoom
            return True
        elif key == 'KEY_LEFT':
            self.center_x -= 0.1 * self.zoom
            return True
        elif key == 'KEY_RIGHT':
            self.center_x += 0.1 * self.zoom
            return True
        
        # Zoom controls
        elif key == '+' or key == '=':
            self.zoom_target = max(0.01, self.zoom_target / 1.2)
            return True
        elif key == '-':
            self.zoom_target = min(10.0, self.zoom_target * 1.2)
            return True
            
        return False