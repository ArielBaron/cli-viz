# visualizers/cosmic_pulsar.py
import curses
import random
import math
import numpy as np  # Import numpy for spectrum analysis
from visualizer_base import VisualizerBase

class CosmicPulsarVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Cosmic Pulsar Reactive")
        self.pulsar_rings = []
        self.energy_threshold = 0.3  # Lowered threshold for more frequent rings
        self.ring_density = 1.0
        self.color_mode = 0  # 0: rainbow, 1: monochrome, 2: complementary
        self.orbital_particles = []
        self.orbital_count = 80
        self.gravity_wells = []
        self.max_wells = 4 # Allow slightly more wells
        self.symmetry = 4  # Rotational symmetry
        self.bass_sensitivity = 15.0 # Multiplier for bass effects (thickness, well strength)
        self.mids_sensitivity = 10.0 # Multiplier for mid-range effects (waves)
        self.highs_sensitivity = 5.0 # Multiplier for high-range effects (waves)
        self.particle_brightness_factor = 2.5 # How much spectrum affects particle brightness

    def setup(self):
        self.time = 0
        self.pulsar_rings = []
        self.orbital_particles = []
        self.gravity_wells = []

        # Create initial orbital particles
        for i in range(self.orbital_count):
            angle = random.uniform(0, 2 * math.pi)
            base_radius = random.uniform(8, 20) # Store base radius
            orbital_speed = 0.02 + random.uniform(-0.01, 0.01)
            # Assign a frequency band index based on particle index
            # (Could also be random, but this gives some spatial distribution)
            freq_idx_rel = i / self.orbital_count
            self.orbital_particles.append({
                'angle': angle,
                'base_radius': base_radius,
                'current_radius': base_radius, # Add current radius for modulation
                'orbital_speed': orbital_speed,
                'size': random.choice(['*', '.', '+', '·', '•']),
                'freq_idx_rel': freq_idx_rel, # Relative position in spectrum (0 to 1)
                'hue': freq_idx_rel # Use frequency position for hue
            })

    def _get_freq_bands(self, spectrum, width):
        """Helper to get average energy in bass, mids, highs"""
        if len(spectrum) == 0:
            return 0, 0, 0

        # Define frequency band ranges (adjust as needed)
        # Use relative indices based on spectrum length
        spec_len = len(spectrum)
        bass_end = spec_len // 10
        mids_end = spec_len // 3

        bass = np.mean(spectrum[:bass_end]) if bass_end > 0 else 0
        mids = np.mean(spectrum[bass_end:mids_end]) if mids_end > bass_end else 0
        highs = np.mean(spectrum[mids_end:]) if spec_len > mids_end else 0

        # Apply sensitivities and clamp
        bass = min(1.0, bass * self.bass_sensitivity)
        mids = min(1.0, mids * self.mids_sensitivity)
        highs = min(1.0, highs * self.highs_sensitivity)

        return bass, mids, highs

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        center_x = width // 2
        center_y = height // 2
        self.time += 0.05
        max_dim = max(width, height)

        # Ensure spectrum is not empty before processing
        if len(spectrum) == 0:
            spectrum = np.zeros(1) # Avoid errors with empty spectrum

        # Get frequency band energies
        bass_energy, mids_energy, highs_energy = self._get_freq_bands(spectrum, width)

        # --- Subtle Background Shimmer ---
        if energy > 0.05: # Only draw if some sound
            bg_char = '.'
            # Vary brightness slightly with energy
            bg_val = min(0.3, energy * 0.5)
            # Slow color cycle for background
            bg_hue = (hue_offset * 0.1) % 1.0
            bg_sat = 0.1 + energy * 0.2 # Slightly more saturation with energy
            bg_attr = self.hsv_to_color_pair(stdscr, bg_hue, bg_sat, bg_val)
            # Draw sparsely
            for y_bg in range(0, height, 7): # Wider spacing
                for x_bg in range(0, width, 14):
                    # Add slight random positional jitter based on time
                    jitter_x = int(math.sin(self.time + x_bg * 0.1) * 1)
                    jitter_y = int(math.cos(self.time + y_bg * 0.1) * 1)
                    draw_x, draw_y = x_bg + jitter_x, y_bg + jitter_y
                    if 0 <= draw_x < width and 0 <= draw_y < height:
                        try:
                            # Random chance to draw based on energy
                            if random.random() < energy * 2.0:
                                stdscr.addch(draw_y, draw_x, bg_char, bg_attr)
                        except curses.error:
                            pass # Ignore errors at screen edges


        # --- Pulsar Ring Creation ---
        # Trigger more frequently based on energy peaks
        if energy > self.energy_threshold and random.random() < (energy - self.energy_threshold) * 1.5:
            ring_count = int(1 + energy * 2 * self.ring_density)
            for _ in range(ring_count):
                # Thickness based on bass energy
                thickness = max(1, min(4, 1 + int(bass_energy * 3)))
                # Wave amplitude based on highs, frequency based on mids
                wave_amplitude = highs_energy * 2.0
                wave_frequency = 4 + mids_energy * 8.0
                # Store energy at creation for brightness/saturation control
                initial_energy = energy

                self.pulsar_rings.append({
                    'radius': 1,
                    'growth_rate': 0.4 + energy * 1.2, # More variation in growth speed
                    'life': 1.0,
                    'thickness': thickness,
                    'hue': random.random(), # Keep random hue for variety
                    'wave_freq': wave_frequency,
                    'wave_amp': wave_amplitude,
                    'segments': random.randint(self.symmetry, self.symmetry * 3) if random.random() > 0.7 else 0,
                    'initial_energy': initial_energy
                })

        # --- Gravity Well Creation & Update ---
        # More likely to spawn on bass hits
        if len(self.gravity_wells) < self.max_wells and random.random() < (0.005 + energy * 0.01 + bass_energy * 0.08):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(max_dim * 0.1, max_dim * 0.3)
            lifetime = random.uniform(5, 15)
            base_strength = random.uniform(0.5, 2.0) # Store base strength

            self.gravity_wells.append({
                'x': center_x + distance * math.cos(angle),
                'y': center_y + distance * math.sin(angle),
                'base_strength': base_strength,
                'current_strength': base_strength, # Initialize current strength
                'life': 1.0,
                'lifetime': lifetime,
                'hue': random.random()
            })

        # Update existing gravity wells (pulsate strength with bass)
        new_wells = []
        for well in self.gravity_wells:
            well['life'] -= (1.0 / well['lifetime']) / 30.0 # Slower decay based on update rate (~30fps)
            # Pulsate strength with bass
            well['current_strength'] = well['base_strength'] * (0.8 + bass_energy * 1.5)

            if well['life'] > 0:
                new_wells.append(well)
        self.gravity_wells = new_wells

        # --- Draw Pulsar Rings ---
        new_rings = []
        for ring in self.pulsar_rings:
            ring['radius'] += ring['growth_rate']
            ring['life'] -= 0.015 # Slightly faster fade

            if ring['life'] <= 0 or ring['radius'] > max_dim * 1.5: # Allow going slightly off-screen
                continue

            radius = ring['radius']
            thickness = ring['thickness']
            segments = ring['segments'] # TODO: Implement drawing for segmented rings if needed

            # Color based on mode and initial energy
            brightness_factor = (ring['life'] * 0.4 + ring['initial_energy'] * 0.6) # Mix lifetime fade and creation energy
            brightness_factor = max(0, min(1.0, brightness_factor)) # Clamp

            if self.color_mode == 0:  # Rainbow
                hue = (ring['hue'] + hue_offset) % 1.0
            elif self.color_mode == 1:  # Monochrome
                hue = hue_offset
            else:  # Complementary
                hue = (hue_offset + 0.5 * (ring['hue'] > 0.5)) % 1.0

            # Saturation and Value linked to brightness_factor
            sat = 0.5 + 0.5 * brightness_factor
            val = 0.4 + 0.6 * brightness_factor
            color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)

            # --- Continuous Ring Drawing ---
            steps = max(10, int(2 * math.pi * radius)) # Ensure minimum steps
            # ** FIXED LINE BELOW **
            for i in range(0, steps, max(1, int(steps / (100 + mids_energy * 100)))): # Density slightly affected by mids
                angle = i * 2 * math.pi / steps

                # Add wave effect
                wave_offset = ring['wave_amp'] * math.sin(angle * ring['wave_freq'] + self.time * 3) # Faster wave time
                current_radius = radius + wave_offset

                # Apply rotational symmetry
                for sym in range(self.symmetry):
                    sym_angle = angle + sym * (2 * math.pi / self.symmetry)

                    for r_offset in range(thickness): # Draw thickness inward
                        r = current_radius - r_offset
                        if r <= 0: continue # Don't draw negative radius

                        x = center_x + r * math.cos(sym_angle)
                        y = center_y + r * math.sin(sym_angle)

                        if 0 <= x < width and 0 <= y < height:
                            try:
                                # Use different characters based on thickness/radius?
                                char = '*' if r_offset < thickness / 2 else '.'
                                stdscr.addstr(int(y), int(x), char, color_attr)
                            except curses.error:
                                pass # Ignore screen edge errors

            new_rings.append(ring)
        self.pulsar_rings = new_rings


        # --- Draw and Update Gravity Wells ---
        for well in self.gravity_wells:
            x, y = int(well['x']), int(well['y'])

            # Well appearance based on pulsating strength and life
            intensity = well['life'] * well['current_strength']
            chars = ['·', '∘', '○', '◎', '●']
            char_idx = min(len(chars) - 1, int(intensity * (len(chars) / 1.5))) # Scale index

            # Color based on current mode and intensity
            if self.color_mode == 0: hue = (well['hue'] + hue_offset) % 1.0
            elif self.color_mode == 1: hue = hue_offset
            else: hue = (hue_offset + 0.5) % 1.0
            sat = 0.6 + 0.4 * intensity # More saturation with intensity
            val = 0.4 + 0.6 * intensity # More brightness with intensity
            color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)

            if 0 <= x < width and 0 <= y < height:
                try:
                    stdscr.addstr(y, x, chars[char_idx], color_attr | curses.A_BOLD)

                    # Draw a fading glow, intensity based on well strength
                    glow_intensity = well['current_strength'] * well['life']
                    for r in range(1, 3):
                        glow_val = val * (1 - r / 3) * (0.5 + glow_intensity * 0.5) # Glow pulses
                        glow_attr = self.hsv_to_color_pair(stdscr, hue, sat * 0.8, max(0, min(1.0, glow_val)))
                        for dx in range(-r, r + 1):
                            for dy in range(-r, r + 1):
                                dist_sq = dx*dx + dy*dy
                                # Draw approx circle
                                if r*r - r < dist_sq <= r*r + r:
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < width and 0 <= ny < height:
                                        try:
                                            stdscr.addstr(ny, nx, '·', glow_attr)
                                        except curses.error: pass
                except curses.error: pass


        # --- Update and Draw Orbital Particles ---
        spec_len = len(spectrum)
        for particle in self.orbital_particles:
            # Update orbital speed based on overall energy
            particle['angle'] = (particle['angle'] + particle['orbital_speed'] * (1 + energy * 1.5)) % (2 * math.pi) # More speed variation

            # Get energy for this particle's frequency band
            freq_idx = int(particle['freq_idx_rel'] * (spec_len -1)) if spec_len > 0 else 0
            freq_energy = spectrum[freq_idx] if spec_len > 0 else 0

            # Modulate radius slightly based on frequency energy (push outward)
            radial_push = freq_energy * 2.0
            particle['current_radius'] = particle['base_radius'] * (1 + radial_push * 0.1) # Subtle radius change

            # Calculate base position
            base_x = center_x + particle['current_radius'] * math.cos(particle['angle'])
            base_y = center_y + particle['current_radius'] * math.sin(particle['angle'])

            # Apply influence from gravity wells
            final_x, final_y = base_x, base_y
            for well in self.gravity_wells:
                well_vector_x = well['x'] - final_x
                well_vector_y = well['y'] - final_y
                dist_sq = well_vector_x**2 + well_vector_y**2
                dist = math.sqrt(dist_sq) if dist_sq > 0.01 else 0.1

                # Use pulsating strength
                force = well['current_strength'] * well['life'] / dist_sq * 3 # Slightly stronger pull
                force = min(force, dist / 2) # Prevent excessive jumps

                final_x += well_vector_x / dist * force
                final_y += well_vector_y / dist * force

            # Draw particle if in bounds
            if 0 <= final_x < width and 0 <= final_y < height:
                # Color based on mode
                if self.color_mode == 0: hue = (particle['hue'] + hue_offset) % 1.0
                elif self.color_mode == 1: hue = hue_offset
                else: hue = (hue_offset + 0.5 * (particle['hue'] > 0.5)) % 1.0

                # Brightness (Value) based on frequency energy
                particle_val = 0.4 + freq_energy * self.particle_brightness_factor
                particle_val = max(0.1, min(1.0, particle_val)) # Clamp value
                particle_sat = 0.6 + freq_energy * 0.4 # Saturation also slightly affected
                particle_sat = max(0.2, min(1.0, particle_sat))

                color_attr = self.hsv_to_color_pair(stdscr, hue, particle_sat, particle_val)

                try:
                    # Maybe make size react slightly?
                    size = particle['size']
                    if freq_energy > 0.5: size = '#' # Use brighter char on high energy
                    stdscr.addstr(int(final_y), int(final_x), size, color_attr)
                except curses.error:
                    pass


        # --- Draw the Pulsar Core ---
        # More reactive size and intensity range
        core_radius = 1.0 + energy * 5.0
        core_intensity = 0.2 + energy * 0.8 # Wider brightness range
        core_intensity = max(0, min(1.0, core_intensity))

        core_hue = (hue_offset + bass_energy * 0.1) % 1.0 # Subtle hue shift with bass
        core_sat = 0.1 + energy * 0.5 # Saturation pulses with energy

        # Draw core as a bright, multi-layered spot
        for r_layer in range(int(core_radius), -1, -1): # Draw from outside in
            layer_radius = r_layer
            # Intensity falls off from center
            intensity_at_layer = core_intensity * max(0, 1 - (layer_radius / (core_radius + 1e-6)))**2
            if intensity_at_layer < 0.05: continue # Skip very dim layers

            char = '*' if layer_radius < core_radius / 2 else '+' if layer_radius < core_radius * 0.8 else '.'
            color_attr = self.hsv_to_color_pair(stdscr, core_hue, core_sat, intensity_at_layer)
            attr = curses.A_BOLD if layer_radius < core_radius / 3 else 0

            # Draw circle points for this layer
            steps = max(6, int(layer_radius * 4)) # More points for larger radii
            for i in range(steps):
                angle = i * 2 * math.pi / steps
                x = center_x + layer_radius * math.cos(angle)
                y = center_y + layer_radius * math.sin(angle)
                if 0 <= x < width and 0 <= y < height:
                    try:
                         stdscr.addstr(int(y), int(x), char, color_attr | attr)
                    except curses.error: pass

        # Draw center point ('O') - always visible
        try:
            center_color = self.hsv_to_color_pair(stdscr, core_hue, 0.0, 1.0) # Whiteish center
            stdscr.addstr(center_y, center_x, "O", center_color | curses.A_BOLD)
        except curses.error: pass


    def handle_keypress(self, key):
        if key == 'c':  # Cycle color modes
            self.color_mode = (self.color_mode + 1) % 3
            return True
        elif key == 't':  # Lower energy threshold
            self.energy_threshold = max(0.05, self.energy_threshold - 0.05)
            return True
        elif key == 'T':  # Raise energy threshold
            self.energy_threshold = min(0.9, self.energy_threshold + 0.05)
            return True
        elif key == 'd':  # Increase ring density
            self.ring_density = min(3.0, self.ring_density + 0.2)
            return True
        elif key == 'D':  # Decrease ring density
            self.ring_density = max(0.2, self.ring_density - 0.2)
            return True
        elif key == 's':  # Change symmetry
            current_sym = self.symmetry
            if current_sym == 0: self.symmetry = 2 # From none to 2
            elif current_sym == 8: self.symmetry = 0 # From 8 to none
            else: self.symmetry = current_sym + 1
            # Effectively cycles: 2, 3, 4, 5, 6, 7, 8, 0
            return True
        # Add keys to adjust sensitivity?
        # elif key == 'b': self.bass_sensitivity = max(1.0, self.bass_sensitivity - 1.0); return True
        # elif key == 'B': self.bass_sensitivity += 1.0; return True
        # elif key == 'm': self.mids_sensitivity = max(1.0, self.mids_sensitivity - 1.0); return True
        # elif key == 'M': self.mids_sensitivity += 1.0; return True
        # elif key == 'h': self.highs_sensitivity = max(1.0, self.highs_sensitivity - 1.0); return True
        # elif key == 'H': self.highs_sensitivity += 1.0; return True
        return False