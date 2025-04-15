"""
Base generator class for celestial bodies.
"""
from typing import Dict, Any, Optional, List, Type
import random

from cosmos_generator.core.noise_generator import NoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator


class CelestialGenerator:
    """
    Base class for generating celestial bodies.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a celestial generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)
        self.noise_gen = NoiseGenerator(seed=self.seed)
        self.color_palette = ColorPalette(seed=self.seed)
        self.texture_gen = TextureGenerator(seed=self.seed)
        
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
        type_seed = self.seed + hash(celestial_type) % 1000000
        
        # Merge default parameters with provided parameters
        default_params = {
            "seed": type_seed,
            "size": 512,
        }
        
        if params:
            default_params.update(params)
            
        # Create the celestial body
        return self.celestial_types[celestial_type](**default_params)
