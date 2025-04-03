# visualizers/starfield_warp.py
import curses
import random
import math
from visualizer_base import VisualizerBase

class StarfieldWarpVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Starfield Warp")
        self.stars = []
        self.star_count = 100
        self.warp_speed = 0.5
        self.waveform_intensity = 1.0
        self.waveform_count = 6
        self.waveform_life = []
        self.star_density = 1.0

    def setup(self):
        self.phase = 0
        self.stars = []
        self.waveform_life = []

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        center_x = width // 2
        center_y = height // 2
        self.phase += energy * self.warp_speed
        
        # Generate new stars if needed
        if len(self.stars) < self.star_count * self.star_density:
            # Create a new star at a random position near the center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(1, 3)
            self.stars.append({
                'x': center_x + distance * math.cos(angle),
                'y': center_y + distance * math.sin(angle),
                'angle': angle,
                'speed': random.uniform(0.1, 0.3),
                'size': random.choice(['.', '*', '+', '·']),
                'hue': random.random()
            })
        
        # Update and draw stars
        new_stars = []
        for star in self.stars:
            # Update star position - move outward from center
            star['speed'] += 0.01 * energy  # Accelerate based on energy
            distance = math.sqrt((star['x'] - center_x)**2 + (star['y'] - center_y)**2)
            
            # Move star outward
            star['x'] += math.cos(star['angle']) * star['speed'] * (1 + energy)
            star['y'] += math.sin(star['angle']) * star['speed'] * (1 + energy)
            
            # Check if star is still on screen
            if (0 <= star['x'] < width and 0 <= star['y'] < height and
                    distance < max(width, height)):
                # Draw star
                x, y = int(star['x']), int(star['y'])
                
                # Calculate color based on distance and original hue
                hue = (star['hue'] + hue_offset) % 1.0
                sat = min(1.0, distance / 10)  # Saturation increases with distance
                val = min(1.0, 0.5 + distance / 20)  # Value increases with distance
                
                # Get color pair and draw
                color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                # Choose character based on speed/distance for streaking effect
                char = star['size']
                if star['speed'] > 0.5:
                    char = '-' if abs(math.cos(star['angle'])) > abs(math.sin(star['angle'])) else '|'
                if star['speed'] > 1.0:
                    char = '=' if abs(math.cos(star['angle'])) > abs(math.sin(star['angle'])) else '‖'
                
                try:
                    stdscr.addstr(y, x, char, color_attr | curses.A_BOLD)
                except:
                    # Skip if we can't draw at this position
                    pass
                
                # Keep this star
                new_stars.append(star)
        
        # Update star list
        self.stars = new_stars
        
        # Generate new waveforms on beat detection
        if energy > 0.6 and random.random() < energy * 0.3:
            # Find the dominant frequency band
            if len(spectrum) > 0:
                max_band = max(range(len(spectrum)), key=lambda i: spectrum[i])
                norm_freq = max_band / len(spectrum)  # Normalized frequency (0-1)
                
                # Add new waveform with the dominant frequency
                self.waveform_life.append({
                    'angle': random.uniform(0, 2 * math.pi),
                    'life': 1.0,
                    'freq': 3 + norm_freq * 10,  # Frequency scaled
                    'amplitude': 5 + energy * 10,  # Amplitude based on energy
                    'hue': random.random()
                })
                
                # Limit waveform count
                if len(self.waveform_life) > self.waveform_count:
                    self.waveform_life.pop(0)
        
        # Draw waveforms
        for wf in self.waveform_life:
            # Decrease life
            wf['life'] -= 0.05
            
            if wf['life'] <= 0:
                continue
                
            # Draw waveform line from center outward
            max_distance = min(width, height) // 2 * wf['life']
            angle = wf['angle']
            amplitude = wf['amplitude'] * self.waveform_intensity
            frequency = wf['freq']
            
            # Get color for this waveform
            hue = (wf['hue'] + hue_offset) % 1.0
            sat = 0.8
            val = 0.7 + 0.3 * wf['life']
            
            # Draw a sinusoidal line extending outward
            prev_x, prev_y = center_x, center_y
            for dist in range(1, int(max_distance)):
                # Calculate position along the angle with sinusoidal offset
                wave_offset = amplitude * math.sin(dist / frequency * math.pi) * wf['life']
                
                # Calculate perpendicular offset direction
                perp_angle = angle + math.pi/2
                
                # Apply offset perpendicular to the main angle
                x = center_x + dist * math.cos(angle) + wave_offset * math.cos(perp_angle)
                y = center_y + dist * math.sin(angle) + wave_offset * math.sin(perp_angle)
                
                # Check bounds
                if 0 <= x < width and 0 <= y < height:
                    # Draw with intensity based on life
                    intensity = wf['life']
                    color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val * intensity)
                    
                    # Use different characters based on wave intensity
                    if dist % 3 == 0:
                        char = '*' if intensity > 0.7 else '+'
                    else:
                        char = '·' if intensity > 0.5 else '.'
                        
                    try:
                        stdscr.addstr(int(y), int(x), char, color_attr)
                    except:
                        # Skip if we can't draw at this position
                        pass
                
                prev_x, prev_y = x, y
        
        # Filter out dead waveforms
        self.waveform_life = [wf for wf in self.waveform_life if wf['life'] > 0]
    
    def handle_keypress(self, key):
        if key == 'w':  # Increase warp speed
            self.warp_speed = min(2.0, self.warp_speed + 0.1)
            return True
        elif key == 'W':  # Decrease warp speed
            self.warp_speed = max(0.1, self.warp_speed - 0.1)
            return True
        elif key == 'i':  # Increase waveform intensity
            self.waveform_intensity = min(2.0, self.waveform_intensity + 0.1)
            return True
        elif key == 'I':  # Decrease waveform intensity
            self.waveform_intensity = max(0.1, self.waveform_intensity - 0.1)
            return True
        elif key == 'n':  # Increase star density
            self.star_density = min(3.0, self.star_density + 0.2)
            return True
        elif key == 'N':  # Decrease star density
            self.star_density = max(0.2, self.star_density - 0.2)
            return True
        return False