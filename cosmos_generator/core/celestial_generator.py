"""
Base generator class for celestial bodies.
"""
from typing import Dict, Any, Optional, List, Type
import random

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator
from cosmos_generator.core.interfaces import NoiseGeneratorInterface, ColorPaletteInterface, TextureGeneratorInterface


class CelestialGenerator:
    """
    Base class for generating celestial bodies.
    """

    def __init__(self, seed: Optional[int] = None,
                 noise_gen: Optional[NoiseGeneratorInterface] = None,
                 color_palette: Optional[ColorPaletteInterface] = None,
                 texture_gen: Optional[TextureGeneratorInterface] = None):
        """
        Initialize a celestial generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
            texture_gen: Optional texture generator instance (will create one if not provided)
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

        # Use provided instances or create new ones
        self.noise_gen = noise_gen if noise_gen is not None else FastNoiseGenerator(seed=self.seed)
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=self.seed)

        # If texture_gen is provided, use it; otherwise create a new one with our noise_gen and color_palette
        if texture_gen is not None:
            self.texture_gen = texture_gen
        else:
            self.texture_gen = TextureGenerator(seed=self.seed,
                                               noise_gen=self.noise_gen,
                                               color_palette=self.color_palette)

        # Registry for celestial body types
        self.celestial_types: Dict[str, Type] = {}

    def register_celestial_type(self, name: str, cls: Type) -> None:
        """
        Register a celestial body type.

        Args:
            name: Name of the celestial body type
            cls: Class for the celestial body type
        """
        self.celestial_types[name] = cls

    def get_celestial_types(self) -> List[str]:
        """
        Get a list of registered celestial body types.

        Returns:
            List of celestial body type names
        """
        return list(self.celestial_types.keys())

    def create(self, celestial_type: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create a celestial body of the specified type.

        Args:
            celestial_type: Type of celestial body to create
            params: Optional parameters for customization

        Returns:
            Created celestial body instance
        """
        if celestial_type not in self.celestial_types:
            raise ValueError(f"Unknown celestial type: {celestial_type}")

        # Create a new seed based on the base seed and celestial type
        # Use a deterministic method that doesn't rely on hash() which can vary between sessions
        # We'll use a simple string-to-int conversion based on character codes
        type_int = sum(ord(c) * (i + 1) for i, c in enumerate(celestial_type.lower()))
        type_seed = self.seed + type_int % 1000000

        # Merge default parameters with provided parameters
        default_params = {
            "seed": type_seed,
            "size": 512,
            "noise_gen": self.noise_gen,
            "color_palette": self.color_palette,
            "texture_gen": self.texture_gen
        }

        if params:
            default_params.update(params)

        # Create the celestial body
        return self.celestial_types[celestial_type](**default_params)
