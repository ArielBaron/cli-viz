# visualizers/guitar_tuner.py
import curses
import math
import numpy as np
from visualizer_base import VisualizerBase

class GuitarTunerVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Guitar Tuner")
        # Standard guitar tuning frequencies (E2, A2, D3, G3, B3, E4)
        self.guitar_strings = {
            'E2': 82.41,
            'A2': 110.00,
            'D3': 146.83,
            'G3': 196.00,
            'B3': 246.94,
            'E4': 329.63
        }
        self.selected_string = 'E2'  # Default selected string
        self.string_names = list(self.guitar_strings.keys())
        self.string_index = 0
        self.needle_position = 0.5  # Centered position
        self.needle_momentum = 0
        self.accuracy = 0  # How close to target frequency (0-1)
        self.animation_frames = 0
        
    def setup(self):
        pass
        
    def get_string_frequency(self, spectrum, target_freq):
        """Find the strongest frequency near the target frequency"""
        # Convert target frequency to FFT bin index
        # Assuming spectrum length is related to sample rate
        # Typical FFT bin calculation: bin = freq * N / sample_rate
        # We make an educated guess about the mapping
        spectrum_length = len(spectrum)
        bin_width = 5  # Crude approximation, may need adjustment based on actual FFT params
        
        # Find the bin closest to our target frequency
        target_bin = int(target_freq / bin_width)
        if target_bin >= spectrum_length:
            return 0
            
        # Search around this bin for the strongest peak
        search_range = 5  # Look 5 bins in each direction
        start_bin = max(0, target_bin - search_range)
        end_bin = min(spectrum_length - 1, target_bin + search_range)
        
        # Find the strongest bin in the range
        strongest_bin = start_bin
        for i in range(start_bin, end_bin + 1):
            if spectrum[i] > spectrum[strongest_bin]:
                strongest_bin = i
                
        # Convert bin back to frequency
        actual_freq = strongest_bin * bin_width
        
        # Calculate how close we are to the target
        freq_diff = abs(actual_freq - target_freq)
        max_diff = target_freq * 0.1  # Allow 10% deviation
        accuracy = max(0, 1 - (freq_diff / max_diff))
        
        return actual_freq, accuracy
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Update animation counter
        self.animation_frames += 1
        
        # Get current guitar string and its target frequency
        current_string = self.string_names[self.string_index]
        target_freq = self.guitar_strings[current_string]
        
        # Get current detected frequency and accuracy
        detected_freq, accuracy = self.get_string_frequency(spectrum, target_freq)
        self.accuracy = accuracy
        
        # Calculate needle movement (with some physics for natural movement)
        target_position = 0.5 + (detected_freq - target_freq) / (target_freq * 0.1) * 0.5
        target_position = max(0, min(1, target_position))  # Clamp between 0 and 1
        
        # Add some "physics" to the needle movement
        self.needle_momentum = self.needle_momentum * 0.8 + (target_position - self.needle_position) * 0.2
        self.needle_position += self.needle_momentum
        self.needle_position = max(0.1, min(0.9, self.needle_position))  # Limit movement range
        
        # Draw tuner background
        middle_y = height // 2
        
        # Draw tuner name and instructions
        title = f"《 GUITAR TUNER - {current_string} ({target_freq:.2f} Hz) 》"
        instructions = "← → : Change String | Space : Auto-Tune"
        stdscr.addstr(2, (width - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(height - 2, (width - len(instructions)) // 2, instructions)
        
        # Draw tuner body
        tuner_width = min(width - 10, 80)
        tuner_height = 12
        tuner_start_x = (width - tuner_width) // 2
        tuner_start_y = middle_y - tuner_height // 2
        
        # Draw tuner outline
        for y in range(tuner_start_y, tuner_start_y + tuner_height):
            # Left edge
            stdscr.addstr(y, tuner_start_x, "│")
            # Right edge
            stdscr.addstr(y, tuner_start_x + tuner_width - 1, "│")
        
        # Draw top and bottom edges
        stdscr.addstr(tuner_start_y, tuner_start_x, "┌" + "─" * (tuner_width - 2) + "┐")
        stdscr.addstr(tuner_start_y + tuner_height - 1, tuner_start_x, "└" + "─" * (tuner_width - 2) + "┘")
        
        # Draw tick marks for the meter
        meter_y = tuner_start_y + 5
        for i in range(tuner_width - 6):
            x_pos = tuner_start_x + 3 + i
            x_ratio = i / (tuner_width - 7)
            if abs(x_ratio - 0.5) < 0.01:  # Center mark
                tick = "┼"
                label = "IN TUNE"
                stdscr.addstr(meter_y + 2, x_pos - len(label) // 2, label)
            elif abs(x_ratio - 0.25) < 0.01 or abs(x_ratio - 0.75) < 0.01:
                tick = "┴"
            elif abs(x_ratio - 0) < 0.01 or abs(x_ratio - 1) < 0.01:
                tick = "┴"
                label = "FLAT" if x_ratio < 0.1 else "SHARP"
                stdscr.addstr(meter_y + 2, x_pos - len(label) // 2, label)
            else:
                tick = "╌"
            
            # Color the ticks based on position
            if x_ratio < 0.4:  # Too flat - red zone
                color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)
            elif x_ratio > 0.6:  # Too sharp - red zone
                color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)
            elif 0.45 < x_ratio < 0.55:  # In tune - green zone
                color = self.hsv_to_color_pair(stdscr, 0.33, 0.8, 0.9)
            else:  # Slightly off - yellow zone
                color = self.hsv_to_color_pair(stdscr, 0.15, 0.8, 0.9)
                
            stdscr.addstr(meter_y, x_pos, tick, color)
        
        # Draw frequency readout
        freq_str = f"Detected: {detected_freq:.2f} Hz"
        stdscr.addstr(tuner_start_y + 8, (width - len(freq_str)) // 2, freq_str)
        
        # Calculate needle position
        needle_x = int(tuner_start_x + 3 + (tuner_width - 7) * self.needle_position)
        
        # Draw the needle
        for i in range(1, 5):
            needle_char = "█" if i < 4 else "▼"
            
            # Calculate color based on accuracy
            if accuracy > 0.95:  # In tune - green
                color = self.hsv_to_color_pair(stdscr, 0.33, 0.8, 0.9)
            elif accuracy > 0.8:  # Close - yellow
                color = self.hsv_to_color_pair(stdscr, 0.15, 0.8, 0.9)
            else:  # Off - red
                color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)
                
            stdscr.addstr(meter_y - i, needle_x, needle_char, color | curses.A_BOLD)
        
        # Draw guitar strings visualization (animated)
        string_y = tuner_start_y + tuner_height + 2
        string_length = tuner_width - 4
        string_start_x = tuner_start_x + 2
        
        # Draw all six strings
        for i, string_name in enumerate(self.guitar_strings.keys()):
            # Highlight the selected string
            is_selected = string_name == current_string
            
            # Calculate string thickness (thicker for lower strings)
            if i < 2:  # E, A (thickest)
                string_char = "═"
            elif i < 4:  # D, G (medium)
                string_char = "─"
            else:  # B, E (thinnest)
                string_char = "╌"
                
            # Calculate string vibration based on energy and accuracy
            if is_selected:
                vibration_amplitude = (1 - accuracy) * 4 + energy * 3
                wave_speed = 0.2 + (1 - accuracy) * 0.3
                
                # Draw vibrating string (sine wave)
                for x in range(string_length):
                    x_pos = string_start_x + x
                    x_ratio = x / string_length
                    
                    # Create a standing wave pattern with some dynamics
                    phase = self.animation_frames * wave_speed
                    wave1 = math.sin(x_ratio * math.pi * 2 + phase) * vibration_amplitude
                    wave2 = math.sin(x_ratio * math.pi * 4 - phase * 0.7) * vibration_amplitude * 0.5
                    y_offset = round(wave1 + wave2)
                    
                    # Draw the string segment with color based on accuracy
                    if accuracy > 0.95:
                        color = self.hsv_to_color_pair(stdscr, 0.33, 0.8, 0.9)
                    elif accuracy > 0.8:
                        color = self.hsv_to_color_pair(stdscr, 0.15, 0.8, 0.9)
                    else:
                        color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)
                        
                    y_pos = string_y + i * 2 + y_offset
                    if 0 <= y_pos < height:
                        stdscr.addstr(y_pos, x_pos, string_char, color | curses.A_BOLD)
            else:
                # Draw straight string (not vibrating)
                color = curses.A_NORMAL
                stdscr.addstr(string_y + i * 2, string_start_x, string_char * string_length, color)
            
            # Draw string name
            name_color = curses.A_BOLD if is_selected else curses.A_NORMAL
            stdscr.addstr(string_y + i * 2, string_start_x - 2, string_name, name_color)
            
        # Draw tuning indicator if in tune
        if accuracy > 0.95:
            tune_msg = "•• IN TUNE ••"
            blink = (self.animation_frames // 5) % 2 == 0
            color = self.hsv_to_color_pair(stdscr, 0.33, 0.9, 1.0)
            if blink:
                stdscr.addstr(tuner_start_y + 10, (width - len(tune_msg)) // 2, tune_msg, color | curses.A_BOLD | curses.A_BLINK)
            else:
                stdscr.addstr(tuner_start_y + 10, (width - len(tune_msg)) // 2, tune_msg, color | curses.A_BOLD)
    
    def handle_keypress(self, key):
        if key == curses.KEY_RIGHT or key == 'd':
            # Move to next string
            self.string_index = (self.string_index + 1) % len(self.string_names)
            self.selected_string = self.string_names[self.string_index]
            return True
        elif key == curses.KEY_LEFT or key == 'a':
            # Move to previous string
            self.string_index = (self.string_index - 1) % len(self.string_names)
            self.selected_string = self.string_names[self.string_index]
            return True
        elif key == ' ':
            # Auto-tune feature (just visual feedback for now)
            self.needle_position = 0.5
            self.accuracy = 1.0
            return True
        return False