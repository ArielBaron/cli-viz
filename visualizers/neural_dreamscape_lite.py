# visualizers/neural_dreamscape_lite.py
import curses
import numpy as np
import random
import math
from visualizer_base import VisualizerBase

class NeuralDreamscapeLiteVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Neural Dreamscape Lite")
        # Neural field
        self.field = None
        self.energy_field = None
        
        # Dynamic state
        self.evolution_speed = 0.0
        self.time_counter = 0
        self.last_beat_time = 0
        self.consciousness_level = 0.0
        self.beat_memory = [0] * 8  # Remember last 8 beats for patterns
        self.color_mode = 0  # Different color modes
        self.particle_mode = 0  # Different particle behaviors
        
        # Rendering options
        self.symbols = "·•○★✧♦◆❅✺"  # More interesting symbols
        self.active_neurons = {}
        self.synapses = []
        self.special_particles = []
        
        # User controls
        self.density = 0.5  # Controls visualization density
        self.show_info = True
    
    def setup(self):
        # Will initialize fields when we know the screen dimensions
        pass
    
    def handle_keypress(self, key):
        """Handle visualization-specific key commands"""
        if key == 'c':
            # Cycle through color modes
            self.color_mode = (self.color_mode + 1) % 3
            return True
        elif key == 'p':
            # Cycle through particle modes
            self.particle_mode = (self.particle_mode + 1) % 3
            return True
        elif key == 'd':
            # Toggle density
            self.density = 1.0 if self.density < 0.7 else 0.5
            return True
        elif key == 'i':
            # Toggle info display
            self.show_info = not self.show_info
            return True
        elif key == 'b':
            # Create a burst of activity
            self.trigger_burst()
            return True
        return False
        
    def trigger_burst(self):
        """Create a burst of neural activity"""
        ds_height, ds_width = self.field.shape
        center_y, center_x = ds_height // 2, ds_width // 2
        
        # Create a burst of neurons in a circular pattern
        for i in range(12):  # Add 12 neurons in a circle
            angle = 2 * math.pi * i / 12
            dist = min(ds_width, ds_height) // 4
            y = int(center_y + dist * math.sin(angle))
            x = int(center_x + dist * math.cos(angle))
            
            if 0 <= x < ds_width and 0 <= y < ds_height:
                # Create neuron with random properties
                self.active_neurons[(y, x)] = {
                    'strength': random.uniform(0.8, 1.0),
                    'hue': (i / 12.0 + self.time_counter / 100) % 1.0,
                    'pulse_rate': random.uniform(0.1, 0.3),
                    'age': 0,
                    'type': random.randint(0, 2)  # Different neuron types
                }
                
                # Add energy
                self.energy_field[y, x] = 1.0
                
                # Create special particle
                self.special_particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * 0.5,
                    'vy': math.sin(angle) * 0.5,
                    'life': 30,
                    'hue': (i / 12.0 + 0.5) % 1.0,
                    'size': random.uniform(0.7, 1.3)
                })
        
        # Connect the neurons with synapses
        neurons = list(self.active_neurons.keys())
        for i in range(len(neurons)):
            if i > 0:  # Connect each neuron to the previous one
                start = neurons[i]
                end = neurons[i-1]
                self.synapses.append({
                    'start': start,
                    'end': end,
                    'strength': 0.9,
                    'active': 0.5
                })
        
    def initialize_fields(self, height, width):
        # Only initialize if needed or dimensions changed
        if (self.field is None or 
            self.field.shape[0] != height//2 or 
            self.field.shape[1] != width//2):
            
            # Downsample dimensions for performance
            ds_height = height // 2
            ds_width = width // 2
            
            # Neural activity field - use downsampled dimensions
            self.field = np.zeros((ds_height, ds_width), dtype=float)
            
            # Energy propagation field - use downsampled dimensions
            self.energy_field = np.zeros((ds_height, ds_width), dtype=float)
            
            # Active neurons (coordinate -> properties)
            self.active_neurons = {}
            
            # Neural connections - reduced count
            self.synapses = []
            
            # Special particles
            self.special_particles = []
            
            # Seed initial activity
            self.seed_initial_activity(ds_height, ds_width)
    
    def seed_initial_activity(self, height, width):
        # Create fewer initial neurons in a simple pattern
        neuron_count = int(min(width, height) * 0.1)  # Reduced count
        
        # Create some neurons in a spiral pattern for more interest
        center_x, center_y = width // 2, height // 2
        
        for i in range(neuron_count):
            # Spiral pattern
            angle = 0.5 * i
            radius = 2 + (i / neuron_count) * min(width, height) // 3
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            if 0 <= x < width and 0 <= y < height:
                # Create a neuron with random properties
                self.active_neurons[(y, x)] = {
                    'strength': random.uniform(0.5, 1.0),
                    'hue': (i / neuron_count) % 1.0,  # Different colors along spiral
                    'pulse_rate': random.uniform(0.05, 0.2),
                    'age': 0,
                    'type': random.randint(0, 2)  # Different neuron types
                }
                
                # Add some random energy to the energy field
                self.energy_field[y, x] = random.uniform(0.5, 1.0)
        
        # Create fewer synaptic connections
        for i in range(neuron_count // 2):  # Reduced count
            neurons = list(self.active_neurons.keys())
            if len(neurons) >= 2:
                start = random.choice(neurons)
                end = random.choice(neurons)
                if start != end:
                    self.synapses.append({
                        'start': start,
                        'end': end,
                        'strength': random.uniform(0.3, 1.0),
                        'active': 0.0
                    })
    
    def update_neural_field(self, spectrum, energy, height, width):
        # Increase time counter
        self.time_counter += 1
        
        # Calculate neural parameters based on audio - with more frequency bands
        bass = np.mean(spectrum[:6]) * 2  
        mid_low = np.mean(spectrum[6:12])
        mid_high = np.mean(spectrum[12:20])
        treble = np.mean(spectrum[20:])
        
        # Beat detection with memory
        current_time = self.time_counter
        beat_detected = False
        
        # Shift beat memory and add new value
        if current_time - self.last_beat_time > 10:
            if energy > 0.3:
                beat_detected = True
                self.last_beat_time = current_time
                self.beat_memory = [1.0] + self.beat_memory[:-1]
            else:
                self.beat_memory = [0.0] + self.beat_memory[:-1]
        
        # Calculate rhythm pattern strength - how regular are the beats?
        rhythm_pattern = 0
        for i in range(4):
            if i < len(self.beat_memory)-1:
                # Check if adjacent beat timings are similar
                rhythm_pattern += self.beat_memory[i] * self.beat_memory[i+1]
        
        # Consciousness represents treble vs bass balance
        consciousness_target = treble / (bass + 0.01)  # Avoid division by zero
        self.consciousness_level = self.consciousness_level * 0.95 + consciousness_target * 0.05
            
        # Create neurons on beat - more variety based on which frequencies are strong
        if beat_detected:
            # Determine neuron generation approach based on dominant frequency
            dominant = max(bass, mid_low, mid_high, treble)
            
            if dominant == bass:
                # Bass creates neurons in center
                center_y, center_x = height // 2, width // 2
                radius = int(min(width, height) * 0.15)
                count = int(3 * energy)
                
                for _ in range(count):
                    angle = random.random() * 2 * math.pi
                    dist = random.random() * radius
                    y = int(center_y + dist * math.sin(angle))
                    x = int(center_x + dist * math.cos(angle))
                    
                    if 0 <= x < width and 0 <= y < height:
                        self.active_neurons[(y, x)] = {
                            'strength': random.uniform(0.7, 1.0) * energy,
                            'hue': (0.0 + self.time_counter / 100) % 1.0,  # Reddish
                            'pulse_rate': random.uniform(0.05, 0.15),  # Slower pulse
                            'age': 0,
                            'type': 0  # Bass type
                        }
                        self.energy_field[y, x] = energy
                
            elif dominant == mid_low or dominant == mid_high:
                # Mids create neurons in a line pattern
                count = int(4 * energy)
                step = width // (count + 1)
                
                for i in range(count):
                    x = (i + 1) * step
                    y = height // 2 + int((random.random() - 0.5) * height * 0.3)
                    
                    if 0 <= x < width and 0 <= y < height:
                        self.active_neurons[(y, x)] = {
                            'strength': random.uniform(0.6, 0.9) * energy,
                            'hue': (0.3 + self.time_counter / 100) % 1.0,  # Greenish
                            'pulse_rate': random.uniform(0.1, 0.2),
                            'age': 0,
                            'type': 1  # Mid type
                        }
                        self.energy_field[y, x] = energy
            
            else:  # treble
                # Treble creates neurons around edges
                count = int(5 * energy)
                
                for _ in range(count):
                    # Choose edge
                    edge = random.randint(0, 3)
                    if edge == 0:  # Top
                        x = random.randint(0, width-1)
                        y = random.randint(0, height//5)
                    elif edge == 1:  # Right
                        x = random.randint(width*4//5, width-1)
                        y = random.randint(0, height-1)
                    elif edge == 2:  # Bottom
                        x = random.randint(0, width-1)
                        y = random.randint(height*4//5, height-1)
                    else:  # Left
                        x = random.randint(0, width//5)
                        y = random.randint(0, height-1)
                    
                    if 0 <= x < width and 0 <= y < height:
                        self.active_neurons[(y, x)] = {
                            'strength': random.uniform(0.8, 1.0) * energy,
                            'hue': (0.6 + self.time_counter / 100) % 1.0,  # Bluish
                            'pulse_rate': random.uniform(0.15, 0.25),  # Faster pulse
                            'age': 0,
                            'type': 2  # Treble type
                        }
                        self.energy_field[y, x] = energy
            
            # Create special particle
            for _ in range(int(energy * 3)):
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                angle = random.random() * 2 * math.pi
                
                self.special_particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * 0.7,
                    'vy': math.sin(angle) * 0.7,
                    'life': random.randint(20, 40),
                    'hue': random.random(),
                    'size': random.uniform(0.5, 1.5)
                })
        
        # Neural death based on age and low energy - different lifespans for different types
        neurons_to_remove = []
        for pos, neuron in self.active_neurons.items():
            neuron['age'] += 1
            
            # Death conditions - vary by type
            max_age = 40 if neuron['type'] == 0 else 60 if neuron['type'] == 1 else 80
            death_chance = 0.08 if neuron['type'] == 0 else 0.05 if neuron['type'] == 1 else 0.03
            
            if (neuron['age'] > max_age and random.random() < death_chance) or \
               (neuron['strength'] < 0.1):
                neurons_to_remove.append(pos)
        
        # Remove dead neurons
        for pos in neurons_to_remove:
            del self.active_neurons[pos]
        
        # Create synapses occasionally based on frequency content
        synapse_chance = treble * 0.1 + mid_high * 0.05
        if random.random() < synapse_chance and len(self.active_neurons) > 2:
            neurons = list(self.active_neurons.keys())
            start = random.choice(neurons)
            
            # Find a nearby neuron to connect to
            potential_ends = []
            for end in neurons:
                if start != end:
                    y1, x1 = start
                    y2, x2 = end
                    dist = math.sqrt((y2-y1)**2 + (x2-x1)**2)
                    if dist < width//4:  # Only connect to nearby neurons
                        potential_ends.append((end, dist))
            
            if potential_ends:
                # Sort by distance and pick one of the closest
                potential_ends.sort(key=lambda x: x[1])
                end = potential_ends[min(2, len(potential_ends)-1)][0]
                
                self.synapses.append({
                    'start': start,
                    'end': end,
                    'strength': random.uniform(0.3, 1.0),
                    'active': 0.0
                })
        
        # Remove old synapses
        self.synapses = [s for s in self.synapses if s['strength'] > 0.2]
        
        # Update energy field - improved diffusion
        # Process a subset of points each frame in a more strategic pattern
        new_energy = np.zeros_like(self.energy_field)
        
        # Process points in a grid pattern that changes each frame
        grid_size = 4  # Process every 4th point
        offset_y = self.time_counter % grid_size
        offset_x = (self.time_counter // 2) % grid_size
        
        for y in range(offset_y, height, grid_size):
            for x in range(offset_x, width, grid_size):
                # Safely get neighbors
                neighbors = []
                neighbor_count = 0
                
                for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        neighbors.append(self.energy_field[ny, nx])
                        neighbor_count += 1
                
                if neighbor_count > 0:
                    # Average of neighbors
                    avg = sum(neighbors) / neighbor_count
                    new_energy[y, x] = avg * 0.8 + self.energy_field[y, x] * 0.1
        
        # Apply energy decay
        self.energy_field = self.energy_field * 0.9
        # Add new diffused energy where calculated
        for y in range(offset_y, height, grid_size):
            for x in range(offset_x, width, grid_size):
                if new_energy[y, x] > 0:
                    self.energy_field[y, x] += new_energy[y, x] * 0.1
        
        # Add energy from active neurons - different patterns based on type
        for (y, x), neuron in self.active_neurons.items():
            if 0 <= y < height and 0 <= x < width:
                # Simple pulse with neuron type variation
                if neuron['type'] == 0:  # Bass type - strong central pulse
                    pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                    self.energy_field[y, x] += neuron['strength'] * pulse * 0.3
                    
                elif neuron['type'] == 1:  # Mid type - wave pattern
                    pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                    
                    # Add energy in a small radius
                    radius = 2
                    for dy in range(-radius, radius+1):
                        for dx in range(-radius, radius+1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < height and 0 <= nx < width:
                                dist = math.sqrt(dy*dy + dx*dx)
                                if dist <= radius:
                                    energy_val = (1 - dist/radius) * pulse * neuron['strength'] * 0.1
                                    self.energy_field[ny, nx] += energy_val
                
                else:  # Treble type - sparking pattern
                    # Random sparks
                    if random.random() < 0.2:
                        # Choose a random direction
                        angle = random.random() * 2 * math.pi
                        dist = random.randint(1, 3)
                        spark_y = int(y + dist * math.sin(angle))
                        spark_x = int(x + dist * math.cos(angle))
                        
                        if 0 <= spark_y < height and 0 <= spark_x < width:
                            self.energy_field[spark_y, spark_x] += neuron['strength'] * 0.4
        
        # Add energy from bass frequencies in a more interesting pattern
        if bass > 0.2:
            center_y, center_x = height // 2, width // 2
            
            # Create ripple pattern
            ripple_count = int(bass * 8)
            for i in range(ripple_count):
                radius = (i / ripple_count) * min(width, height) * 0.4 * bass
                points_to_add = int(min(2 * math.pi * radius, 20))  # Points proportional to circumference
                
                for j in range(points_to_add):
                    angle = 2 * math.pi * j / points_to_add
                    y = int(center_y + radius * math.sin(angle))
                    x = int(center_x + radius * math.cos(angle))
                    
                    if 0 <= y < height and 0 <= x < width:
                        energy_val = (1 - i/ripple_count) * bass * 0.3
                        self.energy_field[y, x] += energy_val
        
        # Update special particles
        new_particles = []
        for particle in self.special_particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Age the particle
            particle['life'] -= 1
            
            # Add energy where particles are
            py, px = int(particle['y']), int(particle['x'])
            if 0 <= py < height and 0 <= px < width:
                self.energy_field[py, px] += 0.3 * particle['size']
            
            # Keep if still alive and on screen
            if (particle['life'] > 0 and 
                0 <= particle['x'] < width and 
                0 <= particle['y'] < height):
                # Modify velocity based on particle mode
                if self.particle_mode == 1:  # Swirling mode
                    # Add circular motion
                    speed = math.sqrt(particle['vx']**2 + particle['vy']**2)
                    angle = math.atan2(particle['vy'], particle['vx']) + 0.1  # Rotate
                    particle['vx'] = math.cos(angle) * speed
                    particle['vy'] = math.sin(angle) * speed
                elif self.particle_mode == 2:  # Chaotic mode
                    # Random jitter
                    particle['vx'] += (random.random() - 0.5) * 0.2
                    particle['vy'] += (random.random() - 0.5) * 0.2
                    # Limit speed
                    speed = math.sqrt(particle['vx']**2 + particle['vy']**2)
                    if speed > 1.0:
                        particle['vx'] /= speed
                        particle['vy'] /= speed
                
                new_particles.append(particle)
        
        self.special_particles = new_particles
        
        # Update synapse activity based on neuron activity - improved for more visual interest
        for synapse in self.synapses:
            start_pos = synapse['start']
            end_pos = synapse['end']
            
            if start_pos in self.active_neurons and end_pos in self.active_neurons:
                start_neuron = self.active_neurons[start_pos]
                end_neuron = self.active_neurons[end_pos]
                
                # Synapse activation based on both neurons
                start_pulse = (math.sin(self.time_counter * start_neuron['pulse_rate']) + 1) / 2
                activation = start_neuron['strength'] * start_pulse * synapse['strength']
                
                # Synapse activity affected by neuron types
                if start_neuron['type'] == end_neuron['type']:
                    # Same type - stronger connection
                    activation *= 1.5
                
                # Smooth activation change
                synapse['active'] = 0.7 * synapse['active'] + 0.3 * activation
                
                # Transfer energy - now with pulse wave effect along synapse
                y1, x1 = start_pos
                y2, x2 = end_pos
                
                # Calculate length
                length = max(abs(y2-y1), abs(x2-x1))
                pulse_pos = (self.time_counter * 0.1) % 1.0  # Position of pulse along synapse
                
                # Only transfer at a few points for performance
                num_points = min(length, 3)
                for i in range(num_points):
                    t = i / max(1, num_points-1)
                    y = int(y1 + (y2-y1) * t)
                    x = int(x1 + (x2-x1) * t)
                    
                    # Pulse intensity based on distance from pulse position
                    pulse_dist = abs(t - pulse_pos)
                    pulse_intensity = max(0, 1 - pulse_dist * 5)  # Narrow pulse
                    
                    if 0 <= y < height and 0 <= x < width:
                        self.energy_field[y, x] += synapse['active'] * 0.05 * (1 + pulse_intensity)
            else:
                # One of the connected neurons died, weaken synapse
                synapse['strength'] *= 0.8
    
    def get_display_color(self, x, y, energy_val, hue_offset):
        """Get color based on current color mode"""
        if self.color_mode == 0:  # Normal color mode - position based
            point_hue = ((x + y) / 40 + hue_offset) % 1.0
            sat = 0.7 + 0.3 * min(1.0, energy_val * 2)
            val = min(1.0, 0.5 + 0.5 * min(1.0, energy_val * 2))
            return point_hue, sat, val
            
        elif self.color_mode == 1:  # Energy based coloring
            # Energy determines hue
            point_hue = (energy_val * 0.7 + hue_offset) % 1.0
            sat = 0.8
            val = min(1.0, 0.5 + 0.5 * min(1.0, energy_val * 2))
            return point_hue, sat, val
            
        else:  # Complementary color mode
            # Base hue varies with position but in a different pattern
            point_hue = ((x * y) / 1000 + hue_offset) % 1.0
            # Higher energy points get complementary color
            if energy_val > 0.5:
                point_hue = (point_hue + 0.5) % 1.0
            sat = 0.7 + 0.3 * min(1.0, energy_val * 2)
            val = min(1.0, 0.5 + 0.5 * min(1.0, energy_val * 2))
            return point_hue, sat, val
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Initialize fields if needed
        self.initialize_fields(height, width)
        
        # Get downsampled dimensions
        ds_height = height // 2
        ds_width = width // 2
        
        # Update the neural state based on audio
        self.update_neural_field(spectrum, energy, ds_height, ds_width)
        
        # Get bass and treble energy for color modulation
        bass = np.mean(spectrum[:6]) * 2
        mid_low = np.mean(spectrum[6:12])
        mid_high = np.mean(spectrum[12:20])
        treble = np.mean(spectrum[20:])
        
        # Clear the screen first
        stdscr.clear()
        
        # Draw title information bar - with more info based on show_info setting
        if self.show_info:
            title = f"Neural Dreamscape Lite | Energy: {energy:.2f} | Color: {self.color_mode} | Particles: {self.particle_mode} | Density: {self.density:.1f}"
            controls = "[C]olor [P]articles [D]ensity [B]urst [I]nfo"
        else:
            title = "Neural Dreamscape Lite"
            controls = ""
        
        title_color = self.hsv_to_color_pair(stdscr, hue_offset, 1.0, 1.0)
        stdscr.addstr(0, max(0, width//2 - len(title)//2), title, title_color | curses.A_BOLD)
        
        if controls:
            controls_color = self.hsv_to_color_pair(stdscr, (hue_offset + 0.3) % 1.0, 0.8, 0.9)
            try:
                stdscr.addstr(height-1, max(0, width - len(controls) - 2), controls, controls_color)
            except curses.error:
                pass
        
        # Draw the neural field - with density control and improved visuals
        # Calculate how many points to sample based on density setting
        points_to_draw = min(ds_height * ds_width * self.density, 300)  # Cap for performance
        
        # Sample points to draw
        sampled_points = []
        
        # Strategic sampling:
        # 1. Always include points with high energy
        # 2. Always include active neurons
        # 3. Fill remaining quota with random sampling
        
        # First add high energy points
        for y in range(ds_height):
            for x in range(ds_width):
                if self.energy_field[y, x] > 0.5:  # High energy threshold
                    sampled_points.append((y, x))
                    
                    # Stop if we've reached our quota
                    if len(sampled_points) >= points_to_draw:
                        break
            if len(sampled_points) >= points_to_draw:
                break
        
        # Add active neurons if not already included
        for (y, x) in self.active_neurons.keys():
            if (y, x) not in sampled_points and len(sampled_points) < points_to_draw:
                sampled_points.append((y, x))
        
        # Fill remaining quota with random sampling
        remaining = points_to_draw - len(sampled_points)
        if remaining > 0:
            # Create a list of all possible points not already sampled
            all_points = [(y, x) for y in range(ds_height) for x in range(ds_width) 
                          if (y, x) not in sampled_points and self.energy_field[y, x] > 0.1]
            
            # Random sample from remaining points
            if all_points:
                random_samples = random.sample(all_points, min(remaining, len(all_points)))
                sampled_points.extend(random_samples)
        
        # Draw sampled points
        for ds_y, ds_x in sampled_points:
            # Upscale to screen coordinates
            y = ds_y * 2
            x = ds_x * 2
            
            # Skip if out of bounds
            if not (0 <= y < height-2 and 0 <= x < width):
                continue
            
            # Get value from downsampled field
            energy_val = self.energy_field[ds_y, ds_x]
            
            # Skip drawing empty space
            if energy_val < 0.1:
                continue
            
            # Calculate intensity
            intensity = min(1.0, energy_val * 2)
            
            # Get color based on current color mode
            hue, sat, val = self.get_display_color(ds_x, ds_y, energy_val, hue_offset)
            
            # Get color
            color = self.hsv_to_color_pair(stdscr, hue, sat, val)
            
            # Choose character based on intensity and mode
            idx = min(len(self.symbols)-1, int(intensity * len(self.symbols)))
            char = self.symbols[idx]
            
            # Apply bold for higher intensity
            attrs = curses.A_BOLD if intensity > 0.7 else 0
            
            # Draw the character
            try:
                stdscr.addstr(y+1, x, char, color | attrs)
            except curses.error:
                pass
        
        # Draw active neural connections (synapses) - more visually interesting
        active_synapses = [s for s in self.synapses if s['active'] > 0.1]
        sample_size = min(len(active_synapses), int(15 * self.density))  # More with higher density
        
        if sample_size > 0:
            for synapse in random.sample(active_synapses, sample_size):
                ds_y1, ds_x1 = synapse['start']
                ds_y2, ds_x2 = synapse['end']
                
                # Upscale to screen coordinates
                y1, x1 = ds_y1 * 2, ds_x1 * 2
                y2, x2 = ds_y2 * 2, ds_x2 * 2
                
                # Calculate distance to determine how many points to draw
                distance = math.sqrt((y2-y1)**2 + (x2-x1)**2)
                steps = min(int(distance / 2) + 1, 5)  # More points for longer synapses
                
                # Pulse wave effect along synapses
                pulse_pos = (self.time_counter * 0.1) % 1.0  # Position of pulse (0-1)
                
                for i in range(steps):
                    t = i / (steps - 1) if steps > 1 else 0.5
                    y = int(y1 + (y2-y1) * t)
                    x = int(x1 + (x2-x1) * t)
                    
                    # Skip if out of bounds
                    if not (0 <= y < height-2 and 0 <= x < width):
                        continue
                    
                    # Calculate pulse intensity - brightest at pulse position
                    pulse_dist = abs(t - pulse_pos)
                    pulse_intensity = max(0, 1 - pulse_dist * 3)  # Narrower pulse = more visible movement
                    
                    # Determine synapse appearance
                    intensity = synapse['active'] * (0.6 + 0.4 * pulse_intensity)
                    
                    # Skip dim points
                    if intensity < 0.2:
                        continue
                    
                    # Calculate synapse color - based on color mode
                    if self.color_mode == 0:
                        hue = (0.6 + hue_offset + pulse_intensity * 0.2) % 1.0  # Bluish with pulse highlight
                    elif self.color_mode == 1:
                        hue = (0.0 + hue_offset + intensity * 0.3) % 1.0  # Reddish intensity
                    else:
                        hue = (0.85 + hue_offset) % 1.0  # Purple
                    
                    color = self.hsv_to_color_pair(stdscr, hue, 0.8, 0.7 + 0.3 * intensity)
                    
                    # Choose character based on pulse position
                    chars = "·•+*❃"
                    char_idx = min(len(chars)-1, int((intensity + pulse_intensity) * 0.7 * len(chars)))
                    char = chars[char_idx]
                    
                    try:
                        attrs = curses.A_BOLD if pulse_intensity > 0.5 else 0
                        stdscr.addstr(y+1, x, char, color | attrs)
                    except curses.error:
                        pass
        
        # Draw active neurons (cell bodies) - with type differentiation
        active_neurons = list(self.active_neurons.items())
        sample_size = min(len(active_neurons), int(30 * self.density))  # More with higher density
        
        if sample_size > 0:
            for (ds_y, ds_x), neuron in random.sample(active_neurons, sample_size):
                # Upscale to screen coordinates
                y, x = ds_y * 2, ds_x * 2
                
                if 0 <= y < height-2 and 0 <= x < width:
                    # Calculate neuron pulse
                    pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                    intensity = neuron['strength'] * (0.7 + 0.3 * pulse)
                    
                    # Skip dim neurons
                    if intensity < 0.2:
                        continue
                    
                    # Calculate color - based on neuron type and color mode
                    if self.color_mode == 0:
                        # Type-based coloring
                        base_hue = 0.0 if neuron['type'] == 0 else 0.3 if neuron['type'] == 1 else 0.6
                        neuron_hue = (base_hue + hue_offset + pulse * 0.1) % 1.0
                    elif self.color_mode == 1:
                        # Intensity-based coloring
                        neuron_hue = (intensity * 0.8 + hue_offset) % 1.0
                    else:
                        # Position-based with complementary pulses
                        neuron_hue = ((ds_x * ds_y) / 1000 + hue_offset) % 1.0
                        if pulse > 0.7:
                            neuron_hue = (neuron_hue + 0.5) % 1.0
                    
                    neuron_sat = 0.8 + 0.2 * pulse
                    neuron_val = 0.7 + 0.3 * intensity
                    
                    color = self.hsv_to_color_pair(stdscr, neuron_hue, neuron_sat, neuron_val)
                    
                    # Draw the neuron - different symbols based on type and intensity
                    try:
                        if neuron['type'] == 0:  # Bass type
                            char = "★" if intensity > 0.7 else "✧"
                        elif neuron['type'] == 1:  # Mid type
                            char = "❅" if intensity > 0.7 else "♦"
                        else:  # Treble type
                            char = "✺" if intensity > 0.7 else "◆"
                            
                        stdscr.addstr(y+1, x, char, color | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Draw special particles - with different behaviors based on particle mode
        for particle in self.special_particles:
            # Convert to screen coordinates
            y = int(particle['y'] * 2)
            x = int(particle['x'] * 2)
            
            if 0 <= y < height-2 and 0 <= x < width:
                # Calculate fade based on lifetime
                fade = particle['life'] / 40.0  # Normalize to 0-1
                
                # Calculate color based on particle mode
                if self.particle_mode == 0:  # Normal mode
                    hue = (particle['hue'] + hue_offset) % 1.0
                    sat = 0.9
                    val = 0.7 * fade + 0.3
                elif self.particle_mode == 1:  # Swirling mode - color changes with direction
                    angle = math.atan2(particle['vy'], particle['vx'])
                    hue = ((angle / (2 * math.pi)) + hue_offset) % 1.0
                    sat = 0.9
                    val = 0.8 * fade + 0.2
                else:  # Chaotic mode - rapid color changes
                    hue = ((particle['hue'] + self.time_counter * 0.03) % 1.0 + hue_offset) % 1.0
                    sat = 0.9
                    val = 0.8 * fade + 0.2
                
                color = self.hsv_to_color_pair(stdscr, hue, sat, val)
                
                # Character based on particle size and mode
                if self.particle_mode == 0:
                    char = "✧" if particle['size'] > 1.0 else "•"
                elif self.particle_mode == 1:
                    char = "✺" if particle['size'] > 1.0 else "✧"
                else:
                    chars = "•✧✺★✦"
                    idx = int((self.time_counter + particle['life']) * 0.1) % len(chars)
                    char = chars[idx]
                
                try:
                    stdscr.addstr(y+1, x, char, color | curses.A_BOLD)
                except curses.error:
                    pass
        
        # Draw enhanced consciousness wave at the bottom - with reactive design
        consciousness_bar = ""
        consciousness_width = min(width - 1, 60)  # Reasonable width for performance
        
        # Determine pattern based on audio characteristics
        if bass > treble * 1.5:  # Bass dominant
            pattern = "▁▂▃▄▅▆▇█"  # Blocky pattern
            wave_hue = (0.0 + hue_offset) % 1.0  # Red
        elif treble > bass * 1.5:  # Treble dominant
            pattern = "∿⌇⌇∿⌇⌇∿"  # Wavy pattern
            wave_hue = (0.6 + hue_offset) % 1.0  # Blue
        else:  # Balanced
            pattern = "▁▄▂▇▃█▅▆"  # Mixed pattern
            wave_hue = (0.3 + hue_offset) % 1.0  # Green
        
        # Generate the bar
        for x in range(consciousness_width):
            # Create wave pattern with more variation
            wave_val = 0.5 + 0.5 * math.sin(x / 5 + self.time_counter * 0.1)
            beat_factor = sum(self.beat_memory) / len(self.beat_memory)  # How regular the beats are
            intensity = (wave_val * self.consciousness_level) + (beat_factor * 0.3)
            
            # Choose symbol based on intensity
            if intensity < 0.3:
                idx = 0
            else:
                idx = min(len(pattern) - 1, int(intensity * len(pattern)))
            bar_char = pattern[idx]
                
            consciousness_bar += bar_char
        
        # Draw the consciousness wave
        wave_color = self.hsv_to_color_pair(stdscr, wave_hue, 0.8, 0.9)
        try:
            stdscr.addstr(height-1, 0, consciousness_bar, wave_color)
        except curses.error:
            # Fallback if there's an issue
            try:
                stdscr.addstr(height-1, 0, consciousness_bar[:-1], wave_color)
            except curses.error:
                pass