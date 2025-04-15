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

        # Create a new image for the result (same size as planet)
        size = planet_image.width
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Create a mask for the planet
        planet_mask = Image.new("L", (size, size), 0)
        planet_draw = ImageDraw.Draw(planet_mask)
        planet_draw.ellipse((0, 0, size-1, size-1), fill=255)

        # Create a slightly larger mask for the atmosphere edge
        # Make the difference more significant for a visible line
        atmosphere_size = int(size * (1.0 + 0.04 * intensity))  # Outer edge
        atmosphere_mask = Image.new("L", (atmosphere_size, atmosphere_size), 0)
        atmosphere_draw = ImageDraw.Draw(atmosphere_mask)
        atmosphere_draw.ellipse((0, 0, atmosphere_size-1, atmosphere_size-1), fill=255)

        # Resize to match the planet size
        atmosphere_mask = atmosphere_mask.resize((size, size), Image.LANCZOS)

        # Create the ring by subtracting the planet mask from the atmosphere mask
        ring_mask = ImageChops.subtract(atmosphere_mask, planet_mask)

        # Calculate light direction
        light_rad = math.radians(light_angle)
        light_x = math.cos(light_rad)
        light_y = -math.sin(light_rad)  # Negative because y increases downward in images

        # Create a light mask with a gradient based on light direction
        light_mask = Image.new("L", (size, size), 0)
        light_array = np.zeros((size, size), dtype=np.uint8)

        center_x, center_y = size // 2, size // 2
        radius = size // 2

        # Fill the light mask with a gradient based on light direction
        for y in range(size):
            for x in range(size):
                # Calculate position relative to center
                dx = (x - center_x) / radius
                dy = (y - center_y) / radius
                distance = math.sqrt(dx*dx + dy*dy)

                # Skip if too far from the edge
                if distance < 0.9 or distance > 1.1:
                    continue

                # Calculate surface normal at this point
                # For a sphere, the normal is just the normalized vector from center to point
                nx, ny = dx, dy  # Normalized direction from center

                # Calculate dot product with light direction (2D)
                dot = nx * light_x + ny * light_y

                # Apply lighting factor
                if dot < 0:
                    # Point is facing away from light
                    factor = 0.2  # Darker in shadow
                else:
                    # Brighter in light
                    factor = 0.2 + 0.8 * (dot ** 0.5)

                # Set light mask value
                light_array[y, x] = min(255, int(255 * factor))

        # Convert back to image
        light_mask = Image.fromarray(light_array)

        # Apply the light mask to the ring mask
        lit_ring_mask = ImageChops.multiply(ring_mask, light_mask)

        # Create a much brighter color for the edge highlight
        highlight_color = (
            min(255, int(r * 3.0)),  # Much brighter red
            min(255, int(g * 3.0)),  # Much brighter green
            min(255, int(b * 3.0)),  # Much brighter blue
            min(255, 255)            # Full opacity for visibility
        )

        # Create a new layer for the atmosphere ring
        atmosphere_ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Draw the atmosphere ring with the highlight color
        for y in range(size):
            for x in range(size):
                mask_value = lit_ring_mask.getpixel((x, y))
                if mask_value > 0:
                    # Scale the alpha by the mask value
                    alpha = min(255, int(highlight_color[3] * (mask_value / 255.0)))
                    atmosphere_ring.putpixel((x, y), (
                        highlight_color[0],
                        highlight_color[1],
                        highlight_color[2],
                        alpha
                    ))

        # Apply a very slight blur to soften the edge but keep it defined
        atmosphere_ring = atmosphere_ring.filter(ImageFilter.GaussianBlur(1))

        # Create the final image by compositing the planet and atmosphere ring
        result = Image.alpha_composite(result, atmosphere_ring)
        result = Image.alpha_composite(result, planet_image)

        return result
