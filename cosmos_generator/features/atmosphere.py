"""
Atmospheric effects for celestial bodies.
"""
from typing import Tuple, Optional
import math
import numpy as np
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
                        intensity: float = 0.5, color: Optional[RGBA] = None,
                        light_angle: float = 45.0) -> Image.Image:
        """
        Apply atmospheric glow to a planet image with a fine light line around the edge.
        The atmosphere will be darker in shadowed areas and brighter in lit areas.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere
            light_angle: Angle of the light source in degrees

        Returns:
            Planet image with atmospheric glow and edge highlight
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Get atmosphere color
        if color is None:
            atmosphere_color = self.color_palette.get_atmosphere_color(planet_type)
        else:
            atmosphere_color = color

        # Extract color components
        r, g, b, a = atmosphere_color

        # Create a much brighter color for the edge highlight
        # Use pure white for maximum visibility and luminosity
        highlight_color = (
            255,  # Pure white for maximum brightness
            255,
            255,
            255  # Full opacity
        )

        # Get the size of the planet image
        size = planet_image.width

        # Create a new image for the result
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Create a mask for the planet
        planet_mask = Image.new("L", (size, size), 0)
        planet_draw = ImageDraw.Draw(planet_mask)
        planet_draw.ellipse((0, 0, size-1, size-1), fill=255)

        # Create a mask for the atmosphere (slightly larger than the planet)
        # Use a small difference to make the line fine but visible
        atmosphere_size = size + int(size * 0.02 * intensity)  # 1-2% larger
        atmosphere_mask = Image.new("L", (atmosphere_size, atmosphere_size), 0)
        atmosphere_draw = ImageDraw.Draw(atmosphere_mask)
        atmosphere_draw.ellipse((0, 0, atmosphere_size-1, atmosphere_size-1), fill=255)

        # Calculate the offset to center the atmosphere mask
        offset = (size - atmosphere_size) // 2

        # Create a new image for the atmosphere
        atmosphere = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Paste the atmosphere mask into the atmosphere image
        atmosphere_with_offset = Image.new("L", (size, size), 0)
        atmosphere_with_offset.paste(atmosphere_mask, (offset, offset))

        # Create the ring by subtracting the planet mask from the atmosphere mask
        ring_mask = ImageChops.subtract(atmosphere_with_offset, planet_mask)

        # Calculate light direction
        light_rad = math.radians(light_angle)
        light_x = math.cos(light_rad)
        light_y = -math.sin(light_rad)  # Negative because y increases downward in images

        # Create a light mask with a gradient based on light direction
        light_mask = Image.new("L", (size, size), 0)
        light_draw = ImageDraw.Draw(light_mask)

        # Draw a gradient circle for the light mask
        for y in range(size):
            for x in range(size):
                # Skip if not in the ring area
                if ring_mask.getpixel((x, y)) == 0:
                    continue

                # Calculate position relative to center
                dx = (x - size/2) / (size/2)
                dy = (y - size/2) / (size/2)

                # Calculate dot product with light direction
                dot = dx * light_x + dy * light_y

                # Apply lighting factor
                if dot < 0:
                    # Point is facing away from light
                    factor = 0.3  # Darker in shadow but still visible
                else:
                    # Brighter in light
                    factor = 0.3 + 0.7 * dot

                # Set light mask value
                light_mask.putpixel((x, y), min(255, int(255 * factor)))

        # Apply the light mask to the ring mask
        lit_ring_mask = ImageChops.multiply(ring_mask, light_mask)

        # Create a colored version of the lit ring
        colored_ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Draw the colored ring pixel by pixel
        for y in range(size):
            for x in range(size):
                mask_value = lit_ring_mask.getpixel((x, y))
                if mask_value > 0:
                    # Use the mask value to determine the alpha
                    alpha = min(255, int(255 * (mask_value / 255.0)))
                    colored_ring.putpixel((x, y), (
                        highlight_color[0],
                        highlight_color[1],
                        highlight_color[2],
                        alpha
                    ))

        # Apply a very slight blur to soften the edge
        colored_ring = colored_ring.filter(ImageFilter.GaussianBlur(1))

        # Increase the brightness of the ring to make it glow
        # We'll do this by creating multiple blurred copies and adding them on top

        # First glow layer - slightly blurred
        glow_ring1 = colored_ring.copy()
        glow_ring1 = glow_ring1.filter(ImageFilter.GaussianBlur(2))

        # Second glow layer - more blurred for a wider glow
        glow_ring2 = colored_ring.copy()
        glow_ring2 = glow_ring2.filter(ImageFilter.GaussianBlur(4))

        # Create a new image to composite all the glows
        enhanced_ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Add the layers from bottom to top
        enhanced_ring.paste(glow_ring2, (0, 0), glow_ring2)  # Widest glow at bottom
        enhanced_ring.paste(glow_ring1, (0, 0), glow_ring1)  # Medium glow in middle
        enhanced_ring.paste(colored_ring, (0, 0), colored_ring)  # Sharp edge on top

        # Replace the colored ring with the enhanced version
        colored_ring = enhanced_ring

        # Composite the colored ring onto the result
        result = Image.alpha_composite(result, colored_ring)

        # Composite the planet on top of the result
        result = Image.alpha_composite(result, planet_image)

        return result
