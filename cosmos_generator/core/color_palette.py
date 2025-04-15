"""
Color palette management for celestial bodies.
"""
from typing import Dict, List, Tuple, Union, Optional
import random

# Type aliases
RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Color = Union[RGB, RGBA]


class ColorPalette:
    """
    Manages color schemes for different celestial bodies.
    Provides methods for generating, manipulating, and retrieving colors.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a color palette with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible color generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

        # Predefined color palettes for different planet types
        self.planet_palettes: Dict[str, Dict[str, List[Color]]] = {
            "Desert": {
                "base": [(210, 180, 140), (244, 164, 96), (222, 184, 135)],
                "highlight": [(255, 222, 173), (245, 222, 179)],
                "shadow": [(139, 69, 19), (160, 82, 45)],
            },
            "Furnace": {
                "base": [(139, 0, 0), (178, 34, 34), (165, 42, 42)],
                "highlight": [(255, 69, 0), (255, 140, 0), (255, 165, 0)],
                "shadow": [(64, 0, 0), (80, 10, 10)],
                "special": [(255, 215, 0), (255, 255, 0)],  # Lava/magma
            },
            "Grave": {
                "base": [(105, 105, 105), (128, 128, 128), (169, 169, 169)],
                "highlight": [(192, 192, 192), (211, 211, 211)],
                "shadow": [(47, 79, 79), (70, 70, 70)],
            },
            "Ice": {
                "base": [(240, 248, 255), (240, 255, 255), (230, 230, 250)],
                "highlight": [(255, 255, 255), (245, 255, 250)],
                "shadow": [(176, 196, 222), (176, 224, 230)],
                "special": [(135, 206, 235), (135, 206, 250)],  # Ice cracks
            },
            "Jovian": {
                "base": [(255, 222, 173), (222, 184, 135), (210, 180, 140)],
                "highlight": [(255, 228, 181), (255, 218, 185)],
                "shadow": [(160, 82, 45), (139, 69, 19)],
                "band1": [(255, 160, 122), (250, 128, 114)],  # Reddish bands
                "band2": [(152, 251, 152), (143, 188, 143)],  # Greenish bands
                "band3": [(135, 206, 235), (135, 206, 250)],  # Bluish bands
                "storm": [(255, 255, 224), (255, 250, 205)],  # Storm systems
            },
            "Jungle": {
                "base": [(34, 139, 34), (0, 128, 0), (0, 100, 0)],
                "highlight": [(144, 238, 144), (152, 251, 152)],
                "shadow": [(0, 100, 0), (85, 107, 47)],
                "water": [(0, 128, 128), (32, 178, 170)],
            },
            "Living": {
                "base": [(221, 160, 221), (218, 112, 214), (186, 85, 211)],
                "highlight": [(238, 130, 238), (255, 0, 255)],
                "shadow": [(148, 0, 211), (138, 43, 226)],
                "special": [(127, 255, 212), (64, 224, 208)],  # Bioluminescence
            },
            "Ocean": {
                "base": [(0, 128, 128), (0, 139, 139), (32, 178, 170)],
                "highlight": [(64, 224, 208), (127, 255, 212)],
                "shadow": [(0, 105, 148), (25, 25, 112)],
                "land": [(240, 230, 140), (189, 183, 107)],  # Islands
            },
            "Rocky": {
                "base": [(112, 128, 144), (119, 136, 153), (128, 128, 128)],
                "highlight": [(192, 192, 192), (211, 211, 211)],
                "shadow": [(47, 79, 79), (105, 105, 105)],
            },
            "Tainted": {
                "base": [(85, 107, 47), (107, 142, 35), (128, 128, 0)],
                "highlight": [(154, 205, 50), (173, 255, 47)],
                "shadow": [(0, 100, 0), (34, 139, 34)],
                "contamination": [(148, 0, 211), (138, 43, 226)],  # Unnatural colors
            },
            "Vital": {
                "base": [(0, 128, 128), (46, 139, 87), (60, 179, 113)],
                "highlight": [(152, 251, 152), (144, 238, 144)],
                "shadow": [(0, 100, 0), (85, 107, 47)],
                "water": [(0, 191, 255), (30, 144, 255)],
                "land": [(210, 180, 140), (222, 184, 135)],
                "ice": [(240, 248, 255), (240, 255, 255)],
            },
            "Shattered": {
                "base": [(139, 0, 0), (165, 42, 42), (178, 34, 34)],
                "highlight": [(255, 69, 0), (255, 140, 0)],
                "shadow": [(64, 0, 0), (80, 10, 10)],
                "core": [(255, 215, 0), (255, 255, 0)],  # Exposed core
            },
        }

        # Atmospheric color palettes
        self.atmosphere_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(255, 200, 150, 60), (255, 220, 180, 40)],
            "Furnace": [(255, 100, 0, 80), (255, 150, 50, 60)],
            "Grave": [(150, 150, 150, 40), (180, 180, 180, 30)],
            "Ice": [(200, 240, 255, 50), (220, 255, 255, 40)],
            "Jovian": [(255, 220, 180, 70), (255, 240, 200, 50)],
            "Jungle": [(150, 255, 150, 60), (200, 255, 200, 40)],
            "Living": [(220, 150, 220, 70), (240, 180, 240, 50)],
            "Ocean": [(150, 200, 255, 70), (180, 230, 255, 50)],
            "Rocky": [(200, 200, 200, 40), (220, 220, 220, 30)],
            "Tainted": [(150, 255, 100, 70), (200, 255, 150, 50)],
            "Vital": [(150, 200, 255, 60), (200, 230, 255, 40)],
            "Shattered": [(255, 100, 50, 80), (255, 150, 100, 60)],
        }

        # Ring color palettes - Increased opacity for better visibility
        self.ring_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(210, 180, 140, 200), (244, 164, 96, 180), (222, 184, 135, 160)],
            "Furnace": [(139, 0, 0, 200), (178, 34, 34, 180), (165, 42, 42, 160)],
            "Grave": [(105, 105, 105, 200), (128, 128, 128, 180), (169, 169, 169, 160)],
            "Ice": [(240, 248, 255, 200), (240, 255, 255, 180), (230, 230, 250, 160)],
            "Jovian": [(255, 222, 173, 200), (222, 184, 135, 180), (210, 180, 140, 160)],
            "Jungle": [(34, 139, 34, 200), (0, 128, 0, 180), (0, 100, 0, 160)],
            "Living": [(221, 160, 221, 200), (218, 112, 214, 180), (186, 85, 211, 160)],
            "Ocean": [(0, 128, 128, 200), (0, 139, 139, 180), (32, 178, 170, 160)],
            "Rocky": [(112, 128, 144, 200), (119, 136, 153, 180), (128, 128, 128, 160)],
            "Tainted": [(85, 107, 47, 200), (107, 142, 35, 180), (128, 128, 0, 160)],
            "Vital": [(0, 128, 128, 200), (46, 139, 87, 180), (60, 179, 113, 160)],
            "Shattered": [(139, 0, 0, 200), (165, 42, 42, 180), (178, 34, 34, 160)],
        }

        # Cloud color palettes - Pure white with maximum opacity for all planet types
        # This ensures clouds are always clearly visible regardless of planet color
        self.cloud_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(255, 255, 255, 255)],      # Pure white for all planet types
            "Furnace": [(255, 255, 255, 255)],    # Pure white for all planet types
            "Grave": [(255, 255, 255, 255)],      # Pure white for all planet types
            "Ice": [(255, 255, 255, 255)],        # Pure white for all planet types
            "Jovian": [(255, 255, 255, 255)],     # Pure white for all planet types
            "Jungle": [(255, 255, 255, 255)],     # Pure white for all planet types
            "Living": [(255, 255, 255, 255)],     # Pure white for all planet types
            "Ocean": [(255, 255, 255, 255)],      # Pure white for all planet types
            "Rocky": [(255, 255, 255, 255)],      # Pure white for all planet types
            "Tainted": [(255, 255, 255, 255)],    # Pure white for all planet types
            "Vital": [(255, 255, 255, 255)],      # Pure white for all planet types
            "Shattered": [(255, 255, 255, 255)],  # Pure white for all planet types
        }

    def get_random_color(self, planet_type: str, category: str = "base") -> Color:
        """
        Get a random color from a specific planet type and category.

        Args:
            planet_type: The type of planet (e.g., "Desert", "Ocean")
            category: The color category (e.g., "base", "highlight", "shadow")

        Returns:
            A random color from the specified palette
        """
        if planet_type not in self.planet_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        palette = self.planet_palettes[planet_type]
        if category not in palette:
            raise ValueError(f"Unknown color category '{category}' for planet type '{planet_type}'")

        return self.rng.choice(palette[category])

    def get_atmosphere_color(self, planet_type: str) -> RGBA:
        """
        Get a random atmospheric color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the atmosphere
        """
        if planet_type not in self.atmosphere_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        return self.rng.choice(self.atmosphere_palettes[planet_type])

    def get_ring_color(self, planet_type: str) -> RGBA:
        """
        Get a random ring color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the rings
        """
        if planet_type not in self.ring_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        return self.rng.choice(self.ring_palettes[planet_type])

    def get_cloud_color(self, planet_type: str) -> RGBA:
        """
        Get a random cloud color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the clouds
        """
        if planet_type not in self.cloud_palettes:
            # Default to white clouds if planet type not found
            return (255, 255, 255, 180)

        return self.rng.choice(self.cloud_palettes[planet_type])

    def blend_colors(self, color1: Color, color2: Color, ratio: float = 0.5) -> Color:
        """
        Blend two colors together.

        Args:
            color1: First color
            color2: Second color
            ratio: Blend ratio (0.0 = all color1, 1.0 = all color2)

        Returns:
            Blended color
        """
        # Handle different color formats (RGB vs RGBA)
        if len(color1) == 3 and len(color2) == 3:
            # Both RGB
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            return (r, g, b)
        elif len(color1) == 4 and len(color2) == 4:
            # Both RGBA
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(color1[3] * (1 - ratio) + color2[3] * ratio)
            return (r, g, b, a)
        elif len(color1) == 3 and len(color2) == 4:
            # RGB and RGBA
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(255 * (1 - ratio) + color2[3] * ratio)
            return (r, g, b, a)
        elif len(color1) == 4 and len(color2) == 3:
            # RGBA and RGB
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(color1[3] * (1 - ratio) + 255 * ratio)
            return (r, g, b, a)
        else:
            raise ValueError("Invalid color formats")

    def adjust_brightness(self, color: Color, factor: float) -> Color:
        """
        Adjust the brightness of a color.

        Args:
            color: The color to adjust
            factor: Brightness factor (>1.0 brightens, <1.0 darkens)

        Returns:
            Adjusted color
        """
        if len(color) == 3:
            # RGB
            r = min(255, int(color[0] * factor))
            g = min(255, int(color[1] * factor))
            b = min(255, int(color[2] * factor))
            return (r, g, b)
        elif len(color) == 4:
            # RGBA
            r = min(255, int(color[0] * factor))
            g = min(255, int(color[1] * factor))
            b = min(255, int(color[2] * factor))
            return (r, g, b, color[3])
        else:
            raise ValueError("Invalid color format")
