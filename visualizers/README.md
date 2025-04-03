# Creating Custom Visualizers for CLI-Viz

This guide explains how to create custom visualizers for the CLI-Viz audio visualization system.

## Basic Structure

All visualizers must:
1. Inherit from the `VisualizerBase` class
2. Implement at least the `draw()` method
3. Be placed in the `visualizers` directory with a `.py` extension

## Minimal Example

Here's a minimal example of a custom visualizer:

```python
# visualizers/minimal.py
from visualizer_base import VisualizerBase
import curses

class MinimalVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Minimal Example")
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Draw a simple text at the center of the screen
        message = "Audio Level: {:.2f}".format(energy)
        y = height // 2
        x = width // 2 - len(message) // 2
        
        # Use the color helpers from the base class
        color = self.hsv_to_color_pair(stdscr, hue_offset, 1.0, 1.0)
        stdscr.addstr(y, x, message, color | curses.A_BOLD)
```

## Essential Methods

### Required Methods

- `__init__(self)`: Initialize your visualizer and set its name by calling `super().__init__(name="Your Visualizer Name")`
- `draw(self, stdscr, spectrum, height, width, energy, hue_offset)`: The main method that draws your visualization

### Optional Methods

- `setup(self)`: Called once when the visualizer is loaded; use for initialization
- `handle_keypress(self, key)`: Handle keyboard input specific to your visualizer; return True if handled

## Parameters

When implementing the `draw()` method, you'll have access to these parameters:

- `stdscr`: The curses screen object used for drawing
- `spectrum`: NumPy array containing the audio frequency spectrum (normalized)
- `height, width`: Current terminal dimensions
- `energy`: Overall audio energy level (useful for beat detection)
- `hue_offset`: Current color hue offset (for creating color cycles)

## Helpful Utilities

The base class provides useful methods:

- `self.hsv_to_color_pair(stdscr, h, s, v)`: Convert HSV color (0-1 range) to a curses color pair
- `self.get_color_pair(stdscr, r, g, b)`: Convert RGB color (0-255 range) to a curses color pair

## Audio Data Usage

### Frequency Spectrum

The `spectrum` parameter is a numpy array containing the frequency components of the audio:
- Lower indices (e.g., `spectrum[0:10]`) represent bass frequencies
- Middle indices (e.g., `spectrum[10:30]`) represent mid-range frequencies
- Higher indices represent treble frequencies

Example:
```python
# Get bass, mid, and treble energy
bass = np.mean(spectrum[:10])
mids = np.mean(spectrum[10:30])
treble = np.mean(spectrum[30:])
```

### Overall Energy

The `energy` parameter represents the overall energy level of the audio and is useful for detecting beats.

Example:
```python
if energy > 0.2:  # Detected a beat
    # Do something exciting
```

## Best Practices

1. **Performance**: Terminal rendering can be slow, so keep your visualizations efficient
   - Avoid redrawing areas that haven't changed
   - Limit the number of characters you draw

2. **Responsiveness**: Make your visualization responsive to audio
   - Use spectrum data to influence your visual elements
   - React to beats using the energy parameter

3. **Terminal Compatibility**: Use ASCII characters that work across different terminals
   - For wide compatibility, stick to basic ASCII
   - For more visual appeal, use Unicode when appropriate

4. **Size Adaptation**: Handle different terminal sizes gracefully
   - Adapt your visualization to the available dimensions
   - Check bounds before drawing to avoid errors

5. **State Management**: Keep visualizer state in instance variables
   - Initialize them in `__init__` or `setup`
   - Update them in the `draw` method

## Advanced Example: Pulsing Text

Here's a more advanced example showing audio-reactive text:

```python
# visualizers/pulsing_text.py
from visualizer_base import VisualizerBase
import curses
import numpy as np
import math

class PulsingTextVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Pulsing Text")
        self.message = "CLI-VIZ"
        self.beat_intensity = 0
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Update beat intensity (rise quickly, fall slowly)
        if energy > self.beat_intensity:
            self.beat_intensity = energy
        else:
            self.beat_intensity *= 0.9  # Decay factor
            
        # Calculate text size based on beat intensity
        size_multiplier = 1.0 + self.beat_intensity * 2.0
        
        # Draw each letter with different color and size
        message_width = len(self.message) * 2  # Estimate width
        start_x = width // 2 - int(message_width * size_multiplier) // 2
        y = height // 2
        
        for i, char in enumerate(self.message):
            # Calculate position with some oscillation
            char_x = start_x + int(i * 2 * size_multiplier)
            char_y = y + int(math.sin(time.time() * 2 + i) * self.beat_intensity * 2)
            
            # Skip if out of bounds
            if not (0 <= char_y < height - 1 and 0 <= char_x < width - 1):
                continue
                
            # Calculate color based on spectrum and position
            freq_idx = (i * 5) % (len(spectrum) // 4)
            freq_intensity = spectrum[freq_idx] * 3.0
            
            hue = (i / len(self.message) + hue_offset) % 1.0
            sat = 0.7 + 0.3 * freq_intensity
            val = 0.7 + 0.3 * self.beat_intensity
            
            # Draw character with appropriate attributes
            color = self.hsv_to_color_pair(stdscr, hue, sat, val)
            
            # Choose character style based on energy
            attrs = curses.A_BOLD
            if freq_intensity > 0.5:
                attrs |= curses.A_REVERSE
                
            # Draw the character
            stdscr.addstr(char_y, char_x, char, color | attrs)
```

## Loading Your Visualizer

Once you've created your visualizer, save it in the `visualizers` directory with a `.py` extension. CLI-Viz will automatically detect and load it the next time you start the application.

If your visualizer doesn't appear, check for errors in the terminal output when starting the application.
