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
        
        # Rendering options
        self.symbols = "·•○★✧♦"  # Reduced symbol set
        self.active_neurons = {}
        self.synapses = []
    
    def setup(self):
        # Will initialize fields when we know the screen dimensions
        pass
        
    def initialize_fields(self, height, width):
        # Only initialize if needed or dimensions changed
        if (self.field is None or 
            self.field.shape[0] != height-2 or 
            self.field.shape[1] != width):
            
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
            
            # Seed initial activity
            self.seed_initial_activity(ds_height, ds_width)
    
    def seed_initial_activity(self, height, width):
        # Create fewer initial neurons in a simple pattern
        neuron_count = int(min(width, height) * 0.1)  # Reduced count
        
        # Create some neurons in a circular pattern
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 4
        
        for i in range(neuron_count):
            angle = 2 * math.pi * i / neuron_count
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            if 0 <= x < width and 0 <= y < height:
                # Create a neuron with random properties
                self.active_neurons[(y, x)] = {
                    'strength': random.uniform(0.5, 1.0),
                    'hue': random.random(),
                    'pulse_rate': random.uniform(0.05, 0.2),
                    'age': 0
                }
                
                # Add some random energy to the energy field
                self.energy_field[y, x] = random.uniform(0.5, 1.0)
        
        # Create fewer synaptic connections
        for i in range(len(self.active_neurons)):  # Reduced count
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
        
        # Calculate neural parameters based on audio - simplified
        bass = np.mean(spectrum[:5]) * 2  # Reduced frequency bands
        treble = np.mean(spectrum[15:])   # Reduced frequency bands
        
        # Beat detection
        current_time = self.time_counter
        beat_detected = False
        
        # Consciousness represents treble vs bass balance
        consciousness_target = treble / (bass + 0.01)  # Avoid division by zero
        self.consciousness_level = self.consciousness_level * 0.95 + consciousness_target * 0.05
        
        # Check for beats (energy spikes) - simplified
        if energy > 0.3 and current_time - self.last_beat_time > 10:
            beat_detected = True
            self.last_beat_time = current_time
            
            # Create neurons on beat
            for _ in range(2):  # Reduced count
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                
                self.active_neurons[(y, x)] = {
                    'strength': random.uniform(0.5, 1.0) * energy,
                    'hue': (bass + treble) % 1.0,
                    'pulse_rate': random.uniform(0.05, 0.2),
                    'age': 0
                }
                
                # Add energy
                self.energy_field[y, x] = energy
        
        # Neural death based on age and low energy - simplified
        neurons_to_remove = []
        for pos, neuron in self.active_neurons.items():
            neuron['age'] += 1
            
            # Death conditions
            if (neuron['age'] > 50 and random.random() < 0.05) or \
               (neuron['strength'] < 0.1):
                neurons_to_remove.append(pos)
        
        # Remove dead neurons
        for pos in neurons_to_remove:
            del self.active_neurons[pos]
        
        # Create synapses occasionally (reduced frequency)
        if random.random() < treble * 0.1 and len(self.active_neurons) > 2:
            neurons = list(self.active_neurons.keys())
            start = random.choice(neurons)
            end = random.choice(neurons)
            if start != end:
                self.synapses.append({
                    'start': start,
                    'end': end,
                    'strength': random.uniform(0.3, 1.0),
                    'active': 0.0
                })
        
        # Remove old synapses
        self.synapses = [s for s in self.synapses if s['strength'] > 0.2]
        
        # Update energy field - simplified diffusion
        # Only process a subset of points each frame to reduce CPU
        new_energy = np.zeros_like(self.energy_field)
        points_to_process = min(height * width // 4, 100)  # Limit points to process
        
        for _ in range(points_to_process):
            y = random.randint(1, height-2)
            x = random.randint(1, width-2)
            # Average of neighbors
            new_energy[y, x] = (
                self.energy_field[y-1, x] + 
                self.energy_field[y+1, x] + 
                self.energy_field[y, x-1] + 
                self.energy_field[y, x+1]
            ) * 0.2 + self.energy_field[y, x] * 0.1
        
        # Apply energy decay
        self.energy_field = self.energy_field * 0.9
        self.energy_field += new_energy * 0.1
        
        # Add energy from active neurons
        for (y, x), neuron in self.active_neurons.items():
            if 0 <= y < height and 0 <= x < width:
                # Simple pulse
                pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                self.energy_field[y, x] += neuron['strength'] * pulse * 0.2
        
        # Add energy from bass frequencies - simplified
        if bass > 0.2:
            center_y, center_x = height // 2, width // 2
            radius = int(min(width, height) * 0.2 * bass)
            points_to_add = min(radius * 4, 20)  # Limit points to add
            
            for _ in range(points_to_add):
                angle = random.random() * 2 * math.pi
                dist = random.random() * radius
                y = int(center_y + dist * math.sin(angle))
                x = int(center_x + dist * math.cos(angle))
                
                if 0 <= y < height and 0 <= x < width:
                    energy_val = (1 - dist/radius) * bass * 0.5
                    self.energy_field[y, x] += energy_val
        
        # Update synapse activity based on neuron activity - simplified
        for synapse in self.synapses:
            start_pos = synapse['start']
            end_pos = synapse['end']
            
            if start_pos in self.active_neurons and end_pos in self.active_neurons:
                start_neuron = self.active_neurons[start_pos]
                
                # Simple activation
                activation = start_neuron['strength'] * synapse['strength']
                
                # Smooth activation change
                synapse['active'] = 0.7 * synapse['active'] + 0.3 * activation
                
                # Transfer energy - simplified to just start and end points
                y1, x1 = start_pos
                y2, x2 = end_pos
                
                if 0 <= y1 < height and 0 <= x1 < width:
                    self.energy_field[y1, x1] += synapse['active'] * 0.05
                
                if 0 <= y2 < height and 0 <= x2 < width:
                    self.energy_field[y2, x2] += synapse['active'] * 0.05
            else:
                # One of the connected neurons died, weaken synapse
                synapse['strength'] *= 0.8
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Initialize fields if needed
        self.initialize_fields(height, width)
        
        # Get downsampled dimensions
        ds_height = height // 2
        ds_width = width // 2
        
        # Update the neural state based on audio
        self.update_neural_field(spectrum, energy, ds_height, ds_width)
        
        # Get bass and treble energy for color modulation
        bass = np.mean(spectrum[:5]) * 2
        treble = np.mean(spectrum[15:])
        
        # Clear the screen first
        stdscr.clear()
        
        # Draw title information bar - simplified
        title = f"Neural Dreamscape Lite | Energy: {energy:.2f}"
        title_color = self.hsv_to_color_pair(stdscr, hue_offset, 1.0, 1.0)
        stdscr.addstr(0, max(0, width//2 - len(title)//2), title, title_color | curses.A_BOLD)
        
        # Draw the neural field - optimized for low-end devices
        # Only draw a subset of points each frame
        # Use upscaling from downsampled field to original resolution
        points_to_draw = min(height * width // 6, 200)  # Limit points to draw
        
        # Draw energy field (randomly sample points)
        for _ in range(points_to_draw):
            ds_y = random.randint(0, ds_height-1)
            ds_x = random.randint(0, ds_width-1)
            
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
            
            # Calculate color
            point_hue = ((x / width + y / height) / 2 + hue_offset) % 1.0
            hue = (point_hue + bass * 0.1) % 1.0
            sat = 0.7 + 0.3 * intensity
            val = min(1.0, 0.5 + 0.5 * intensity)
            
            # Get color
            color = self.hsv_to_color_pair(stdscr, hue, sat, val)
            
            # Choose simpler character set
            idx = min(len(self.symbols)-1, int(intensity * len(self.symbols)))
            char = self.symbols[idx]
            
            # Apply bold for higher intensity
            attrs = curses.A_BOLD if intensity > 0.7 else 0
            
            # Draw the character
            try:
                stdscr.addstr(y+1, x, char, color | attrs)
            except curses.error:
                pass
        
        # Draw active neural connections (synapses) - simplified, draw fewer
        active_synapses = [s for s in self.synapses if s['active'] > 0.2]
        sample_size = min(len(active_synapses), 10)  # Limit number of synapses drawn
        
        if sample_size > 0:
            for synapse in random.sample(active_synapses, sample_size):
                ds_y1, ds_x1 = synapse['start']
                ds_y2, ds_x2 = synapse['end']
                
                # Upscale to screen coordinates
                y1, x1 = ds_y1 * 2, ds_x1 * 2
                y2, x2 = ds_y2 * 2, ds_x2 * 2
                
                # Draw just a few points along the synapse
                steps = 3  # Fixed small number
                
                for i in range(steps):
                    t = i / (steps - 1)
                    y = int(y1 + (y2-y1) * t)
                    x = int(x1 + (x2-x1) * t)
                    
                    # Skip if out of bounds
                    if not (0 <= y < height-2 and 0 <= x < width):
                        continue
                    
                    # Determine synapse appearance
                    intensity = synapse['active']
                    
                    # Calculate synapse color
                    hue = (0.6 + hue_offset) % 1.0
                    color = self.hsv_to_color_pair(stdscr, hue, 0.8, 0.8)
                    
                    try:
                        stdscr.addstr(y+1, x, "•", color | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Draw active neurons (cell bodies) - simplified
        active_neurons = list(self.active_neurons.items())
        sample_size = min(len(active_neurons), 20)  # Limit number of neurons drawn
        
        if sample_size > 0:
            for (ds_y, ds_x), neuron in random.sample(active_neurons, sample_size):
                # Upscale to screen coordinates
                y, x = ds_y * 2, ds_x * 2
                
                if 0 <= y < height-2 and 0 <= x < width:
                    # Calculate neuron pulse
                    pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                    intensity = neuron['strength'] * (0.7 + 0.3 * pulse)
                    
                    # Skip dim neurons
                    if intensity < 0.3:
                        continue
                    
                    # Calculate color
                    neuron_hue = (neuron['hue'] + hue_offset) % 1.0
                    color = self.hsv_to_color_pair(stdscr, neuron_hue, 0.8, 0.9)
                    
                    # Draw the neuron
                    try:
                        # Use simpler symbol
                        char = "○" if intensity > 0.6 else "•"
                        stdscr.addstr(y+1, x, char, color | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Draw simple consciousness wave at the bottom
        consciousness_bar = ""
        consciousness_width = min(width - 1, 40)  # Reduce width for performance
        
        for x in range(consciousness_width):
            # Create wave pattern
            wave_val = math.sin(x / 5 + self.time_counter * 0.05) * 0.5 + 0.5
            intensity = wave_val * self.consciousness_level
            
            if intensity < 0.3:
                bar_char = "░"
            else:
                bar_char = "▒"
                
            consciousness_bar += bar_char
        
        # Draw the consciousness wave
        wave_color = self.hsv_to_color_pair(stdscr, (hue_offset + 0.7) % 1.0, 0.8, 0.9)
        try:
            stdscr.addstr(height-1, 0, consciousness_bar, wave_color)
        except curses.error:
            pass