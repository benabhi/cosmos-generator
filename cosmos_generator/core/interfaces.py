"""
Abstract interfaces for core components.

This module defines abstract base classes for the main components of the system,
ensuring consistent interfaces and facilitating dependency injection.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Callable, TypeVar, Union, Protocol
import numpy as np
from PIL import Image

# Type definitions
T = TypeVar('T')
U = TypeVar('U')

# Color types
RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Color = Union[RGB, RGBA]

# Coordinate type
Coordinate = Tuple[float, float]

# Noise function types
NoiseFunction = Callable[[float, float], float]
WarpFunction = Callable[[float, float], Tuple[float, float]]
NoiseMapFunction = Callable[[int, int], np.ndarray]

# Image types
ImageType = Image.Image
MaskType = Image.Image

# Parameter types
ParamValue = Union[str, int, float, bool, None]
ParamDict = Dict[str, ParamValue]

# Validation types
ValidationError = Dict[str, str]
ValidationResult = Tuple[bool, Optional[List[ValidationError]]]


class NoiseGeneratorInterface(ABC):
    """Abstract interface for noise generators."""

    @abstractmethod
    def simplex_noise(self, x: float, y: float, scale: float = 1.0) -> float:
        """Generate 2D Simplex noise at the given coordinates."""
        pass

    @abstractmethod
    def fractal_simplex(self, x: float, y: float, octaves: int = 6,
                       persistence: float = 0.5, lacunarity: float = 2.0,
                       scale: float = 1.0) -> float:
        """Generate fractal Simplex noise at the given coordinates."""
        pass

    @abstractmethod
    def ridged_simplex(self, x: float, y: float, octaves: int = 6,
                      persistence: float = 0.5, lacunarity: float = 2.0,
                      scale: float = 1.0) -> float:
        """Generate ridged multi-fractal noise at the given coordinates."""
        pass

    @abstractmethod
    def worley_noise(self, x: float, y: float, cell_count: int = 10,
                    distance_function: str = "euclidean") -> float:
        """Generate Worley (cellular) noise at the given coordinates."""
        pass

    @abstractmethod
    def domain_warp(self, x: float, y: float,
                   warp_function: Callable[[float, float], float],
                   noise_function: Callable[[float, float], float],
                   warp_strength: float = 1.0) -> float:
        """Apply domain warping to create more organic patterns."""
        pass

    @abstractmethod
    def simplex_warp(self, x: float, y: float, scale: float = 1.0,
                    strength: float = 1.0) -> Coordinate:
        """Apply simplex-based domain warping to coordinates."""
        pass

    @abstractmethod
    def generate_noise_map(self, width: int, height: int,
                          noise_function: Callable[[float, float], float]) -> np.ndarray:
        """Generate a 2D noise map using the provided noise function."""
        pass

    @abstractmethod
    def combine_noise_maps(self, noise_maps: List[np.ndarray],
                          weights: List[float]) -> np.ndarray:
        """Combine multiple noise maps with the given weights."""
        pass


class ColorPaletteInterface(ABC):
    """Abstract interface for color palettes."""

    @abstractmethod
    def get_random_color(self, planet_type: str, category: str = "base") -> Color:
        """Get a random color from a specific planet type and category."""
        pass

    @abstractmethod
    def get_ring_color(self, planet_type: str) -> RGBA:
        """Get a random ring color for a specific planet type."""
        pass

    @abstractmethod
    def get_atmosphere_color(self, planet_type: str) -> RGBA:
        """Get a random atmosphere color for a specific planet type."""
        pass

    @abstractmethod
    def get_cloud_color(self, planet_type: str) -> RGBA:
        """Get a random cloud color for a specific planet type."""
        pass

    @abstractmethod
    def blend_colors(self, color1: Color, color2: Color, ratio: float = 0.5) -> Color:
        """Blend two colors together."""
        pass

    @abstractmethod
    def adjust_brightness(self, color: Color, factor: float) -> Color:
        """Adjust the brightness of a color."""
        pass


class TextureGeneratorInterface(ABC):
    """Abstract interface for texture generators."""

    @abstractmethod
    def create_base_sphere(self, size: int, color: Color) -> ImageType:
        """Create a base sphere with the given color."""
        pass

    @abstractmethod
    def apply_noise_to_sphere(self, base_image: ImageType, noise_map: np.ndarray,
                             color_map: Dict[str, Color], threshold_map: Dict[float, str]) -> ImageType:
        """Apply noise to a sphere using the provided color and threshold maps."""
        pass

    @abstractmethod
    def apply_lighting(self, texture: ImageType, light_angle: float = 45.0,
                      light_intensity: float = 1.0, falloff: float = 0.6) -> ImageType:
        """Apply lighting to a texture."""
        pass


class FeatureInterface(ABC):
    """Abstract interface for planet features."""

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Whether the feature is enabled."""
        pass

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool) -> None:
        """Set whether the feature is enabled."""
        pass


class AtmosphereInterface(FeatureInterface):
    """Abstract interface for atmosphere features."""

    @abstractmethod
    def apply_to_planet(self, planet_image: ImageType, planet_type: str,
                       has_rings: bool = False, color: Optional[RGBA] = None) -> ImageType:
        """Apply atmospheric effects to a planet image."""
        pass


class CloudsInterface(FeatureInterface):
    """Abstract interface for cloud features."""

    @property
    @abstractmethod
    def coverage(self) -> float:
        """Cloud coverage (0.0 to 1.0)."""
        pass

    @coverage.setter
    @abstractmethod
    def coverage(self, value: float) -> None:
        """Set cloud coverage."""
        pass

    @abstractmethod
    def set_light_angle(self, angle: float) -> None:
        """Set the light angle for cloud lighting effects."""
        pass

    @abstractmethod
    def apply_to_planet(self, planet_image: ImageType) -> ImageType:
        """Apply clouds to a planet image."""
        pass


class RingsInterface(FeatureInterface):
    """Abstract interface for ring features."""

    @abstractmethod
    def apply_rings(self, planet_image: ImageType, planet_type: str,
                   tilt: float = 0.0, light_angle: float = 45.0,
                   color: Optional[RGBA] = None, detail: float = 1.0,
                   original_planet_size: Optional[int] = None) -> ImageType:
        """Apply rings to a planet image."""
        pass


class CelestialBodyInterface(ABC):
    """Abstract interface for celestial bodies."""

    # These properties are implemented in the concrete classes
    # We don't make them abstract to avoid breaking existing code

    @abstractmethod
    def render(self) -> ImageType:
        """Render the celestial body."""
        pass

    @abstractmethod
    def save(self, filename: str) -> None:
        """Save the celestial body image to a file."""
        pass

    @abstractmethod
    def get_params(self) -> ParamDict:
        """Get the parameters used to generate this celestial body."""
        pass

    @abstractmethod
    def set_param(self, key: str, value: ParamValue) -> None:
        """Set a parameter and invalidate the image cache."""
        pass

    @abstractmethod
    def get_param(self, key: str, default: ParamValue = None) -> ParamValue:
        """Get a parameter value."""
        pass


class PlanetInterface(CelestialBodyInterface):
    """Abstract interface for planets."""

    @property
    def PLANET_TYPE(self) -> str:
        """Planet type identifier."""
        return self.__class__.__name__.replace('Planet', '')

    # These properties are implemented in the concrete classes
    # We don't make them abstract to avoid breaking existing code

    @abstractmethod
    def generate_texture(self) -> ImageType:
        """Generate the base texture for the planet."""
        pass

    @abstractmethod
    def apply_lighting(self, texture: ImageType) -> ImageType:
        """Apply lighting to the planet texture."""
        pass

    @abstractmethod
    def apply_features(self, base_image: ImageType) -> ImageType:
        """Apply additional features to the planet."""
        pass


class ContainerInterface(ABC):
    """Abstract interface for containers."""

    @abstractmethod
    def set_content(self, content: Any) -> None:
        """Set the content to be displayed in the container."""
        pass

    @abstractmethod
    def set_rotation(self, angle: float) -> None:
        """Set the rotation angle."""
        pass

    @abstractmethod
    def rotate(self, angle: float) -> None:
        """Rotate by the specified angle."""
        pass

    @abstractmethod
    def render(self) -> ImageType:
        """Render the container with its content."""
        pass

    @abstractmethod
    def export(self, filename: str) -> None:
        """Export the current container to an image file."""
        pass
