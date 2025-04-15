"""
Atmospheric effects for celestial bodies.
"""
from typing import Tuple, Optional
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

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
        Apply atmospheric glow to a planet image with a smooth gradient from the planet's edge.
        The atmosphere will be darker in shadowed areas and brighter in lit areas.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere
            light_angle: Angle of the light source in degrees

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

        # Extract color components
        r, g, b, a = atmosphere_color

        # Get the size of the planet image
        size = planet_image.width

        # Calculate the atmospheric thickness based on intensity
        # Use a larger factor for more visible atmosphere (5-20% of the planet size)
        atmo_thickness = int(size * 0.05 + size * 0.15 * intensity)
        atmosphere_size = size + atmo_thickness * 2

        # Create a new image for the result (large enough for the atmosphere)
        result = Image.new("RGBA", (atmosphere_size, atmosphere_size), (0, 0, 0, 0))

        # Calculate the center of the atmosphere
        center_x, center_y = atmosphere_size // 2, atmosphere_size // 2

        # Create a radial gradient for the atmosphere with smooth falloff
        gradient = Image.new("RGBA", (atmosphere_size, atmosphere_size), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)

        # Draw a filled circle for the planet area (will be transparent later)
        planet_radius = size // 2
        planet_area = (
            center_x - planet_radius,
            center_y - planet_radius,
            center_x + planet_radius,
            center_y + planet_radius
        )
        gradient_draw.ellipse(planet_area, fill=(0, 0, 0, 0))

        # Create atmosphere gradient with multiple layers for smooth falloff
        atmo_radius = planet_radius + atmo_thickness

        # Draw concentric circles with decreasing opacity
        num_layers = 15  # More layers = smoother gradient
        for i in range(num_layers):
            # Calculate the current radius and opacity
            current_radius = planet_radius + (atmo_thickness * (i + 1) / num_layers)
            # Opacity decreases exponentially from the planet edge (start higher for intense atmospheres)
            base_opacity = 0.3 + 0.7 * intensity  # Base opacity depends on intensity
            opacity_factor = math.exp(-3.0 * i / num_layers)  # Exponential falloff
            current_opacity = int(base_opacity * opacity_factor * a)

            current_color = (r, g, b, current_opacity)

            # Draw the current layer
            ellipse_bounds = (
                center_x - current_radius,
                center_y - current_radius,
                center_x + current_radius,
                center_y + current_radius
            )
            gradient_draw.ellipse(ellipse_bounds, fill=current_color)

        # Apply lighting effect to the atmosphere
        # Calculate light direction
        light_rad = math.radians(light_angle)
        light_x = math.cos(light_rad)
        light_y = -math.sin(light_rad)  # Negative because y increases downward in images

        # Create a light mask with a gradient based on light direction
        light_mask = Image.new("L", (atmosphere_size, atmosphere_size), 0)
        light_draw = ImageDraw.Draw(light_mask)

        # Draw a filled ellipse for the light mask - lighter on the lit side
        light_draw.ellipse((0, 0, atmosphere_size-1, atmosphere_size-1), fill=255)
        light_data = np.array(light_mask)

        # Apply lighting based on the angle
        for y in range(atmosphere_size):
            for x in range(atmosphere_size):
                # Calculate position relative to center
                dx = (x - center_x) / atmo_radius
                dy = (y - center_y) / atmo_radius

                # Skip if outside the maximum atmosphere radius
                if dx*dx + dy*dy > 1.25:  # Add some margin
                    continue

                # Calculate dot product with light direction
                dot = dx * light_x + dy * light_y

                # Apply lighting factor
                if dot < 0:
                    # Point is facing away from light
                    factor = 0.5  # Darker in shadow but still visible
                else:
                    # Brighter in light
                    factor = 0.5 + 0.5 * dot

                # Apply to the light mask
                light_data[y, x] = int(light_data[y, x] * factor)

        # Convert back to image
        light_mask = Image.fromarray(light_data)

        # Apply the light mask to the gradient
        lit_gradient = ImageChops.multiply(gradient.split()[3], light_mask)

        # Recreate the atmosphere with the lit alpha channel
        atmosphere = Image.new("RGBA", (atmosphere_size, atmosphere_size), (0, 0, 0, 0))
        r_channel, g_channel, b_channel, _ = gradient.split()
        atmosphere = Image.merge("RGBA", (r_channel, g_channel, b_channel, lit_gradient))

        # Add a subtle glow effect
        atmosphere_glow = atmosphere.filter(ImageFilter.GaussianBlur(3))
        atmosphere = ImageChops.add(atmosphere, atmosphere_glow)

        # Create a mask for the planet
        planet_mask = Image.new("L", (size, size), 255)
        planet_mask_draw = ImageDraw.Draw(planet_mask)
        planet_mask_draw.ellipse((0, 0, size-1, size-1), fill=0)

        # Paste the planet in the center of the atmosphere
        paste_pos = (center_x - planet_radius, center_y - planet_radius)
        result.paste(atmosphere, (0, 0), atmosphere)
        result.paste(planet_image, paste_pos, planet_image)

        return result

    def apply_simple_atmosphere(self, planet_image: Image.Image, planet_type: str,
                              intensity: float = 0.5, color: Optional[RGBA] = None) -> Image.Image:
        """
        Apply a simple atmospheric glow around the planet.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere

        Returns:
            Planet image with simple atmospheric glow
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Get atmosphere color
        if color is None:
            atmosphere_color = self.color_palette.get_atmosphere_color(planet_type)
        else:
            atmosphere_color = color

        # Get the size of the planet image
        size = planet_image.width

        # Create a mask for the planet
        planet_mask = Image.new("L", (size, size), 0)
        planet_draw = ImageDraw.Draw(planet_mask)
        planet_draw.ellipse((0, 0, size-1, size-1), fill=255)

        # Create a new image for the atmosphere
        atmosphere = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        atmosphere_draw = ImageDraw.Draw(atmosphere)
        atmosphere_draw.ellipse((0, 0, size-1, size-1), fill=atmosphere_color)

        # Apply multiple blur passes for a nice glow effect
        blur_radius = int(5 + 15 * intensity)  # Scale blur with intensity
        for _ in range(3):  # Multiple passes create a smoother glow
            atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))

        # Composite the planet on top of the atmosphere
        result = Image.alpha_composite(atmosphere, planet_image)

        return result