# visualizers/__init__.py
from .bars import BarsVisualizer
from .circle import CircleVisualizer
from .wave import WaveVisualizer
from .particles import ParticlesVisualizer
from .flame import FlameVisualizer
from .matrix_rain import MatrixRainVisualizer
from .neural_dreamscape import NeuralDreamscapeVisualizer
from .neural_dreamscape_lite import NeuralDreamscapeLiteVisualizer
from .fractal_universe import FractalUniverseVisualizer
from .fractal_universe_lite import FractalUniverseLiteVisualizer
from .stick_figure import StickFigureVisualizer
from .starfield_warp import StarfieldWarpVisualizer
from .cosmic_pulsar import CosmicPulsarVisualizer

# Dictionary mapping visualizer names to classes
visualizers = {
    "bars": BarsVisualizer,
    "circle": CircleVisualizer,
    "wave": WaveVisualizer,
    "particles": ParticlesVisualizer,
    "flame": FlameVisualizer,
    "matrix": MatrixRainVisualizer,
    "neural": NeuralDreamscapeVisualizer,
    "neural-lite": NeuralDreamscapeLiteVisualizer,
    "fractal": FractalUniverseVisualizer,
    "fractal-lite": FractalUniverseLiteVisualizer,
    "stick": StickFigureVisualizer,
    "starfield": StarfieldWarpVisualizer,
    "pulsar": CosmicPulsarVisualizer,
}