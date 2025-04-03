# visualizers/neural_dreamscape.py
import curses
import numpy as np
import random
import math
from visualizer_base import VisualizerBase

class NeuralDreamscapeVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Neural Dreamscape")
        # Neural field
        self.field = None
        self.energy_field = None
        self.wave_field = None
        self.thought_particles = []
        
        # Dynamic state
        self.evolution_speed = 0.0
        self.last_beat_time = 0
        self.resonance = 0.0
        self.consciousness_level = 0.0
        self.dream_intensity = 0.0
        self.time_counter = 0
        
        # Rendering options
        self.symbols = "·•○◙★✧♦❂☼❈♠♣⚡✿❀⚘❄✺⚕"
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
            
            # Neural activity field
            self.field = np.zeros((height-2, width), dtype=float)
            
            # Energy propagation field
            self.energy_field = np.zeros((height-2, width), dtype=float)
            
            # Wave propagation field
            self.wave_field = np.zeros((height-2, width), dtype=float)
            
            # Active neurons (coordinate -> properties)
            self.active_neurons = {}
            
            # Neural connections
            self.synapses = []
            
            # Seed initial activity
            self.seed_initial_activity(height-2, width)
    
    def seed_initial_activity(self, height, width):
        # Create initial neurons in a pleasing pattern
        neuron_count = int(min(width, height) * 0.2)
        
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
        
        # Create some synaptic connections
        for i in range(len(self.active_neurons) * 3):
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
        
        # Calculate neural parameters based on audio
        bass = np.mean(spectrum[:10]) * 2
        mids = np.mean(spectrum[10:30])
        treble = np.mean(spectrum[30:])
        
        # Beat detection
        current_time = self.time_counter
        beat_detected = False
        
        # Energy affects evolution speed
        self.evolution_speed = 0.1 + energy * 0.4
        
        # Resonance represents harmonic balance
        target_resonance = mids + treble * 0.5
        self.resonance = self.resonance * 0.9 + target_resonance * 0.1
        
        # Consciousness represents treble vs bass balance
        consciousness_target = treble / (bass + 0.01)  # Avoid division by zero
        self.consciousness_level = self.consciousness_level * 0.95 + consciousness_target * 0.05
        
        # Dream intensity represents overall energy
        self.dream_intensity = self.dream_intensity * 0.9 + energy * 0.1
        
        # Check for beats (energy spikes)
        if energy > 0.25 and current_time - self.last_beat_time > 5:
            beat_detected = True
            self.last_beat_time = current_time
            
            # Strong beat - create thought particles
            thought_count = int(energy * 10)
            for _ in range(thought_count):
                # Create a thought particle at a random location
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                
                # Angle based on current position
                angle = math.atan2(y - height/2, x - width/2)
                
                self.thought_particles.append({
                    'x': x, 
                    'y': y,
                    'vx': math.cos(angle) * (0.5 + energy * 2),
                    'vy': math.sin(angle) * (0.5 + energy * 2),
                    'life': random.randint(10, 30),
                    'hue': random.random(),
                    'size': random.uniform(0.5, 1.5)
                })
                
                # Add energy to the wave field
                if 0 <= y < height and 0 <= x < width:
                    self.wave_field[y, x] = 1.0
        
        # Spontaneous neuron creation/deletion based on music
        if random.random() < 0.1 * energy:
            # Create new neurons
            for _ in range(int(energy * 5)):
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
        
        # Neural death based on age and low energy
        neurons_to_remove = []
        for pos, neuron in self.active_neurons.items():
            neuron['age'] += 1
            
            # Death conditions
            if (neuron['age'] > 100 and random.random() < 0.02) or \
               (neuron['strength'] < 0.1 and random.random() < 0.1):
                neurons_to_remove.append(pos)
        
        # Remove dead neurons
        for pos in neurons_to_remove:
            del self.active_neurons[pos]
        
        # Create synapses when certain frequencies are strong
        if random.random() < treble * 0.3:
            neurons = list(self.active_neurons.keys())
            if len(neurons) >= 2:
                start = random.choice(neurons)
                end = random.choice(neurons)
                if start != end:
                    self.synapses.append({
                        'start': start,
                        'end': end,
                        'strength': random.uniform(0.3, 1.0) * mids,
                        'active': 0.0
                    })
        
        # Remove old synapses
        self.synapses = [s for s in self.synapses if s['strength'] > 0.1]
        
        # Update energy field - diffusion
        new_energy = np.zeros_like(self.energy_field)
        
        # Simple diffusion kernel
        for y in range(1, height-1):
            for x in range(1, width-1):
                # Average of neighbors
                new_energy[y, x] = (
                    self.energy_field[y-1, x] + 
                    self.energy_field[y+1, x] + 
                    self.energy_field[y, x-1] + 
                    self.energy_field[y, x+1]
                ) * 0.23 + self.energy_field[y, x] * 0.08
        
        # Apply energy decay
        self.energy_field = new_energy * (0.95 + 0.05 * energy)
        
        # Add energy from active neurons
        for (y, x), neuron in self.active_neurons.items():
            if 0 <= y < height and 0 <= x < width:
                # Neurons pulse based on their pulse rate
                pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                self.energy_field[y, x] += neuron['strength'] * pulse * 0.2
        
        # Add energy from bass frequencies
        if bass > 0.2:
            center_y, center_x = height // 2, width // 2
            radius = int(min(width, height) * 0.3 * bass)
            
            for y in range(max(0, center_y-radius), min(height, center_y+radius)):
                for x in range(max(0, center_x-radius), min(width, center_x+radius)):
                    dist = math.sqrt((y-center_y)**2 + (x-center_x)**2)
                    if dist < radius:
                        # Add energy that decreases with distance from center
                        energy_val = (1 - dist/radius) * bass * 0.5
                        self.energy_field[y, x] += energy_val
        
        # Update wave field (ripple effect)
        new_wave = np.zeros_like(self.wave_field)
        
        # Wave propagation algorithm
        for y in range(1, height-1):
            for x in range(1, width-1):
                # Classic wave equation discretization
                new_wave[y, x] = (
                    self.wave_field[y-1, x] + 
                    self.wave_field[y+1, x] + 
                    self.wave_field[y, x-1] + 
                    self.wave_field[y, x+1]
                ) * 0.25 - self.wave_field[y, x]
                
                # Damping
                new_wave[y, x] *= 0.99
        
        self.wave_field = new_wave + self.wave_field * 0.5
        
        # Apply energy to wave field (energy causes waves)
        self.wave_field += self.energy_field * 0.03
        
        # Clamp wave field values
        self.wave_field = np.clip(self.wave_field, -1.0, 1.0)
        
        # Update thought particles
        new_thoughts = []
        for thought in self.thought_particles:
            # Update position
            thought['x'] += thought['vx']
            thought['y'] += thought['vy']
            
            # Age the thought
            thought['life'] -= 1
            
            # Add energy where thoughts are
            y, x = int(thought['y']), int(thought['x'])
            if 0 <= y < height and 0 <= x < width:
                self.energy_field[y, x] += 0.2 * thought['size']
                self.wave_field[y, x] += 0.1
            
            # Keep if still alive and on screen
            if (thought['life'] > 0 and 
                0 <= thought['x'] < width and 
                0 <= thought['y'] < height):
                new_thoughts.append(thought)
        
        self.thought_particles = new_thoughts
        
        # Update synapse activity based on neuron activity
        for synapse in self.synapses:
            start_pos = synapse['start']
            end_pos = synapse['end']
            
            if start_pos in self.active_neurons and end_pos in self.active_neurons:
                start_neuron = self.active_neurons[start_pos]
                
                # Synapse activation based on start neuron strength and pulse
                pulse = (math.sin(self.time_counter * start_neuron['pulse_rate']) + 1) / 2
                activation = start_neuron['strength'] * pulse * synapse['strength']
                
                # Smooth activation change
                synapse['active'] = 0.8 * synapse['active'] + 0.2 * activation
                
                # Transfer energy along synapse
                y1, x1 = start_pos
                y2, x2 = end_pos
                
                # Simple linear interpolation of points along the synapse
                steps = max(abs(y2-y1), abs(x2-x1)) + 1
                for i in range(steps):
                    t = i / steps
                    y = int(y1 + (y2-y1) * t)
                    x = int(x1 + (x2-x1) * t)
                    
                    if 0 <= y < height and 0 <= x < width:
                        self.energy_field[y, x] += synapse['active'] * 0.05
            else:
                # One of the connected neurons died, weaken synapse
                synapse['strength'] *= 0.9
    
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Initialize fields if needed
        self.initialize_fields(height, width)
        
        # Update the neural state based on audio
        self.update_neural_field(spectrum, energy, height-2, width)
        
        # Get bass, mid, and treble energy for color modulation
        bass = np.mean(spectrum[:10]) * 2
        mids = np.mean(spectrum[10:30])
        treble = np.mean(spectrum[30:])
        
        # Clear the screen first
        stdscr.clear()
        
        # Draw title information bar
        title = f"Neural Dreamscape | Consciousness: {self.consciousness_level:.2f} | Resonance: {self.resonance:.2f} | Energy: {energy:.2f}"
        title_color = self.hsv_to_color_pair(stdscr, hue_offset, 1.0, 1.0)
        stdscr.addstr(0, width//2 - len(title)//2, title, title_color | curses.A_BOLD)
        
        # Draw the neural field
        for y in range(height-2):
            for x in range(width):
                # Get total intensity from energy and wave fields
                energy_val = self.energy_field[y, x]
                wave_val = (self.wave_field[y, x] + 1) / 2  # Normalize to 0-1
                
                # Skip drawing empty space to improve performance
                if energy_val < 0.05 and wave_val < 0.1:
                    continue
                
                # Calculate display values
                intensity = min(1.0, energy_val * 2 + wave_val * 0.5)
                if intensity < 0.05:
                    continue
                
                # Calculate color
                # Base hue varies with position and offset
                point_hue = ((x / width + y / height) / 2 + hue_offset) % 1.0
                
                # Modulate hue based on audio frequencies
                hue = (point_hue + bass * 0.2 + mids * 0.1 + treble * 0.05) % 1.0
                
                # Saturation and value based on intensity
                sat = 0.7 + 0.3 * intensity
                val = min(1.0, 0.5 + 0.5 * intensity)
                
                # Get color
                color = self.hsv_to_color_pair(stdscr, hue, sat, val)
                
                # Choose character based on intensity and wave field
                idx = min(len(self.symbols)-1, int(intensity * len(self.symbols)))
                char = self.symbols[idx]
                
                # Apply bold for higher intensity
                attrs = curses.A_BOLD if intensity > 0.7 else 0
                
                # Draw the character
                try:
                    stdscr.addstr(y+1, x, char, color | attrs)
                except curses.error:
                    pass
        
        # Draw active neural connections (synapses)
        for synapse in self.synapses:
            if synapse['active'] > 0.1:
                y1, x1 = synapse['start']
                y2, x2 = synapse['end']
                
                # Draw more points for stronger connections
                steps = max(3, int(10 * synapse['active']))
                
                for i in range(steps):
                    t = i / (steps - 1)
                    y = int(y1 + (y2-y1) * t)
                    x = int(x1 + (x2-x1) * t)
                    
                    # Skip if out of bounds
                    if not (0 <= y < height-2 and 0 <= x < width):
                        continue
                    
                    # Calculate pulse effect along synapse
                    pulse_offset = (t + self.time_counter * 0.05) % 1.0
                    pulse_intensity = (math.sin(pulse_offset * 2 * math.pi) + 1) / 2
                    
                    # Determine synapse appearance
                    intensity = synapse['active'] * (0.5 + 0.5 * pulse_intensity)
                    
                    # Skip dim points
                    if intensity < 0.1:
                        continue
                    
                    # Calculate synapse color (bluish for inhibitory, reddish for excitatory)
                    base_hue = 0.6 if synapse['strength'] < 0.5 else 0.0
                    hue = (base_hue + hue_offset + pulse_offset * 0.2) % 1.0
                    sat = 0.8
                    val = 0.7 + 0.3 * intensity
                    
                    color = self.hsv_to_color_pair(stdscr, hue, sat, val)
                    
                    # Get character based on intensity
                    chars = "·•◦○●"
                    char_idx = min(len(chars)-1, int(intensity * len(chars)))
                    
                    try:
                        stdscr.addstr(y+1, x, chars[char_idx], color | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Draw active neurons (cell bodies)
        for (y, x), neuron in self.active_neurons.items():
            if 0 <= y < height-2 and 0 <= x < width:
                # Calculate neuron pulse
                pulse = (math.sin(self.time_counter * neuron['pulse_rate']) + 1) / 2
                intensity = neuron['strength'] * (0.7 + 0.3 * pulse)
                
                # Skip dim neurons
                if intensity < 0.2:
                    continue
                
                # Calculate color
                neuron_hue = (neuron['hue'] + hue_offset) % 1.0
                neuron_sat = 0.8 + 0.2 * pulse
                neuron_val = 0.7 + 0.3 * intensity
                
                color = self.hsv_to_color_pair(stdscr, neuron_hue, neuron_sat, neuron_val)
                
                # Draw the neuron
                try:
                    # Use different symbols based on neuron characteristics
                    if intensity > 0.8:
                        char = "❂"  # Highly active
                    elif intensity > 0.5:
                        char = "☼"  # Moderately active
                    else:
                        char = "○"  # Less active
                        
                    stdscr.addstr(y+1, x, char, color | curses.A_BOLD)
                except curses.error:
                    pass
        
        # Draw thought particles
        for thought in self.thought_particles:
            y, x = int(thought['y']), int(thought['x'])
            
            # Skip if out of bounds
            if not (0 <= y < height-2 and 0 <= x < width):
                continue
            
            # Calculate color
            thought_hue = (thought['hue'] + hue_offset) % 1.0
            thought_sat = 0.9
            thought_val = 0.8 * (thought['life'] / 30)
            
            color = self.hsv_to_color_pair(stdscr, thought_hue, thought_sat, thought_val)
            
            # Draw different characters based on thought size
            if thought['size'] > 1.0:
                char = "✺"
            else:
                char = "✧"
                
            try:
                stdscr.addstr(y+1, x, char, color | curses.A_BOLD)
            except curses.error:
                pass
        
        # Draw consciousness wave at the bottom - FIX: avoid the last column to prevent cursor error
        consciousness_bar = ""
        consciousness_width = width - 1  # Avoid the very last column
        
        for x in range(consciousness_width):
            # Create wave pattern
            wave_val = math.sin(x / 10 + self.time_counter * 0.1) * 0.5 + 0.5
            intensity = wave_val * self.consciousness_level
            
            if intensity < 0.2:
                bar_char = "░"
            elif intensity < 0.5:
                bar_char = "▒"
            else:
                bar_char = "█"
                
            consciousness_bar += bar_char
        
        # Draw the consciousness wave - safely avoiding the last position
        wave_color = self.hsv_to_color_pair(stdscr, (hue_offset + 0.7) % 1.0, 0.8, 0.9)
        try:
            stdscr.addstr(height-1, 0, consciousness_bar, wave_color)
        except curses.error:
            # Fallback if even the modified version has issues
            stdscr.addstr(height-1, 0, consciousness_bar[:-1], wave_color)