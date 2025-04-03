# visualizers/fractal_universe_lite.py
import curses
import numpy as np
import cmath
import random
import time
from visualizer_base import VisualizerBase

class FractalUniverseLiteVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Fractal Universe Lite")
        # Core fractal parameters (reduced for low-end devices)
        self.max_iterations = 15  # Lower detail level
        self.zoom = 2.5  # Starting zoom level
        self.center_x = 0
        self.center_y = 0
        self.julia_mode = False  # Start in Mandelbrot mode
        
        # Audio influence parameters
        self.zoom_target = 2.5
        self.zoom_speed = 0.03
        self.julia_seed = complex(-0.8, 0.156)
        
        # Animation state (simplified)
        self.beat_intensity = 0
        self.last_beat_time = 0
        
        # Rendering characters (reduced set)
        self.density_chars = " .,:;+*#@"
        self.render_mode = 0  # 0=normal, 1=psychedelic
        
        # Performance optimization
        self.downsample = 2  # Compute at lower resolution
        self.skip_frames = 0  # For skipping computation on some frames
        self.frame_counter = 0
        self.fractal_buffer = None  # Cache to store computed fractal
    
    def setup(self):
        self.start_time = time.time()
    
    def compute_fractal(self, width, height, spectrum, energy):
        # Increment frame counter
        self.frame_counter += 1
        
        # Skip computation on some frames to improve performance
        if self.fractal_buffer is not None and self.frame_counter % (self.skip_frames + 1) != 0:
            return self.fractal_buffer, False
        
        # Create buffer for fractal data (at reduced resolution)
        ds_width = width // self.downsample
        ds_height = height // self.downsample
        buffer = np.zeros((ds_height, ds_width), dtype=float)
        
        # Adjust iterations based on mid frequencies (simplified)
        mid_energy = np.mean(spectrum[5:15]) * 2  # Use fewer bands
        current_max_iter = int(self.max_iterations * (1.0 + mid_energy))
        
        # Calculate aspect ratio correction
        aspect_ratio = ds_height / ds_width
        
        # Calculate zoom based on bass (simplified)
        bass = np.mean(spectrum[:5]) * 2  # Use fewer bands
        self.zoom_target = max(0.8, min(5.0, 2.5 - bass * 3.0))
        self.zoom += (self.zoom_target - self.zoom) * self.zoom_speed
        
        # Determine if a beat has occurred (simplified)
        current_time = time.time()
        beat_detected = False
        
        if energy > 0.25 and current_time - self.last_beat_time > 0.3:
            beat_detected = True
            self.last_beat_time = current_time
            self.beat_intensity = min(1.0, energy * 1.5)
            
            # Toggle modes occasionally on beats
            if self.julia_mode and random.random() < 0.2:
                self.julia_mode = False
            elif not self.julia_mode and random.random() < 0.1:
                self.julia_mode = True
                
                # Update Julia seed (simplified)
                angle = current_time * 0.2
                radius = 0.7 + bass * 0.2
                self.julia_seed = complex(
                    radius * np.cos(angle), 
                    radius * np.sin(angle)
                )
        
        # Update beat intensity decay
        self.beat_intensity *= 0.9
        
        # Compute the fractal - use step size to skip pixels for better performance
        step_size = 1  # Can be increased to 2 or 3 on very low-end devices
        for y in range(0, ds_height, step_size):
            for x in range(0, ds_width, step_size):
                # Map pixel coordinates to complex plane
                real = (x - ds_width/2) * (4.0 / ds_width) * self.zoom + self.center_x
                imag = (y - ds_height/2) * (4.0 / ds_width) * aspect_ratio * self.zoom + self.center_y
                c = complex(real, imag)
                
                # Initialize z based on mode
                if self.julia_mode:
                    z = c
                    c = self.julia_seed
                else:  # Mandelbrot mode
                    z = complex(0, 0)
                
                # Iterate to determine if point is in set
                iteration = 0
                while abs(z) < 4.0 and iteration < current_max_iter:
                    # Apply simplified formula based on render mode
                    if self.render_mode == 1:  # Psychedelic mode
                        z = z*z*z + c
                    else:  # Normal mode
                        z = z*z + c
                    
                    iteration += 1
                
                # Calculate color value (simplified)
                if iteration < current_max_iter:
                    value = iteration / current_max_iter
                    buffer[y, x] = value
                else:
                    buffer[y, x] = 0
                
                # Fill in skipped pixels by copying
                if step_size > 1:
                    for dy in range(step_size):
                        for dx in range(step_size):
                            ny, nx = y + dy, x + dx
                            if ny < ds_height and nx < ds_width:
                                buffer[ny, nx] = buffer[y, x]
        
        # Store buffer for frame skipping
        self.fractal_buffer = (buffer, beat_detected)
        return self.fractal_buffer
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Compute the fractal field
        fractal_field, beat_detected = self.compute_fractal(width, height, spectrum, energy)
        
        # Get audio metrics (simplified)
        bass = np.mean(spectrum[:5]) * 2
        
        # Draw title with information
        mode_name = "Julia" if self.julia_mode else "Mandelbrot"
        title = f"Fractal Universe Lite | {mode_name} | Zoom: {1/self.zoom:.1f}x"
        title_color = self.hsv_to_color_pair(stdscr, hue_offset, 0.8, 1.0)
        try:
            stdscr.addstr(0, max(0, width//2 - len(title)//2), title, title_color | curses.A_BOLD)
        except curses.error:
            pass
        
        # Draw the fractal field (upscale from lower resolution)
        ds_height, ds_width = fractal_field.shape
        
        # Limit drawing to alternate lines for better performance
        draw_step = 1 if height < 30 else 1  # Increase step for very small terminals
        
        for y in range(0, height-1, draw_step):
            # Map to downsampled coordinates
            ds_y = min(ds_height-1, y // self.downsample)
            
            for x in range(0, width, draw_step):
                # Map to downsampled coordinates
                ds_x = min(ds_width-1, x // self.downsample)
                
                value = fractal_field[ds_y, ds_x]
                
                if value == 0:  # Inside the set
                    if self.julia_mode:
                        # Simple coloring for Julia sets
                        inner_hue = (hue_offset + bass * 0.2) % 1.0
                        color = self.hsv_to_color_pair(stdscr, inner_hue, 0.7, 0.5)
                        try:
                            stdscr.addstr(y+1, x, "●", color)
                        except curses.error:
                            pass
                    else:
                        # Simple black for Mandelbrot inside
                        try:
                            stdscr.addstr(y+1, x, " ")
                        except curses.error:
                            pass
                else:
                    # Outside the set - map to colors and characters
                    
                    # Adjust hue based on value and audio (simplified)
                    point_hue = (value + hue_offset) % 1.0
                    
                    # Add beat pulse to brightness
                    val = 0.7 + 0.3 * value
                    if beat_detected or self.beat_intensity > 0.1:
                        val = min(1.0, val + self.beat_intensity * 0.3)
                    
                    # Get the color
                    color = self.hsv_to_color_pair(stdscr, point_hue, 0.8, val)
                    
                    # Map value to character density (simplified)
                    char_idx = min(len(self.density_chars)-1, 
                                 int(value * len(self.density_chars)))
                    char = self.density_chars[char_idx]
                    
                    # Draw the character
                    try:
                        stdscr.addstr(y+1, x, char, color)
                    except curses.error:
                        pass
        
        # Draw simple controls help at bottom
        controls = "J: Toggle Mode | R: Reset | Arrow Keys: Navigate"
        try:
            stdscr.addstr(height-1, max(0, width//2 - len(controls)//2), controls, title_color)
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
            return True
        
        # Change rendering style
        elif key == '1':
            self.render_mode = 0
            return True
        elif key == '2':
            self.render_mode = 1
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
            self.zoom_target = max(0.1, self.zoom_target / 1.2)
            return True
        elif key == '-':
            self.zoom_target = min(8.0, self.zoom_target * 1.2)
            return True
        
        # Performance options
        elif key == '9':
            # Decrease quality for better performance
            self.downsample = min(4, self.downsample + 1)
            self.skip_frames = min(3, self.skip_frames + 1)
            self.fractal_buffer = None  # Clear cache to force redraw
            return True
        elif key == '0':
            # Increase quality at expense of performance
            self.downsample = max(1, self.downsample - 1)
            self.skip_frames = max(0, self.skip_frames - 1)
            self.fractal_buffer = None  # Clear cache to force redraw
            return True
            
        return False