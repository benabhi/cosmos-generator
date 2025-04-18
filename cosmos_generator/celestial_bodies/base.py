"""
Base class for all celestial objects.
"""
from typing import Dict, Any, Optional, Tuple
import random
from PIL import Image

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator


class AbstractCelestialBody:
    """
    Base class for all celestial objects.
    """

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a celestial body with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the celestial body image in pixels
            **kwargs: Additional parameters for customization
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.size = size
        self.params = kwargs

        # Initialize generators with the same seed for consistency
        self.rng = random.Random(self.seed)
        self.noise_gen = FastNoiseGenerator(seed=self.seed)
        self.color_palette = ColorPalette(seed=self.seed)
        self.texture_gen = TextureGenerator(seed=self.seed)

        # Image cache
        self._image = None

    @property
    def image(self) -> Image.Image:
        """
        Get the rendered image of the celestial body.

        Returns:
            PIL Image of the celestial body
        """
        if self._image is None:
            self._image = self.render()
        return self._image

    def render(self) -> Image.Image:
        """
        Render the celestial body.

        Returns:
            PIL Image of the celestial body
        """
        raise NotImplementedError("Subclasses must implement render()")

    def save(self, filename: str) -> None:
        """
        Save the celestial body image to a file.

        Args:
            filename: Output filename
        """
        self.image.save(filename)

    def get_params(self) -> Dict[str, Any]:
        """
        Get the parameters used to generate this celestial body.

        Returns:
            Dictionary of parameters
        """
        return {
            "seed": self.seed,
            "size": self.size,
            **self.params
        }

    def set_param(self, key: str, value: Any) -> None:
        """
        Set a parameter and invalidate the image cache.

        Args:
            key: Parameter name
            value: Parameter value
        """
        if key == "seed":
            self.seed = value
            # Reinitialize generators with the new seed
            self.rng = random.Random(self.seed)
            self.noise_gen = FastNoiseGenerator(seed=self.seed)
            self.color_palette = ColorPalette(seed=self.seed)
            self.texture_gen = TextureGenerator(seed=self.seed)
        elif key == "size":
            self.size = value
        else:
            self.params[key] = value

        # Invalidate image cache
        self._image = None

    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Get a parameter value.

        Args:
            key: Parameter name
            default: Default value if parameter is not set

        Returns:
            Parameter value
        """
        if key == "seed":
            return self.seed
        elif key == "size":
            return self.size
        else:
            return self.params.get(key, default)

    def __str__(self) -> str:
        """
        Get a string representation of the celestial body.

        Returns:
            String representation
        """
        return f"{self.__class__.__name__}(seed={self.seed}, size={self.size})"
