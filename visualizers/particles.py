# visualizers/particles.py
import curses
import random
from visualizer_base import VisualizerBase

class ParticlesVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Particles")
        self.particles = []
        self.max_particles = 100
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Particle system visualization
        
        # Create new particles based on audio energy
        if len(self.particles) < self.max_particles and energy > 0.1:
            spawn_count = int(energy * 10)
            for _ in range(spawn_count):
                # Create particle at the bottom center
                self.particles.append({
                    'x': width // 2 + random.randint(-10, 10),
                    'y': height - 5,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-5, -2),
                    'life': random.uniform(0.5, 1.0),
                    'hue': random.random(),
                    'size': random.choice(['.', '*', '+', '•', '○', '◌', '◦'])
                })
        
        # Update and draw particles
        new_particles = []
        for p in self.particles:
            # Update position
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravity
            p['life'] -= 0.02
            
            # If particle is still alive and on screen
            if p['life'] > 0 and 0 <= p['y'] < height - 1 and 0 <= p['x'] < width:
                # Draw particle
                x, y = int(p['x']), int(p['y'])
                
                # Color based on life and initial hue
                hue = (p['hue'] + hue_offset) % 1.0
                sat = 0.8
                val = 0.7 + 0.3 * p['life']
                
                # Get color pair and draw
                color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
                stdscr.addstr(y, x, p['size'], color_attr | curses.A_BOLD)
                
                # Keep this particle
                new_particles.append(p)
        
        # Update particle list
        self.particles = new_particles
    
    def handle_keypress(self, key):
        if key == 'p':
            self.max_particles = min(500, self.max_particles + 50)
            return True
        elif key == 'P':
            self.max_particles = max(50, self.max_particles - 50)
            return True
        return False