# visualizers/starfield_warp.py
import curses
import random
import math
import numpy as np
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
        # New audio reactivity variables
        self.beat_pulse = 0.0
        self.bass_level = 0.0
        self.mid_level = 0.0
        self.treble_level = 0.0
        self.beat_history = [0.0] * 10

    def setup(self):
        self.phase = 0
        self.stars = []
        self.waveform_life = []
        self.beat_pulse = 0.0

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        center_x = width // 2
        center_y = height // 2
        
        # Process audio spectrum into frequency bands
        if len(spectrum) > 30:
            self.bass_level = np.mean(spectrum[:10]) * 2  # Bass frequencies
            self.mid_level = np.mean(spectrum[10:20])     # Mid frequencies
            self.treble_level = np.mean(spectrum[20:30])  # Treble frequencies
        
        # Update beat detection
        self.beat_history.append(energy)
        self.beat_history.pop(0)
        avg_energy = sum(self.beat_history) / len(self.beat_history)
        is_beat = energy > 1.5 * avg_energy and energy > 0.4
        
        # Create beat pulse effect
        if is_beat:
            self.beat_pulse = min(1.0, self.beat_pulse + 0.7 * self.bass_level)
        else:
            self.beat_pulse *= 0.8  # Decay the pulse

        # Update phase with audio reactivity
        self.phase += (0.5 + energy) * self.warp_speed
        
        # Generate new stars - AUDIO REACTIVE: more stars with bass
        star_gen_chance = 0.3 + self.bass_level * 2
        if (len(self.stars) < self.star_count * self.star_density and 
                random.random() < star_gen_chance):
            # Create a new star at a random position near the center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(1, 3)
            
            # Vary star type based on audio spectrum
            if self.bass_level > 0.5:
                star_char = '*'  # Bass-heavy stars are brighter
            elif self.mid_level > 0.3:
                star_char = '+'  # Mid-range gets plus signs
            elif self.treble_level > 0.2:
                star_char = '·'  # Treble gets small dots
            else:
                star_char = '.'  # Default tiny dot
                
            self.stars.append({
                'x': center_x + distance * math.cos(angle),
                'y': center_y + distance * math.sin(angle),
                'angle': angle,
                'speed': 0.1 + random.uniform(0, 0.4) * (1 + self.bass_level),  # Faster with bass
                'size': star_char,
                'hue': random.random(),
                'birth_time': self.phase  # Track when star was created
            })
        
        # VISUALIZE BEAT: Draw expanding circle on beats
        if self.beat_pulse > 0.1:
            pulse_radius = int(max(width, height) * 0.4 * self.beat_pulse)
            pulse_color = self.hsv_to_color_pair(stdscr, hue_offset + 0.6, 1.0, 1.0)
            
            for angle in range(0, 360, 15):  # Draw segments for performance
                rad_angle = math.radians(angle)
                x = int(center_x + pulse_radius * math.cos(rad_angle))
                y = int(center_y + pulse_radius * math.sin(rad_angle))
                
                if 0 <= x < width and 0 <= y < height:
                    try:
                        char = '°' if angle % 30 == 0 else '·'
                        stdscr.addstr(y, x, char, pulse_color)
                    except:
                        pass
        
        # Update and draw stars with enhanced audio reactivity
        new_stars = []
        for star in self.stars:
            # Update star position with audio-reactive speed
            # Bass affects speed, treble affects wobble
            wobble = self.treble_level * math.sin(self.phase * 5 + star['birth_time'])
            star_angle = star['angle'] + wobble * 0.2
            
            # Accelerate based on bass and energy
            star['speed'] += 0.02 * self.bass_level + 0.01 * energy
            
            # Move star outward with audio-reactive speed
            star['x'] += math.cos(star_angle) * star['speed'] * (1 + energy)
            star['y'] += math.sin(star_angle) * star['speed'] * (1 + energy)
            
            # Check if star is still on screen
            distance = math.sqrt((star['x'] - center_x)**2 + (star['y'] - center_y)**2)
            if (0 <= star['x'] < width and 0 <= star['y'] < height and
                    distance < max(width, height)):
                # Draw star with audio-reactive color
                x, y = int(star['x']), int(star['y'])
                
                # Base hue on original + offset, but modulate with mid frequencies
                hue = (star['hue'] + hue_offset + self.mid_level * 0.2) % 1.0
                
                # Saturation based on energy and distance
                sat = min(1.0, 0.5 + distance / 20 + self.beat_pulse * 0.3)
                
                # Value (brightness) pulses with the beat and varies with distance
                val = min(1.0, 0.5 + distance / 20 + self.beat_pulse * 0.5)
                
                # Get color pair and draw
                color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                
                # Choose character based on speed and audio levels
                char = star['size']
                if star['speed'] > 0.5 + self.bass_level:
                    char = '-' if abs(math.cos(star_angle)) > abs(math.sin(star_angle)) else '|'
                if star['speed'] > 1.0 + self.bass_level * 0.5:
                    char = '=' if abs(math.cos(star_angle)) > abs(math.sin(star_angle)) else '‖'
                
                # On strong beats, make some stars flash
                if is_beat and random.random() < self.bass_level:
                    color_attr |= curses.A_REVERSE
                
                try:
                    stdscr.addstr(y, x, char, color_attr | curses.A_BOLD)
                except:
                    # Skip if we can't draw at this position
                    pass
                
                # Keep this star
                new_stars.append(star)
        
        # Update star list
        self.stars = new_stars
        
        # Generate new waveforms on beat detection - ENHANCED
        if is_beat and self.bass_level > 0.3:
            # Find the dominant frequency band
            if len(spectrum) > 0:
                # Create multiple waveforms on strong beats
                waveforms_to_create = 1 + int(self.bass_level * 3)
                
                for _ in range(waveforms_to_create):
                    # Get a random frequency to highlight
                    max_band = max(range(min(len(spectrum), 30)), 
                                  key=lambda i: spectrum[i] * (1 if random.random() < 0.7 else 0.5))
                    norm_freq = max_band / min(len(spectrum), 30)  # Normalized frequency (0-1)
                    
                    # Add new waveform with the dominant frequency
                    angle = random.uniform(0, 2 * math.pi)
                    self.waveform_life.append({
                        'angle': angle,
                        'life': 1.0,
                        'freq': 3 + norm_freq * 10,  # Frequency scaled
                        'amplitude': 5 + self.bass_level * 15,  # Bass-based amplitude
                        'hue': (hue_offset + norm_freq) % 1.0,  # Frequency-based color
                        'width': 1 + int(energy * 2)  # Wider on stronger beats
                    })
                    
                    # Limit waveform count
                    if len(self.waveform_life) > self.waveform_count + int(self.bass_level * 3):
                        self.waveform_life.pop(0)
        
        # Draw waveforms with enhanced audio reactivity
        for wf in self.waveform_life:
            # Decrease life
            wf['life'] -= 0.03 + 0.02 * self.treble_level  # Treble makes waves dissipate faster
            
            if wf['life'] <= 0:
                continue
                
            # Draw waveform line from center outward
            max_distance = min(width, height) // 2 * wf['life']
            angle = wf['angle']
            amplitude = wf['amplitude'] * self.waveform_intensity
            frequency = wf['freq'] * (1 + self.mid_level * 0.5)  # Mid frequencies affect wavelength
            width = wf['width']
            
            # Get color for this waveform with audio-reactive intensity
            hue = (wf['hue'] + self.phase * 0.01) % 1.0
            sat = 0.8 + 0.2 * self.mid_level
            val = 0.7 + 0.3 * wf['life'] + 0.2 * self.beat_pulse
            
            # Draw a sinusoidal line extending outward
            for dist in range(1, int(max_distance), 2):  # Step by 2 for performance
                # Calculate position with audio-reactive wave pattern
                wave_offset = amplitude * math.sin(dist / frequency * math.pi) * wf['life']
                
                # Calculate perpendicular offset direction
                perp_angle = angle + math.pi/2
                
                # Apply offset perpendicular to the main angle
                x = center_x + dist * math.cos(angle) + wave_offset * math.cos(perp_angle)
                y = center_y + dist * math.sin(angle) + wave_offset * math.sin(perp_angle)
                
                # Check bounds
                if 0 <= x < width and 0 <= y < height:
                    # Draw with intensity based on life and audio
                    intensity = wf['life'] * (1 + self.bass_level * 0.5)
                    color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val * intensity)
                    
                    # Use different characters based on wave intensity and audio
                    if dist % 3 == 0:
                        char = '*' if intensity > 0.7 or self.beat_pulse > 0.5 else '+'
                    else:
                        char = '·' if intensity > 0.5 else '.'
                    
                    # Draw the wave point
                    try:
                        stdscr.addstr(int(y), int(x), char, color_attr)
                        
                        # For wide waves, add extra points
                        if width > 1:
                            for w in range(1, width):
                                if random.random() < 0.7:  # Sparse additional points
                                    try:
                                        wx = int(x + w * math.cos(perp_angle))
                                        wy = int(y + w * math.sin(perp_angle))
                                        if 0 <= wx < width and 0 <= wy < height:
                                            stdscr.addstr(wy, wx, '.', color_attr)
                                    except:
                                        pass
                    except:
                        # Skip if we can't draw at this position
                        pass
        
        # Filter out dead waveforms
        self.waveform_life = [wf for wf in self.waveform_life if wf['life'] > 0]
        
        # Display audio levels for debugging
        debug_color = self.hsv_to_color_pair(stdscr, 0.3, 0.7, 0.9)
        try:
            level_bar = f"Bass: {'█' * int(self.bass_level * 10):<10} Mid: {'█' * int(self.mid_level * 10):<10} Treble: {'█' * int(self.treble_level * 10):<10}"
            stdscr.addstr(height-1, 0, level_bar, debug_color)
        except:
            pass
    
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