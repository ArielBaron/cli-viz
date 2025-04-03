# visualizers/cosmic_pulsar.py
import curses
import random
import math
from visualizer_base import VisualizerBase

class CosmicPulsarVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Cosmic Pulsar")
        self.pulsar_rings = []
        self.energy_threshold = 0.5
        self.ring_density = 1.0
        self.color_mode = 0  # 0: rainbow, 1: monochrome, 2: complementary
        self.orbital_particles = []
        self.orbital_count = 80
        self.gravity_wells = []
        self.max_wells = 3
        self.symmetry = 4  # Rotational symmetry (4 = fourfold symmetry)
        
    def setup(self):
        self.time = 0
        self.pulsar_rings = []
        self.orbital_particles = []
        self.gravity_wells = []
        
        # Create initial orbital particles
        for _ in range(self.orbital_count):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(8, 20)
            orbital_speed = 0.02 + random.uniform(-0.01, 0.01)
            self.orbital_particles.append({
                'angle': angle,
                'radius': radius,
                'orbital_speed': orbital_speed,
                'size': random.choice(['*', '.', '+', '·', '•']),
                'hue': random.random()
            })

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        center_x = width // 2
        center_y = height // 2
        self.time += 0.05
        
        # Create pulsar rings on strong beats
        if energy > self.energy_threshold and random.random() < energy * 0.3:
            # Add a new expanding ring
            ring_count = int(1 + energy * 2 * self.ring_density)
            for _ in range(ring_count):
                thickness = random.choice([1, 2])
                wave_amplitude = random.uniform(0, 2) if random.random() > 0.5 else 0
                self.pulsar_rings.append({
                    'radius': 1,
                    'growth_rate': 0.5 + energy * 0.8,  # Faster expansion with more energy
                    'life': 1.0,
                    'thickness': thickness,
                    'hue': random.random(),
                    'wave_freq': random.uniform(4, 8),
                    'wave_amp': wave_amplitude,
                    'segments': random.randint(self.symmetry, self.symmetry * 3) if random.random() > 0.7 else 0
                })
        
        # Create or update gravity wells
        if len(self.gravity_wells) < self.max_wells and random.random() < 0.01 + energy * 0.02:
            # Create a new gravity well at a random position
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 15)
            lifetime = random.uniform(5, 15)
            
            self.gravity_wells.append({
                'x': center_x + distance * math.cos(angle),
                'y': center_y + distance * math.sin(angle),
                'strength': random.uniform(0.5, 2.0),
                'life': 1.0,
                'lifetime': lifetime,
                'hue': random.random()
            })
        
        # Draw and update pulsar rings
        new_rings = []
        for ring in self.pulsar_rings:
            ring['radius'] += ring['growth_rate']
            ring['life'] -= 0.01
            
            if ring['life'] <= 0 or ring['radius'] > max(width, height):
                continue
                
            # Draw the ring
            radius = ring['radius']
            thickness = ring['thickness']
            segments = ring['segments']
            
            # Get color based on mode
            if self.color_mode == 0:  # Rainbow mode
                hue = (ring['hue'] + hue_offset) % 1.0
            elif self.color_mode == 1:  # Monochrome mode
                hue = hue_offset
            else:  # Complementary mode
                hue = (hue_offset + 0.5 * (ring['hue'] > 0.5)) % 1.0
                
            sat = 0.8
            val = 0.6 + 0.4 * ring['life']
            color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
            
            # Draw different ring types
            if segments > 0:
                # Segmented ring
                segment_angle = 2 * math.pi / segments
                for i in range(segments):
                    start_angle = i * segment_angle
                    arc_length = segment_angle * 0.7  # 70% of segment is drawn
                    
                    for t in range(int(arc_length * 100)):
                        angle = start_angle + t * arc_length / 100
                        
                        for r in range(thickness):
                            current_radius = radius - r
                            x = center_x + current_radius * math.cos(angle)
                            y = center_y + current_radius * math.sin(angle)
                            
                            if 0 <= x < width and 0 <= y < height:
                                try:
                                    stdscr.addstr(int(y), int(x), "*", color_attr)
                                except:
                                    pass
            else:
                # Continuous ring with optional wave
                steps = int(2 * math.pi * radius)
                
                for i in range(0, steps, max(1, int(steps / 150))):
                    angle = i * 2 * math.pi / steps
                    
                    # Add wave effect
                    wave_radius = ring['wave_amp'] * math.sin(angle * ring['wave_freq'] + self.time * 2)
                    current_radius = radius + wave_radius
                    
                    if self.symmetry > 0:
                        # Apply rotational symmetry
                        for sym in range(self.symmetry):
                            sym_angle = angle + sym * (2 * math.pi / self.symmetry)
                            
                            for r in range(thickness):
                                r_offset = current_radius - r
                                x = center_x + r_offset * math.cos(sym_angle)
                                y = center_y + r_offset * math.sin(sym_angle)
                                
                                if 0 <= x < width and 0 <= y < height:
                                    try:
                                        stdscr.addstr(int(y), int(x), "*", color_attr)
                                    except:
                                        pass
                    else:
                        # No symmetry - simple ring
                        for r in range(thickness):
                            r_offset = current_radius - r
                            x = center_x + r_offset * math.cos(angle)
                            y = center_y + r_offset * math.sin(angle)
                            
                            if 0 <= x < width and 0 <= y < height:
                                try:
                                    stdscr.addstr(int(y), int(x), "*", color_attr)
                                except:
                                    pass
            
            new_rings.append(ring)
        
        self.pulsar_rings = new_rings
        
        # Draw and update gravity wells
        new_wells = []
        for well in self.gravity_wells:
            well['life'] -= 1.0 / well['lifetime']
            
            if well['life'] <= 0:
                continue
                
            # Draw the gravity well
            x, y = int(well['x']), int(well['y'])
            
            # Well appearance based on strength
            intensity = well['life'] * well['strength']
            chars = ['·', '∘', '○', '◎', '●']
            char_idx = min(len(chars) - 1, int(intensity * len(chars)))
            
            # Color based on current mode
            if self.color_mode == 0:
                hue = (well['hue'] + hue_offset) % 1.0
            elif self.color_mode == 1:
                hue = hue_offset
            else:
                hue = (hue_offset + 0.5) % 1.0
                
            sat = 0.7
            val = 0.5 + 0.5 * intensity
            color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
            
            # Draw gravity well if in bounds
            if 0 <= x < width and 0 <= y < height:
                try:
                    stdscr.addstr(y, x, chars[char_idx], color_attr | curses.A_BOLD)
                    
                    # Draw a fading glow around the well
                    for r in range(1, 3):
                        for dx in range(-r, r + 1):
                            for dy in range(-r, r + 1):
                                dist = math.sqrt(dx*dx + dy*dy)
                                if r - 0.5 <= dist <= r + 0.5:
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < width and 0 <= ny < height:
                                        glow_val = val * (1 - dist / 3)
                                        glow_attr = self.hsv_to_color_pair(stdscr, hue, sat, glow_val)
                                        try:
                                            stdscr.addstr(ny, nx, '·', glow_attr)
                                        except:
                                            pass
                except:
                    pass
                    
            new_wells.append(well)
            
        self.gravity_wells = new_wells
        
        # Update and draw orbital particles
        for particle in self.orbital_particles:
            # Update orbital position
            particle['angle'] += particle['orbital_speed'] * (1 + energy * 0.5)
            
            # Calculate base position in orbit
            base_x = center_x + particle['radius'] * math.cos(particle['angle'])
            base_y = center_y + particle['radius'] * math.sin(particle['angle'])
            
            # Apply influence from gravity wells
            dx, dy = 0, 0
            for well in self.gravity_wells:
                well_vector_x = well['x'] - base_x
                well_vector_y = well['y'] - base_y
                dist = max(0.1, math.sqrt(well_vector_x**2 + well_vector_y**2))
                
                # Inverse square law for gravity
                force = well['strength'] * well['life'] / (dist * dist) * 2
                
                # Apply force to movement
                dx += well_vector_x / dist * force
                dy += well_vector_y / dist * force
            
            # Apply current spectrum data to particle motion
            if len(spectrum) > 0:
                freq_idx = int(particle['hue'] * len(spectrum))
                freq_energy = spectrum[freq_idx % len(spectrum)]
                
                # Add some spectrum-based movement
                dx += random.uniform(-1, 1) * freq_energy * 0.5
                dy += random.uniform(-1, 1) * freq_energy * 0.5
            
            # Final position
            x = base_x + dx
            y = base_y + dy
            
            # Draw particle if in bounds
            if 0 <= x < width and 0 <= y < height:
                # Get color based on mode
                if self.color_mode == 0:
                    hue = (particle['hue'] + hue_offset) % 1.0
                elif self.color_mode == 1:
                    hue = hue_offset
                else:
                    hue = (hue_offset + 0.5 * (particle['hue'] > 0.5)) % 1.0
                    
                sat = 0.7
                val = 0.7
                color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                
                try:
                    stdscr.addstr(int(y), int(x), particle['size'], color_attr)
                except:
                    pass
        
        # Draw the pulsar core
        core_radius = 2 + energy * 3
        core_intensity = 0.5 + energy * 0.5
        
        # Draw core as a bright spot at center
        for r in range(int(core_radius)):
            char = '·' if r > core_radius / 2 else '*'
            intensity = core_intensity * (1 - r / core_radius)
            color_attr = self.hsv_to_color_pair(stdscr, hue_offset, 0.3, intensity)
            
            try:
                # Draw horizontally and vertically
                for x_offset in [-r, r]:
                    if 0 <= center_x + x_offset < width:
                        stdscr.addstr(center_y, center_x + x_offset, char, color_attr | curses.A_BOLD)
                
                for y_offset in [-r, r]:
                    if 0 <= center_y + y_offset < height:
                        stdscr.addstr(center_y + y_offset, center_x, char, color_attr | curses.A_BOLD)
                        
                # Draw diagonals
                if r > 0:
                    for diag in [(-r, -r), (-r, r), (r, -r), (r, r)]:
                        dx, dy = diag
                        if 0 <= center_x + dx < width and 0 <= center_y + dy < height:
                            stdscr.addstr(center_y + dy, center_x + dx, char, color_attr)
            except:
                pass
                
        # Draw center point
        try:
            stdscr.addstr(center_y, center_x, "O", self.hsv_to_color_pair(stdscr, hue_offset, 0.0, 1.0) | curses.A_BOLD)
        except:
            pass
            
    def handle_keypress(self, key):
        if key == 'c':  # Cycle color modes
            self.color_mode = (self.color_mode + 1) % 3
            return True
        elif key == 't':  # Lower energy threshold
            self.energy_threshold = max(0.1, self.energy_threshold - 0.1)
            return True
        elif key == 'T':  # Raise energy threshold
            self.energy_threshold = min(0.9, self.energy_threshold + 0.1)
            return True
        elif key == 'd':  # Increase ring density
            self.ring_density = min(3.0, self.ring_density + 0.2)
            return True
        elif key == 'D':  # Decrease ring density
            self.ring_density = max(0.2, self.ring_density - 0.2)
            return True
        elif key == 's':  # Change symmetry
            self.symmetry = (self.symmetry + 1) % 9  # 0, 1, 2, 3, 4, 5, 6, 7, 8
            if self.symmetry == 1:  # Skip 1 as it's same as 0
                self.symmetry = 2
            return True
        return False