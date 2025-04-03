# visualizers/matrix_rain.py
import curses
import random
import numpy as np
from visualizer_base import VisualizerBase

class MatrixRainVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Matrix Rain")
        # Configuration parameters
        self.density = 0.2  # Controls density of drops (0.0-1.0)
        self.speed_factor = 1.0  # Base speed multiplier
        self.length_factor = 1.0  # Length of trails
        self.spawn_threshold = 0.05  # Minimum energy to spawn drops
        
        # Internal state
        self.drops = []  # List of active raindrop trails
        self.chars = "".join([chr(i) for i in range(33, 127)] + [chr(i) for i in range(0x30A0, 0x30FF)])
        self.last_beat = 0
        self.beat_active = False
        self.beat_cooldown = 0
        
    def setup(self):
        # Initialize any resources needed
        random.seed()
    
    def spawn_drops(self, count, width, spectrum):
        """Spawn new drops based on audio spectrum"""
        for _ in range(count):
            # Determine position - influenced by spectrum
            # Higher amplitude frequencies have more chance to spawn drops
            spectrum_pos = min(len(spectrum) - 1, random.randint(0, len(spectrum) // 2))
            spawn_weight = spectrum[spectrum_pos] * 3.0
            
            if random.random() < spawn_weight:
                x = random.randint(0, width - 1)
                # Create a new drop
                drop = {
                    'x': x,
                    'y': 0,
                    'speed': random.uniform(0.2, 0.8) * self.speed_factor,
                    'length': random.randint(3, 20) * self.length_factor,
                    'char_idx': 0,
                    'chars': ''.join(random.choice(self.chars) for _ in range(random.randint(5, 15))),
                    'bright': random.random() < 0.2,  # Occasional bright character
                    'freq_index': spectrum_pos,  # Remember which frequency this drop responds to
                }
                self.drops.append(drop)
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Handle beat detection for dramatic effects
        beat_detected = False
        if energy > 0.2 and self.beat_cooldown == 0:
            self.beat_active = True
            self.beat_cooldown = 5
            beat_detected = True
        elif self.beat_cooldown > 0:
            self.beat_cooldown -= 1
        
        # Calculate bass, mid, and treble energy
        bass = np.mean(spectrum[:10]) * 2
        mids = np.mean(spectrum[10:30])
        treble = np.mean(spectrum[30:])
        
        # Base spawn rate on overall energy and beat detection
        base_spawn_rate = int(width * 0.15 * self.density)
        spawn_boost = 5 if beat_detected else 0
        spawn_count = base_spawn_rate + int(energy * 15) + spawn_boost
        
        # Spawn new drops
        if energy > self.spawn_threshold:
            self.spawn_drops(spawn_count, width, spectrum)
        
        # Update and draw existing drops
        new_drops = []
        for drop in self.drops:
            # Update drop position - speed affected by corresponding frequency
            freq_amplitude = spectrum[drop['freq_index']] * 3.0
            drop['y'] += drop['speed'] * (1 + freq_amplitude)
            
            # Periodically change the character
            if random.random() < 0.1:
                drop['char_idx'] = (drop['char_idx'] + 1) % len(drop['chars'])
            
            # Skip if out of bounds
            if drop['y'] >= height:
                continue
            
            # Calculate how much of the trail to draw
            trail_start = int(max(0, drop['y'] - drop['length']))
            trail_end = int(drop['y'])
            
            # Draw the trail
            for y in range(trail_start, trail_end + 1):
                if 0 <= y < height:
                    # Closer to head = brighter
                    proximity = 1.0 - (trail_end - y) / drop['length']
                    
                    # Get a character from the drop's character set
                    char_position = (drop['char_idx'] + (y % len(drop['chars']))) % len(drop['chars'])
                    char = drop['chars'][char_position]
                    
                    # Determine color based on position and audio frequencies
                    if y == trail_end:  # Head of the drop
                        # Head color influenced by beat and bass
                        hue = (drop['x'] / width + hue_offset + bass * 0.3) % 1.0
                        saturation = 0.7 if drop['bright'] else 0.5
                        value = 1.0 if drop['bright'] else 0.7
                        attr = curses.A_BOLD
                    else:
                        # Trail color with gradient
                        hue = (drop['x'] / width + hue_offset) % 1.0
                        saturation = 0.7 * proximity
                        value = max(0.4, proximity) * 0.8
                        attr = 0
                    
                    # Adjust color based on beat detection
                    if self.beat_active and drop['bright']:
                        saturation = min(1.0, saturation + 0.3)
                        value = min(1.0, value + 0.3)
                    
                    # Apply color and draw character
                    color = self.hsv_to_color_pair(stdscr, hue, saturation, value)
                    try:
                        stdscr.addstr(y, drop['x'], char, color | attr)
                    except curses.error:
                        pass  # Ignore errors from writing at screen edge
            
            # Keep this drop for next frame
            new_drops.append(drop)
        
        # Replace drops list with updated list
        self.drops = new_drops
        
        # Draw info text
        info_text = f"Drops: {len(self.drops)} | Energy: {energy:.2f} | Bass: {bass:.2f}"
        color = self.hsv_to_color_pair(stdscr, hue_offset, 0.7, 1.0)
        stdscr.addstr(height - 1, 0, info_text, color | curses.A_BOLD)
        
        # Additional visual effect on beat
        if beat_detected:
            # Flash screen corners on strong beats
            for corner_y, corner_x in [(1, 1), (1, width-2), (height-2, 1), (height-2, width-2)]:
                if 0 <= corner_y < height and 0 <= corner_x < width:
                    try:
                        stdscr.addstr(corner_y, corner_x, "✧", self.hsv_to_color_pair(stdscr, hue_offset, 1.0, 1.0) | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Decay beat active state
        if self.beat_active and not beat_detected:
            self.beat_active = False
    
    def handle_keypress(self, key):
        # Adjust density
        if key == 'd':
            self.density = min(1.0, self.density + 0.05)
            return True
        elif key == 'D':
            self.density = max(0.05, self.density - 0.05)
            return True
        # Adjust speed
        elif key == 's':
            self.speed_factor = min(3.0, self.speed_factor + 0.1)
            return True
        elif key == 'S':
            self.speed_factor = max(0.1, self.speed_factor - 0.1)
            return True
        # Adjust trail length
        elif key == 'l':
            self.length_factor = min(3.0, self.length_factor + 0.1)
            return True
        elif key == 'L':
            self.length_factor = max(0.1, self.length_factor - 0.1)
            return True
        # Reset parameters
        elif key == 'r':
            self.density = 0.2
            self.speed_factor = 1.0
            self.length_factor = 1.0
            return True
        return False