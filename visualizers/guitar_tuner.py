# visualizers/guitar_tuner.py
import curses
import math
import numpy as np
from visualizer_base import VisualizerBase
import time # Import time for the pulsing text example, if needed - though not used in this tuner

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
        # Crude approximation, assuming sample rate 44100 and chunk size used in main.py
        # bin = freq * N / sample_rate
        # N = self.CHUNK from main.py (2048)
        # sample_rate = self.RATE from main.py (44100)
        # This might need access to main.py's CHUNK/RATE or pass them during init/draw
        # For now, let's make a more educated guess based on typical params
        N = 2048 # Assuming CHUNK size from main.py - might need adjustment if this changes
        sample_rate = 44100 # Assuming RATE from main.py
        spectrum_length = len(spectrum) # Should be N // 2

        if spectrum_length == 0: return 0, 0 # Avoid division by zero

        bin_width = sample_rate / N # Frequency represented by each bin

        if bin_width == 0: return 0, 0 # Avoid division by zero

        # Find the bin closest to our target frequency
        target_bin = int(target_freq / bin_width)

        # Ensure target_bin is within valid range
        if target_bin >= spectrum_length or target_bin < 0:
            # Fallback: search the lower spectrum if target is too high/low for FFT resolution
             target_bin = min(max(0, target_bin), spectrum_length - 1)
             # return 0, 0 # Or handle this case differently

        # Search around this bin for the strongest peak
        # Search range should be relative to target freq (e.g., +/- 5%)
        search_radius_hz = target_freq * 0.10 # Search +/- 10% of target frequency
        search_radius_bins = int(search_radius_hz / bin_width)
        search_radius_bins = max(1, search_radius_bins) # Minimum search radius of 1 bin

        start_bin = max(0, target_bin - search_radius_bins)
        end_bin = min(spectrum_length - 1, target_bin + search_radius_bins)

        # Find the strongest bin in the range, weighted towards target bin if magnitudes are similar
        strongest_bin = target_bin # Default to target bin
        max_magnitude = 0
        if start_bin <= end_bin and 0 <= start_bin < spectrum_length: # Check range validity
             max_magnitude = spectrum[start_bin]
             strongest_bin = start_bin
             for i in range(start_bin, end_bin + 1):
                 if spectrum[i] > max_magnitude:
                     max_magnitude = spectrum[i]
                     strongest_bin = i

        # Convert bin back to frequency
        detected_freq = strongest_bin * bin_width

        # Calculate how close we are to the target
        # Use cents for more musical accuracy (100 cents per semitone)
        if detected_freq <= 0 or target_freq <= 0:
            accuracy = 0
            freq_diff_cents = 0
        else:
            freq_diff_cents = 1200 * math.log2(detected_freq / target_freq)

        # Define accuracy based on cents deviation (e.g., +/- 10 cents is good)
        max_diff_cents = 50 # Maximum deviation allowed (50 cents = quarter tone)
        accuracy = max(0, 1 - abs(freq_diff_cents / max_diff_cents))

        # Adjust target position based on cents difference
        # Map -max_diff_cents to 0, 0 to 0.5, +max_diff_cents to 1
        target_position = 0.5 + (freq_diff_cents / (2 * max_diff_cents))
        target_position = max(0, min(1, target_position)) # Clamp between 0 and 1

        return detected_freq, accuracy, target_position

    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Update animation counter
        self.animation_frames += 1

        # Get current guitar string and its target frequency
        current_string = self.string_names[self.string_index]
        target_freq = self.guitar_strings[current_string]

        # Get current detected frequency and accuracy
        detected_freq, accuracy, target_position = self.get_string_frequency(spectrum, target_freq)
        self.accuracy = accuracy

        # Add some "physics" to the needle movement
        # Target position is now calculated in get_string_frequency
        force = (target_position - self.needle_position) * 0.2 # Spring force
        damping = self.needle_momentum * -0.2 # Damping force
        self.needle_momentum += force + damping
        self.needle_momentum *= 0.85 # Air resistance / friction
        self.needle_position += self.needle_momentum

        # Clamp needle position after momentum update
        self.needle_position = max(0.05, min(0.95, self.needle_position)) # Limit movement slightly inside the meter

        # Draw tuner background
        middle_y = height // 2
        min_tuner_height = 16 # Ensure minimum height for all elements

        # Adaptive tuner height based on screen, but with a minimum
        tuner_height = max(min_tuner_height, height // 3 * 2)
        tuner_height = min(tuner_height, height - 6) # Ensure space for title/instructions

        # Center tuner vertically if possible
        tuner_start_y = max(3, (height - tuner_height) // 2) # Ensure space below title

        # Tuner width
        tuner_width = min(width - 4, 80) # Ensure padding
        tuner_start_x = (width - tuner_width) // 2

        # Ensure tuner fits
        if tuner_height < min_tuner_height or tuner_width < 20:
             stdscr.addstr(0, 0, "Terminal too small!")
             return # Stop drawing if too small

        # --- Draw UI Elements ---

        # Draw tuner name and instructions (check bounds)
        title = f"《 GUITAR TUNER - {current_string} ({target_freq:.2f} Hz) 》"
        instructions = "← → : Change String" # Removed Space: Auto-tune as it wasn't functional
        title_x = (width - len(title)) // 2
        instr_x = (width - len(instructions)) // 2
        if 2 < height and 0 <= title_x < width and title_x + len(title) <= width:
            stdscr.addstr(1, title_x, title, curses.A_BOLD) # Move title down slightly
        if height - 2 >= 0 and 0 <= instr_x < width and instr_x + len(instructions) <= width:
            stdscr.addstr(height - 2, instr_x, instructions)

        # Draw tuner outline
        meter_y = tuner_start_y + tuner_height // 4 # Position meter higher
        freq_y = meter_y + 3
        tune_msg_y = freq_y + 2
        string_display_start_y = tune_msg_y + 2 # Y pos where strings drawing starts

        # Top/Bottom borders
        if tuner_start_y < height and tuner_start_x + tuner_width <= width:
            stdscr.addstr(tuner_start_y, tuner_start_x, "┌" + "─" * (tuner_width - 2) + "┐")
        if tuner_start_y + tuner_height -1 < height and tuner_start_x + tuner_width <= width:
            stdscr.addstr(tuner_start_y + tuner_height - 1, tuner_start_x, "└" + "─" * (tuner_width - 2) + "┘")

        # Left/Right borders
        for y in range(tuner_start_y + 1, tuner_start_y + tuner_height - 1):
            if 0 <= y < height:
                if 0 <= tuner_start_x < width:
                     stdscr.addch(y, tuner_start_x, "│")
                if 0 <= tuner_start_x + tuner_width - 1 < width:
                     stdscr.addch(y, tuner_start_x + tuner_width - 1, "│")

        # Draw tick marks for the meter
        meter_width = tuner_width - 6 # Width of the scale inside the box
        meter_start_x = tuner_start_x + 3

        if 0 <= meter_y < height and 0 <= meter_y + 2 < height: # Check if meter area fits vertically
            for i in range(meter_width):
                x_pos = meter_start_x + i
                if not (0 <= x_pos < width): continue # Skip if horizontally out of bounds

                x_ratio = i / (meter_width -1) if meter_width > 1 else 0.5

                # Determine tick character and labels
                tick = "╌"
                label = ""
                label_y = meter_y + 2
                label_offset = 0
                is_center_mark = abs(x_ratio - 0.5) < 0.01
                is_quarter_mark = abs(x_ratio - 0.25) < 0.01 or abs(x_ratio - 0.75) < 0.01
                is_end_mark = abs(x_ratio - 0) < 0.01 or abs(x_ratio - 1) < 0.01

                if is_center_mark:
                    tick = "┼"
                    label = "IN TUNE"
                    label_offset = -len(label) // 2
                elif is_quarter_mark:
                    tick = "┴"
                elif is_end_mark:
                    tick = "┴"
                    label = "FLAT" if x_ratio < 0.1 else "SHARP"
                    label_offset = -len(label) // 2 if x_ratio < 0.1 else -len(label)//2 # Adjust label pos slightly


                # Color the ticks based on position (relative to center 0.5)
                if abs(x_ratio - 0.5) < 0.05: # In tune - green zone (5%)
                    color = self.hsv_to_color_pair(stdscr, 0.33, 0.8, 0.9)
                elif abs(x_ratio - 0.5) < 0.15: # Slightly off - yellow zone (15%)
                    color = self.hsv_to_color_pair(stdscr, 0.15, 0.8, 0.9)
                else: # Off - red zone
                    color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)

                stdscr.addstr(meter_y, x_pos, tick, color)
                if label:
                    label_x = x_pos + label_offset
                    if 0 <= label_x < width and label_x + len(label) <= width:
                        stdscr.addstr(label_y, label_x, label)

        # Draw frequency readout
        freq_str = f"Detected: {detected_freq:.2f} Hz"
        freq_x = (width - len(freq_str)) // 2
        if 0 <= freq_y < height and 0 <= freq_x < width and freq_x + len(freq_str) <= width:
             stdscr.addstr(freq_y, freq_x, freq_str)

        # Draw the needle
        needle_meter_width = tuner_width - 7 # Width available for needle travel
        needle_x = int(meter_start_x + needle_meter_width * self.needle_position)
        needle_x = max(meter_start_x, min(meter_start_x + needle_meter_width -1, needle_x)) # Clamp needle x

        # Determine needle color based on accuracy
        if accuracy > 0.9:  # In tune - green (+/- 5 cents)
            needle_color = self.hsv_to_color_pair(stdscr, 0.33, 0.9, 1.0)
        elif accuracy > 0.7:  # Close - yellow (+/- 15 cents)
            needle_color = self.hsv_to_color_pair(stdscr, 0.15, 0.9, 1.0)
        else:  # Off - red
            needle_color = self.hsv_to_color_pair(stdscr, 0.0, 0.9, 1.0)

        for i in range(1, 5): # Draw needle lines
             needle_char = "█" if i < 4 else "▼"
             needle_y = meter_y - i
             if 0 <= needle_y < height and 0 <= needle_x < width:
                 stdscr.addstr(needle_y, needle_x, needle_char, needle_color | curses.A_BOLD)

        # Draw tuning indicator if in tune
        if accuracy > 0.9: # Threshold for "IN TUNE" display
            tune_msg = "•• IN TUNE ••"
            blink = (self.animation_frames // 6) % 2 == 0 # Slower blink
            tune_msg_x = (width - len(tune_msg)) // 2
            if 0 <= tune_msg_y < height and 0 <= tune_msg_x < width and tune_msg_x + len(tune_msg) <= width:
                color = self.hsv_to_color_pair(stdscr, 0.33, 0.9, 1.0)
                attr = curses.A_BOLD | (curses.A_BLINK if blink else 0)
                stdscr.addstr(tune_msg_y, tune_msg_x, tune_msg, color | attr)

        # Draw guitar strings visualization
        string_display_height = tuner_start_y + tuner_height - string_display_start_y - 1
        num_strings = len(self.guitar_strings)
        vertical_spacing = 2 # Lines between strings

        # Check if there's enough vertical space to draw strings
        if string_display_height >= num_strings * vertical_spacing:
            string_length = tuner_width - 4
            string_start_x = tuner_start_x + 2

            for i, string_name in enumerate(self.guitar_strings.keys()):
                is_selected = string_name == current_string
                string_base_y = string_display_start_y + i * vertical_spacing

                # Ensure base string position is valid before drawing anything for this string
                if not (0 <= string_base_y < height):
                    continue

                # Calculate string thickness
                string_char = "╌" # Thin (B, E4)
                if string_name in ['D3', 'G3']: string_char = "─" # Medium
                if string_name in ['E2', 'A2']: string_char = "═" # Thick

                # Draw string name (check bounds)
                name_x = string_start_x - 3 # Adjusted position
                name_color = curses.A_BOLD if is_selected else curses.A_NORMAL
                if 0 <= name_x < width and name_x + len(string_name) <= width:
                    stdscr.addstr(string_base_y, name_x, string_name, name_color)

                # Draw the string itself (vibrating or straight)
                if is_selected and energy > 0.01: # Only vibrate selected string if there's sound
                    # Adjust vibration based on how far off tune and overall energy
                    cents_off = abs(1200 * math.log2(detected_freq / target_freq)) if detected_freq > 0 else max_diff_cents
                    off_tune_factor = min(1, cents_off / 20) # Max vibration when > 20 cents off

                    vibration_amplitude = (off_tune_factor * 0.5 + energy * 0.5) * 2.0 # Mix off-tune and energy
                    vibration_amplitude = min(1.5, vibration_amplitude) # Limit max amplitude
                    wave_speed = 0.15 + off_tune_factor * 0.2 # Faster wave if more off-tune

                    # Determine color based on accuracy
                    if accuracy > 0.9: color = self.hsv_to_color_pair(stdscr, 0.33, 0.8, 0.9)
                    elif accuracy > 0.7: color = self.hsv_to_color_pair(stdscr, 0.15, 0.8, 0.9)
                    else: color = self.hsv_to_color_pair(stdscr, 0.0, 0.8, 0.9)

                    # Draw vibrating string (sine wave)
                    if 0 <= string_start_x < width and string_start_x + string_length <= width: # Check horizontal bounds for the string area
                        phase = self.animation_frames * wave_speed
                        for x in range(string_length):
                            x_pos = string_start_x + x
                            x_ratio = x / (string_length -1) if string_length > 1 else 0.5

                            # Standing wave pattern
                            wave = math.sin(x_ratio * math.pi * 2 + phase) # Simple sine wave
                            y_offset = round(wave * vibration_amplitude)

                            y_pos = string_base_y + y_offset
                            if 0 <= y_pos < height: # Check y bound for this specific char
                                stdscr.addstr(y_pos, x_pos, string_char, color | curses.A_BOLD)

                else:
                    # Draw straight string (not vibrating or not selected)
                    color = curses.A_DIM # Use DIM for non-selected strings
                    y_pos = string_base_y

                    # --- Boundary Check FIX applied here ---
                    # Check if the line is within vertical bounds AND horizontal bounds
                    if 0 <= y_pos < height and 0 <= string_start_x < width and string_start_x + string_length <= width:
                        stdscr.addstr(y_pos, string_start_x, string_char * string_length, color)
                    # --- End FIX ---


    def handle_keypress(self, key):
        if key == curses.KEY_RIGHT or key == 'd' or key == 'l':
            # Move to next string
            self.string_index = (self.string_index + 1) % len(self.string_names)
            self.selected_string = self.string_names[self.string_index]
            self.needle_momentum = 0 # Reset needle momentum when changing strings
            self.needle_position = 0.5
            return True
        elif key == curses.KEY_LEFT or key == 'a' or key == 'h':
            # Move to previous string
            self.string_index = (self.string_index - 1 + len(self.string_names)) % len(self.string_names)
            self.selected_string = self.string_names[self.string_index]
            self.needle_momentum = 0 # Reset needle momentum
            self.needle_position = 0.5
            return True
        # Removed space key binding as 'auto-tune' wasn't implemented
        # elif key == ' ':
        #     # Placeholder for a potential auto-tune feature trigger
        #     # self.needle_position = 0.5 # Simulate tuning instantly
        #     # self.accuracy = 1.0
        #     return True # Consume the keypress even if feature isn't there
        return False