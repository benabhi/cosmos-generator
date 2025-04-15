"""
Atmospheric effects for celestial bodies.
"""
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.core.color_palette import ColorPalette, RGBA


class Atmosphere:
    """
    Creates atmospheric glow effects for planets.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize an atmosphere generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
        """
        self.color_palette = ColorPalette(seed=seed)
    
    def apply_atmosphere(self, planet_image: Image.Image, planet_type: str, 
                        intensity: float = 0.5, color: Optional[RGBA] = None) -> Image.Image:
        """
        Apply atmospheric glow to a planet image.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere

        Returns:
            Planet image with atmospheric glow
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")
            
        # Get atmosphere color
        if color is None:
            atmosphere_color = self.color_palette.get_atmosphere_color(planet_type)
        else:
            atmosphere_color = color
            
        # Create a larger circle for the atmosphere
        size = planet_image.width
        atmosphere_size = int(size * (1.0 + 0.1 * intensity))
        atmosphere = Image.new("RGBA", (atmosphere_size, atmosphere_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(atmosphere)
        
        # Draw the atmosphere circle
        draw.ellipse((0, 0, atmosphere_size-1, atmosphere_size-1), fill=atmosphere_color)
        
        # Blur the atmosphere
        blur_radius = int(size * 0.05 * intensity)
        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Create a new image for the result
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        
        # Paste the atmosphere centered on the result
        offset = (size - atmosphere_size) // 2
        result.paste(atmosphere, (offset, offset), atmosphere)
        
        # Paste the planet on top
        result.paste(planet_image, (0, 0), planet_image)
        
        return result
