"""
Atmosphere feature for planets.

This module provides the Atmosphere class, which handles the creation and application
of realistic atmospheric effects to planets, including scattering and limb brightening.
"""
from typing import Optional, Tuple, Any
import time
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

from cosmos_generator.core.color_palette import ColorPalette, RGBA
from cosmos_generator.utils.logger import logger
from cosmos_generator.core.interfaces import AtmosphereInterface, ColorPaletteInterface

# Type aliases
Color = Tuple[int, int, int]


class Atmosphere(AtmosphereInterface):
    """
    Atmosphere class for creating and applying realistic atmospheric effects to planets.

    This class handles the creation of atmospheric scattering, limb brightening, and color
    shifting effects around planets. It provides configurable parameters for controlling
    the appearance of the atmosphere.
    """

    def __init__(self,
                 seed: Optional[int] = None,
                 enabled: bool = True,
                 density: float = 0.5,
                 scattering: float = 0.7,
                 color_shift: float = 0.3,
                 color_palette: Optional[ColorPaletteInterface] = None):
        """
        Initialize the atmosphere with configurable parameters.

        Args:
            seed: Random seed for reproducible generation
            enabled: Whether the atmosphere is enabled
            density: Density of the atmosphere (0.0-1.0), affects thickness and opacity
            scattering: Intensity of light scattering effect (0.0-1.0)
            color_shift: Amount of color shifting in the atmosphere (0.0-1.0)
            color_palette: Optional color palette instance (will create one if not provided)
        """
        self.seed = seed
        self._enabled = enabled
        self.density = max(0.0, min(1.0, density))
        self.scattering = max(0.0, min(1.0, scattering))
        self.color_shift = max(0.0, min(1.0, color_shift))

        # Use provided color palette or create a new one
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=seed)

        # Store the last used color for logging
        self.last_color = None

    @property
    def enabled(self) -> bool:
        """Whether the atmosphere is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether the atmosphere is enabled."""
        self._enabled = value

    def apply_to_planet(self, planet_image: Image.Image, planet_type: str,
                        has_rings: bool = False, color: Optional[RGBA] = None,
                        base_color: Optional[Color] = None,
                        highlight_color: Optional[Color] = None) -> Image.Image:
        """
        Apply realistic atmospheric effects to a planet image.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet (used to get the default color if not provided)
            has_rings: Whether the planet has rings (affects atmosphere padding)
            color: Optional custom color for the atmosphere
            base_color: Optional base color of the planet (used to derive atmosphere color)
            highlight_color: Optional highlight color of the planet (used to derive atmosphere color)

        Returns:
            Planet image with realistic atmosphere applied
        """
        if not self.enabled:
            return planet_image

        start_time = time.time()
        try:
            # Get atmosphere color if not provided
            if color is None:
                if base_color is not None and highlight_color is not None:
                    # Use the provided planet colors to derive the atmosphere color
                    # Blend them with some transparency for the atmosphere
                    r = int((base_color[0] * 0.3 + highlight_color[0] * 0.7))
                    g = int((base_color[1] * 0.3 + highlight_color[1] * 0.7))
                    b = int((base_color[2] * 0.3 + highlight_color[2] * 0.7))
                    # Add some transparency (alpha value)
                    alpha = 75  # Default transparency
                    atmosphere_color = (r, g, b, alpha)
                else:
                    # Fallback to the old method if no planet colors are provided
                    atmosphere_color = self.color_palette.get_atmosphere_color(planet_type)
            else:
                atmosphere_color = color

            # Store the color for logging
            self.last_color = atmosphere_color

            # Ensure the planet image has an alpha channel
            if planet_image.mode != "RGBA":
                planet_image = planet_image.convert("RGBA")

            # Get the size of the planet image
            size = planet_image.width

            # Calculate padding based on density and whether the planet has rings
            # Usar valores muy pequeños para hacer la atmósfera muy angosta pero visible
            if has_rings:
                # For planets with rings, use a very small padding
                atmosphere_padding = int(size * 0.015 * (0.5 + self.density))
            else:
                # For planets without rings, use a slightly larger padding
                # but still keep it subtle
                atmosphere_padding = int(size * 0.02 * (0.5 + self.density))

            # Store the original atmosphere color (without color shift)
            # We'll apply color shift only to the atmosphere elements, not to the planet
            original_atmosphere_color = atmosphere_color

            # Apply color shift to the atmosphere color for the atmosphere elements
            shifted_atmosphere_color = self._apply_color_shift(atmosphere_color)

            # Create the main atmosphere with scattering effect
            # Use the shifted color for the atmosphere elements
            result = self._create_atmosphere(
                planet_image,
                shifted_atmosphere_color,
                atmosphere_padding,
                has_rings
            )

            duration_ms = (time.time() - start_time) * 1000

            # Log details about the atmosphere
            padding_percent = atmosphere_padding / (size // 2) * 100

            logger.log_step(
                "apply_atmosphere",
                duration_ms,
                f"Padding: {padding_percent:.1f}%, Density: {self.density:.2f}, " +
                f"Scattering: {self.scattering:.2f}, Color Shift: {self.color_shift:.2f}"
            )
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_atmosphere", duration_ms, f"Error: {str(e)}")
            raise

    def _apply_color_shift(self, color: RGBA) -> RGBA:
        """
        Apply color shift to the atmosphere color.

        Args:
            color: Original RGBA color tuple

        Returns:
            Modified RGBA color with shift applied
        """
        r, g, b, a = color

        # No shift if color_shift is 0
        if self.color_shift <= 0:
            return color

        # Determine the dominant color channel
        max_channel = max(r, g, b)

        if max_channel == 0:
            return color  # Avoid division by zero

        # Calculate ratios
        r_ratio = r / max_channel
        g_ratio = g / max_channel
        b_ratio = b / max_channel

        # Apply color shift based on planet type characteristics
        # Higher color_shift means more dramatic color changes
        # Don't scale down to make the effect more noticeable
        shift_factor = self.color_shift  # Use the full value for more dramatic effects

        # Enhance the dominant color and reduce others for more dramatic atmosphere
        if r >= g and r >= b:  # Red dominant (warm atmospheres)
            r = min(255, int(r * (1 + shift_factor * 0.3)))
            g = int(g * (1 - shift_factor * 0.1))
            b = int(b * (1 - shift_factor * 0.2))
        elif g >= r and g >= b:  # Green dominant
            g = min(255, int(g * (1 + shift_factor * 0.3)))
            r = int(r * (1 - shift_factor * 0.1))
            b = int(b * (1 - shift_factor * 0.1))
        elif b >= r and b >= g:  # Blue dominant (cool atmospheres)
            b = min(255, int(b * (1 + shift_factor * 0.3)))
            r = int(r * (1 - shift_factor * 0.2))
            g = int(g * (1 - shift_factor * 0.1))

        # Adjust alpha based on density
        adjusted_alpha = int(a * (0.7 + self.density * 0.6))

        return (r, g, b, min(255, adjusted_alpha))

    def _create_atmosphere(self,
                                planet_image: Image.Image,
                                color: RGBA,
                                padding: int,
                                has_rings: bool) -> Image.Image:
        # The has_rings parameter is used to adjust the scattering effect
        """
        Create a realistic atmosphere with scattering effect.

        Args:
            planet_image: Base planet image
            color: RGBA color tuple for the atmosphere
            padding: Padding around the planet for the atmosphere
            has_rings: Whether the planet has rings (affects certain parameters)

        Returns:
            Image with realistic atmospheric effects applied
        """
        # Get the size of the planet image
        size = planet_image.width

        # Create a canvas for the atmosphere with extra padding
        # Make sure we have enough space for the atmosphere and scattering effects
        # Use a larger canvas to ensure the atmosphere doesn't get cut off
        extra_padding = int(size * 0.1)  # Add 10% extra padding on each side
        canvas_size = size + (padding + extra_padding) * 2

        # Log the padding used
        logger.debug(f"Atmosphere padding: {padding}px + {extra_padding}px extra (canvas size: {canvas_size}px)", "atmosphere")

        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate center and planet radius
        center = canvas_size // 2
        planet_radius = size // 2

        # Create the base atmosphere layer
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
        # Calculate blur radius based on padding and density
        # Use a larger blur radius to make the desvanecimiento more noticeable
        blur_radius = max(2, int(padding * 0.8 * self.density))

        # Apply multiple blur passes for a more gradual fade-out effect
        for _ in range(2):
            atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))

        # Create the scattering effect (limb brightening)
        scattering_layer = self._create_scattering_effect(
            canvas_size,
            center,
            planet_radius,
            atmosphere_radius,
            color,
            has_rings
        )

        # Composite the base atmosphere and scattering effect
        result = Image.alpha_composite(result, atmosphere)

        # Only apply scattering if the parameter is > 0
        if self.scattering > 0:
            result = Image.alpha_composite(result, scattering_layer)

        # Create the atmosphere line (thin bright line at the edge of the planet)
        atmosphere_line = self._create_atmosphere_line(
            canvas_size,
            center,
            planet_radius,
            color
        )

        # Composite the atmosphere line
        result = Image.alpha_composite(result, atmosphere_line)

        # Paste the planet in the center
        planet_pos = (center - planet_radius, center - planet_radius)
        result.paste(planet_image, planet_pos, planet_image)

        return result

    def _create_scattering_effect(self,
                                 canvas_size: int,
                                 center: int,
                                 planet_radius: int,
                                 atmosphere_radius: int,
                                 color: RGBA,
                                 has_rings: bool) -> Image.Image:
        """
        Create the light scattering effect (limb brightening).

        Args:
            canvas_size: Size of the canvas
            center: Center point of the canvas
            planet_radius: Radius of the planet
            atmosphere_radius: Radius of the atmosphere
            color: RGBA color tuple for the atmosphere

        Returns:
            Image with scattering effect
        """
        # Create a new layer for the scattering effect
        scattering = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        scattering_draw = ImageDraw.Draw(scattering)

        # Extract and enhance color for scattering
        r, g, b, a = color

        # Make the scattering color much brighter to simulate light emission
        # Higher values create a more intense glow effect
        scattering_r = min(255, int(r * 2.5))
        scattering_g = min(255, int(g * 2.5))
        scattering_b = min(255, int(b * 2.5))

        # Calculate the scattering intensity based on the scattering parameter
        # Higher alpha makes the scattering more visible
        scattering_alpha = int(min(255, a * 3 * self.scattering))
        scattering_color = (scattering_r, scattering_g, scattering_b, scattering_alpha)

        # Calculate the thickness of the scattering effect
        # Make the scattering very thin but still visible
        # Use a very small base value to make it subtle
        base_thickness = planet_radius * 0.015 * (0.2 + self.scattering * 1.0)

        # Make the density parameter have a more noticeable effect on concentration
        # Higher density values will create a more concentrated effect
        density_factor = 1.0 - (self.density * 0.4)  # Stronger reduction for high density

        # Calculate final thickness with a minimum of 1 pixel
        scattering_thickness = max(1, int(base_thickness * density_factor))

        # Draw multiple concentric circles with decreasing opacity to create the scattering effect
        steps = 20
        for i in range(steps):
            # Calculate progress (0 to 1)
            t = i / (steps - 1)

            # Calculate current radius - concentrate near the planet's edge
            # Use a non-linear distribution to concentrate more at the edge
            if t < 0.5:
                # Inner half - concentrate at the planet's edge
                factor = t * 2  # 0 to 1
                current_radius = planet_radius + scattering_thickness * factor
            else:
                # Outer half - extend into the atmosphere, but limit the maximum extension
                factor = (t - 0.5) * 2  # 0 to 1
                base_extension = scattering_thickness

                # Calculate the maximum extension based on the planet radius
                # Use a muy pequeño porcentaje para hacer el scattering muy angosto pero visible
                max_extension_factor = 0.03  # 3% of the planet radius

                max_extension = planet_radius * max_extension_factor
                available_extension = min(atmosphere_radius - planet_radius - scattering_thickness, max_extension)

                additional_extension = available_extension * factor
                current_radius = planet_radius + base_extension + additional_extension

            # Calculate alpha - create a more dramatic fade-out effect
            # Use a non-linear curve for more visible desvanecimiento
            if t < 0.2:
                # Near the planet's edge - highest intensity
                alpha_factor = 1.0 - (t * 2.5)  # 1.0 to 0.5 (steeper drop)
            elif t < 0.5:
                # Middle region - medium intensity with faster drop-off
                alpha_factor = 0.5 - ((t - 0.2) * 1.2)  # 0.5 to 0.14
            else:
                # Outer region - very low intensity that fades to zero
                alpha_factor = 0.14 * (1 - ((t - 0.5) / 0.5))  # 0.14 to 0 (more gradual)

            # Apply the scattering parameter to the alpha
            alpha_factor *= self.scattering

            # Create color with adjusted alpha
            current_alpha = int(scattering_alpha * alpha_factor)
            current_color = (scattering_r, scattering_g, scattering_b, current_alpha)

            # Draw the circle
            scattering_draw.ellipse(
                (center - current_radius, center - current_radius,
                 center + current_radius, center + current_radius),
                outline=current_color, width=2
            )

        # Apply a slight blur to smooth the scattering effect
        blur_amount = max(1, int(3 * self.scattering))
        scattering = scattering.filter(ImageFilter.GaussianBlur(blur_amount))

        return scattering

    def _create_atmosphere_line(self,
                               canvas_size: int,
                               center: int,
                               planet_radius: int,
                               color: RGBA) -> Image.Image:
        """
        Create a thin bright line at the edge of the planet to simulate the atmosphere edge.

        Args:
            canvas_size: Size of the canvas
            center: Center point of the canvas
            planet_radius: Radius of the planet
            color: RGBA color tuple for the atmosphere

        Returns:
            Image with atmosphere line
        """
        # Create a new layer for the atmosphere line
        line_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_layer)

        # Extract and enhance color for the line
        r, g, b, a = color

        # Make the line color much brighter
        line_r = min(255, int(r * 2.0))
        line_g = min(255, int(g * 2.0))
        line_b = min(255, int(b * 2.0))

        # Calculate the line alpha based on the scattering parameter
        # Higher scattering means more visible line
        line_alpha = int(min(255, 150 * self.scattering))
        line_color = (line_r, line_g, line_b, line_alpha)

        # Draw the atmosphere line as a thin circle at the planet's edge
        # Slightly larger than the planet radius
        line_radius = planet_radius + 1
        line_width = max(1, int(2 * self.density))

        line_draw.ellipse(
            (center - line_radius, center - line_radius,
             center + line_radius, center + line_radius),
            outline=line_color, width=line_width
        )

        # Apply a slight blur to smooth the line
        blur_amount = max(1, int(2 * self.scattering))
        line_layer = line_layer.filter(ImageFilter.GaussianBlur(blur_amount))

        return line_layer
