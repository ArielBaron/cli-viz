# CLI-Viz: Terminal Audio Visualizer

A powerful terminal-based audio visualizer with a plugin system that renders beautiful, responsive visualizations in your terminal. CLI-Viz processes audio from your microphone in real-time and transforms it into captivating visual displays.

## Included Visualizations

1. **Spectrum Bars**: Classic frequency spectrum analyzer with colorful bars
   - Controls: **b/B** - Increase/decrease bass boost
![Spectrum Bars](previews/bars.gif)

2. **Wave**: Audio-reactive sine wave that changes with different frequencies
![Wave](previews/wave.gif)

3. **Circle**: Circular spectrum visualization with pulsating rings
![Circle](previews/circle.gif)

4. **Particles**: Particle system that responds to beats and energy in the music
   - Controls: **p/P** - Increase/decrease maximum number of particles
![Particles](previews/particles.gif)

5. **Flame**: A realistic flame that dances to your music
   - Controls: **w/W** - Increase/decrease flame width
   - Controls: **h/H** - Increase/decrease flame height
![Flame](previews/flame.gif)

6. **Fractal Universe**: Hypnotic fractal patterns that evolve and respond to audio frequencies
![Fractal Universe](previews/fractal_universe.gif)

7. **Matrix Rain**: Digital rain effect inspired by The Matrix, with characters that flow and respond to the music
![Matrix Rain](previews/matrix_rain.gif)

8. **Neural Dreamscape**: Abstract visualization resembling neural networks that pulse and evolve with audio input
![Neural Dreamscape](previews/neural_dreamscape.gif)

9. **Neural Dreamscape Lite**: Optimized version of Neural Dreamscape designed specifically for low-end devices like Raspberry Pi Zero W

## Features

- Modular plugin system for visualizers
- Multiple audio-reactive visualizations included
- Real-time audio processing
- Customizable with keyboard controls
- Low resource usage

## Global Controls

- **Q**: Quit the program
- **M**: Switch to the next visualization
- **Space**: Pause/resume visualizations
- **+/-**: Increase/decrease audio sensitivity

## Requirements

- Python 3.6+
- numpy
- pyaudio
- curses (included in the standard library)

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/sam1am/cli-viz.git
cd cli-viz

# Create venv (optional)
python -m venv venv
source ./venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the visualizer
python main.py
```

### Troubleshooting PyAudio Installation

If you encounter issues installing PyAudio:

#### On Linux:
```bash
# Install portaudio development package
sudo apt-get install portaudio19-dev python-pyaudio

# Then install PyAudio
pip install pyaudio
```

#### On macOS:
```bash
# Using Homebrew
brew install portaudio
pip install pyaudio
```

#### On Windows:
You may need to install PyAudio from a pre-built wheel:
```bash
pip install pipwin
pipwin install pyaudio
```

## Creating Your Own Visualizers

CLI-Viz has a plugin system that makes it easy to create your own visualizations. See the [visualizer documentation](visualizers/README.md) for details on creating custom visualizers.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue on GitHub.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-visualization`)
3. Commit your changes (`git commit -am 'Add amazing visualization'`)
4. Push to the branch (`git push origin feature/amazing-visualization`)
5. Create a new Pull Request