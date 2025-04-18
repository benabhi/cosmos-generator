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

        # Create a high-resolution canvas for better quality
        # Working at 2x resolution for smoother edges
        hi_res_size = canvas_size * 2
        hi_res_result = Image.new("RGBA", (hi_res_size, hi_res_size), (0, 0, 0, 0))
        hi_res_draw = ImageDraw.Draw(hi_res_result)

        # Calculate center of the high-res image
        hi_res_center = hi_res_size // 2

        # Calculate the inner and outer radii of the halo
        # Create a gap of 2-3 pixels between the planet edge and the halo
        # Scale up for high resolution
        gap = 2  # Gap between planet and halo
        hi_res_inner_radius = (planet_radius + gap) * 2
        hi_res_outer_radius = hi_res_inner_radius + (thickness * 2)

        # Extract color components and ensure we have a vibrant, visible color
        r, g, b, a = color

        # Print the original color for debugging
        print(f"Original atmosphere color: R:{r}, G:{g}, B:{b}, A:{a}")

        # Force a minimum brightness to ensure visibility
        min_brightness = 100
        r = max(min_brightness, r)
        g = max(min_brightness, g)
        b = max(min_brightness, b)

        # Preserve the color's character but make it more vibrant
        # Find the dominant color channel
        max_channel = max(r, g, b)
        min_channel = min(r, g, b)

        # Calculate color intensity and boost it
        intensity_boost = 2.5

        # Boost each channel while preserving color relationships
        r = min(255, int(r * intensity_boost))
        g = min(255, int(g * intensity_boost))
        b = min(255, int(b * intensity_boost))

        # Print the enhanced color for debugging
        print(f"Enhanced halo color: R:{r}, G:{g}, B:{b}")

        # Create a two-layer halo for better definition
        # First layer: Main halo with original color
        main_halo_width = thickness * 2 * 0.7  # 70% of total thickness
        main_halo_inner = hi_res_inner_radius
        main_halo_outer = main_halo_inner + main_halo_width

        # Second layer: Outer glow with slightly different color
        glow_inner = main_halo_outer
        glow_outer = hi_res_outer_radius

        # Calculate alpha values based on intensity
        base_alpha = int(255 * self.halo_intensity)

        # Instead of drawing a filled ring and cutting out the center,
        # we'll draw multiple concentric circles with high opacity to create a solid ring
        # This approach gives us more control over the appearance

        # Calculate the number of circles to draw for the main halo
        main_halo_steps = max(10, int(main_halo_width / 2))

        # Draw the main halo as multiple concentric circles
        for i in range(main_halo_steps):
            # Calculate the current radius
            t = i / (main_halo_steps - 1)  # 0 to 1
            current_radius = main_halo_inner + (main_halo_outer - main_halo_inner) * t

            # Calculate alpha - higher in the middle of the ring
            if t < 0.3 or t > 0.7:
                # Edges of the ring - slightly lower alpha
                alpha_factor = 0.8
            else:
                # Middle of the ring - full alpha
                alpha_factor = 1.0

            # Create a very opaque color for the main halo
            alpha = int(base_alpha * alpha_factor)
            ring_color = (r, g, b, alpha)

            # Draw the circle with a thick outline
            outline_width = 3  # Thicker outline for better visibility
            hi_res_draw.ellipse(
                (hi_res_center - current_radius - outline_width/2, hi_res_center - current_radius - outline_width/2,
                 hi_res_center + current_radius + outline_width/2, hi_res_center + current_radius + outline_width/2),
                outline=ring_color, width=outline_width
            )

        # Create a separate layer for the outer glow for better blur control
        glow_layer = Image.new("RGBA", (hi_res_size, hi_res_size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        # Draw the outer glow (gradient ring) with more steps for smoother gradient
        steps = 30  # More steps for smoother gradient

        # Create a much more vibrant color for the glow - more ethereal and visible
        # Significantly enhance the color to make the second resplandor clearly visible
        glow_r = min(255, r + 50)
        glow_g = min(255, g + 50)
        glow_b = min(255, b + 80)  # Add more blue for ethereal effect

        # Print the glow color for debugging
        print(f"Outer glow color: R:{glow_r}, G:{glow_g}, B:{glow_b}")

        for i in range(steps):
            t = i / (steps - 1)  # 0 to 1
            current_radius = glow_inner + (glow_outer - glow_inner) * t

            # Calculate alpha for this step with a smoother falloff
            # Use a curve that creates a more visible outer glow
            if t < 0.3:
                # Inner part of the glow - stronger
                alpha_factor = 0.8 - (t * 0.5)
            else:
                # Outer part of the glow - gradual falloff
                alpha_factor = 0.65 * (1 - ((t - 0.3) / 0.7)) ** 1.2

            # Apply the blur amount parameter to control the glow intensity
            # Significantly increase the alpha to make the second resplandor more visible
            alpha = int(base_alpha * alpha_factor * self.blur_amount * 3.0)

            # Draw a circle with the calculated alpha and increased width for more visibility
            glow_color = (glow_r, glow_g, glow_b, alpha)
            outline_width = 2 if t < 0.5 else 1  # Thicker for inner part
            glow_draw.ellipse(
                (hi_res_center - current_radius - outline_width/2, hi_res_center - current_radius - outline_width/2,
                 hi_res_center + current_radius + outline_width/2, hi_res_center + current_radius + outline_width/2),
                outline=glow_color, width=outline_width
            )

        # Apply a much stronger blur to the glow layer to create a visible second resplandor
        # Significantly increase the blur amount to make it more diffuse and visible
        blur_amount = max(5.0, thickness * self.blur_amount * 4.0)
        print(f"Applying blur with strength: {blur_amount}")
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(blur_amount))

        # Composite the glow layer onto the result
        hi_res_result = Image.alpha_composite(hi_res_result, glow_layer)

        # Apply a slight blur to smooth the edges
        blur_radius = max(1.0, thickness * 0.3)
        hi_res_result = hi_res_result.filter(ImageFilter.GaussianBlur(blur_radius))

        # Resize back to original resolution with high-quality resampling
        result = hi_res_result.resize((canvas_size, canvas_size), Image.LANCZOS)

        # Composite the halo with the base image
        final_result = Image.alpha_composite(base_image.copy(), result)

        return final_result

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