"""
Atmosphere feature for planets.

This module provides the Atmosphere class, which handles the creation and application
of atmospheric effects to planets, including glow and halo effects.
"""
from typing import Tuple, Optional
import time
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

from cosmos_generator.core.color_palette import ColorPalette, RGBA
from cosmos_generator.utils.logger import logger


class Atmosphere:
    """
    Atmosphere class for creating and applying atmospheric effects to planets.

    This class handles the creation of atmospheric glow and halo effects around planets.
    It provides configurable parameters for controlling the appearance of the atmosphere.
    """

    def __init__(self,
                 seed: Optional[int] = None,
                 enabled: bool = True,
                 glow_intensity: float = 0.5,
                 halo_intensity: float = 0.7,
                 halo_thickness: int = 3,
                 blur_amount: float = 0.5):
        """
        Initialize the atmosphere with configurable parameters.

        Args:
            seed: Random seed for reproducible generation
            enabled: Whether the atmosphere is enabled
            glow_intensity: Intensity of the atmospheric glow (0.0-1.0)
            halo_intensity: Intensity of the halo effect (0.0-1.0)
            halo_thickness: Thickness of the halo in pixels (1-10)
            blur_amount: Amount of blur to apply to the atmosphere (0.0-1.0)
        """
        self.seed = seed
        self.enabled = enabled
        self.glow_intensity = max(0.0, min(1.0, glow_intensity))
        self.halo_intensity = max(0.0, min(1.0, halo_intensity))
        self.halo_thickness = max(1, min(10, halo_thickness))
        self.blur_amount = max(0.0, min(1.0, blur_amount))

        # Initialize color palette for getting atmosphere colors
        self.color_palette = ColorPalette(seed=seed)

        # Store the last used color for logging
        self.last_color = None

    def apply_to_planet(self, planet_image: Image.Image, planet_type: str, has_rings: bool = False, color: Optional[RGBA] = None) -> Image.Image:
        """
        Apply atmospheric effects to a planet image.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet (used to get the default color if not provided)
            has_rings: Whether the planet has rings (affects atmosphere padding)
            color: Optional custom color for the atmosphere

        Returns:
            Planet image with atmosphere applied
        """
        if not self.enabled:
            return planet_image

        start_time = time.time()
        try:
            # Get atmosphere color if not provided
            if color is None:
                atmosphere_color = self.color_palette.get_atmosphere_color(planet_type)
            else:
                atmosphere_color = color

            # Store the color for logging
            self.last_color = atmosphere_color

            # Ensure the planet image has an alpha channel
            if planet_image.mode != "RGBA":
                planet_image = planet_image.convert("RGBA")

            # Adjust color intensity based on glow_intensity
            r, g, b, a = atmosphere_color
            adjusted_alpha = int(a * (0.5 + self.glow_intensity * 1.5))  # Scale alpha by glow intensity
            atmosphere_color = (r, g, b, min(255, adjusted_alpha))

            # Get the size of the planet image
            size = planet_image.width

            # Calculate atmosphere padding based on whether the planet has rings
            # Use smaller padding for planets with rings to avoid interfering with them
            if has_rings:
                atmosphere_padding = int(size * 0.01 * (0.5 + self.glow_intensity))
            else:
                atmosphere_padding = int(size * 0.02 * (0.5 + self.glow_intensity))

            # Create the atmosphere glow
            result = self._create_atmosphere_glow(
                planet_image,
                atmosphere_color,
                atmosphere_padding,
                has_rings
            )

            # Create and apply the halo if intensity > 0
            if self.halo_intensity > 0:
                result = self._create_halo(
                    result,
                    atmosphere_color,
                    size // 2,  # planet radius
                    self.halo_thickness
                )

            duration_ms = (time.time() - start_time) * 1000
            # Log details about the atmosphere
            padding_percent = atmosphere_padding / (size // 2) * 100
            blur_value = self.blur_amount
            if has_rings:
                blur_value *= 0.5  # Reduce blur for planets with rings

            # Calculate actual blur radius based on padding and blur_amount
            blur_radius = max(1, int(atmosphere_padding * blur_value))

            logger.log_step(
                "apply_atmosphere",
                duration_ms,
                f"Padding: {padding_percent:.1f}%, Glow: {self.glow_intensity:.2f}, " +
                f"Halo: {self.halo_intensity:.2f}, Thickness: {self.halo_thickness}px, " +
                f"Blur: {blur_radius}px"
            )
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_atmosphere", duration_ms, f"Error: {str(e)}")
            raise

    def _create_atmosphere_glow(self,
                               planet_image: Image.Image,
                               color: tuple,
                               padding: int,
                               has_rings: bool) -> Image.Image:
        """
        Create the atmospheric glow effect.

        Args:
            planet_image: Base planet image
            color: RGBA color tuple for the atmosphere
            padding: Padding around the planet for the atmosphere
            has_rings: Whether the planet has rings (affects blur amount)

        Returns:
            Image with atmospheric glow applied
        """
        # Get the size of the planet image
        size = planet_image.width

        # Create a canvas for the atmosphere
        canvas_size = size + padding * 2
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate center and planet radius
        center = canvas_size // 2
        planet_radius = size // 2

        # Create the atmosphere layer
        atmosphere = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        atmosphere_draw = ImageDraw.Draw(atmosphere)

        # Draw the atmosphere as a larger circle
        atmosphere_radius = planet_radius + padding
        atmosphere_draw.ellipse(
            (center - atmosphere_radius, center - atmosphere_radius,
             center + atmosphere_radius, center + atmosphere_radius),
            fill=color
        )

        # Apply blur for a nice glow effect
        # Calculate blur radius based on padding and blur_amount
        if has_rings:
            # Use smaller blur for planets with rings
            blur_radius = max(1, int(padding * self.blur_amount * 0.5))
        else:
            blur_radius = max(1, int(padding * self.blur_amount))

        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))

        # Paste the atmosphere onto the result
        result.paste(atmosphere, (0, 0), atmosphere)

        # Paste the planet in the center
        planet_pos = (center - planet_radius, center - planet_radius)
        result.paste(planet_image, planet_pos, planet_image)

        return result

    def _create_halo(self,
                    base_image: Image.Image,
                    color: tuple,
                    planet_radius: int,
                    thickness: int) -> Image.Image:
        """
        Create a halo effect around the planet.

        Args:
            base_image: Base image with planet (and possibly atmosphere glow)
            color: RGBA color tuple for the halo
            planet_radius: Radius of the planet in pixels
            thickness: Thickness of the halo in pixels

        Returns:
            Image with halo applied
        """
        # Get the size of the base image
        canvas_size = base_image.width

        # Create a larger canvas for the halo to avoid edge artifacts
        halo_canvas_size = canvas_size + 10
        halo_center = halo_canvas_size // 2

        # Create two images: one for the inner circle and one for the outer circle
        inner_circle = Image.new("L", (halo_canvas_size, halo_canvas_size), 0)
        outer_circle = Image.new("L", (halo_canvas_size, halo_canvas_size), 0)

        # Create drawing objects
        inner_draw = ImageDraw.Draw(inner_circle)
        outer_draw = ImageDraw.Draw(outer_circle)

        # Set up the halo parameters
        # Make the inner radius slightly smaller to ensure it overlaps with the planet edge
        # This helps prevent gaps between the halo and the planet due to the spherical distortion
        inner_radius = planet_radius - 1  # Slightly smaller to ensure overlap
        outer_radius = planet_radius + thickness  # Outer edge of halo

        # Draw filled circles (not outlines) for clean edges
        inner_draw.ellipse(
            (halo_center - inner_radius, halo_center - inner_radius,
             halo_center + inner_radius, halo_center + inner_radius),
            fill=255
        )

        outer_draw.ellipse(
            (halo_center - outer_radius, halo_center - outer_radius,
             halo_center + outer_radius, halo_center + outer_radius),
            fill=255
        )

        # Create the halo by subtracting the inner circle from the outer circle
        # This creates a perfect ring with clean edges
        halo_mask = ImageChops.subtract(outer_circle, inner_circle)

        # Apply a very small blur for anti-aliasing only
        # Just enough to smooth the edges without creating artifacts
        blur_amount = 0.3  # Minimal blur for clean edges
        halo_mask = halo_mask.filter(ImageFilter.GaussianBlur(blur_amount))

        # Create the colored halo with the mask
        halo = Image.new("RGBA", (halo_canvas_size, halo_canvas_size), (0, 0, 0, 0))
        halo_array = np.array(halo)
        mask_array = np.array(halo_mask)

        # Extract color components
        r, g, b, a = color

        # Adjust alpha based on halo_intensity
        a = int(a * self.halo_intensity)

        # Apply the color with the mask
        for y in range(halo_canvas_size):
            for x in range(halo_canvas_size):
                if mask_array[y, x] > 0:
                    # Use the mask value as the alpha
                    alpha = min(255, int(mask_array[y, x] * self.halo_intensity))
                    halo_array[y, x] = [r, g, b, alpha]

        # Convert back to PIL Image
        halo = Image.fromarray(halo_array)

        # Crop the halo to match the canvas size
        crop_offset = (halo_canvas_size - canvas_size) // 2
        halo = halo.crop((crop_offset, crop_offset,
                         crop_offset + canvas_size,
                         crop_offset + canvas_size))

        # Composite the halo onto the result
        result = Image.alpha_composite(base_image, halo)

        return result

    # Legacy methods for backward compatibility
    def apply_atmosphere(self, planet_image: Image.Image, planet_type: str,
                        intensity: float = 0.5, color: Optional[RGBA] = None,
                        light_angle: float = 45.0) -> Image.Image:
        """
        Legacy method for backward compatibility.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere
            light_angle: Angle of the light source in degrees

        Returns:
            Planet image with atmospheric glow
        """
        # Set parameters based on intensity
        self.glow_intensity = intensity
        self.halo_intensity = intensity
        self.blur_amount = 0.5 + intensity * 0.5

        # Call the new method
        return self.apply_to_planet(planet_image, planet_type, False, color)

    def apply_simple_atmosphere(self, planet_image: Image.Image, planet_type: str,
                              intensity: float = 0.5, color: Optional[RGBA] = None) -> Image.Image:
        """
        Legacy method for backward compatibility.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            intensity: Intensity of the atmospheric effect (0.0 to 1.0)
            color: Optional custom color for the atmosphere

        Returns:
            Planet image with simple atmospheric glow
        """
        # Set parameters based on intensity
        self.glow_intensity = intensity
        self.halo_intensity = 0.0  # No halo for simple atmosphere
        self.blur_amount = 0.5 + intensity * 0.5

        # Call the new method
        return self.apply_to_planet(planet_image, planet_type, False, color)