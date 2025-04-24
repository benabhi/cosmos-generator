"""
Atmosphere feature for planets.

This module provides the Atmosphere class, which handles the creation and application
of atmospheric effects to planets, including glow and halo effects.
"""
from typing import Optional, Tuple
import time
from PIL import Image, ImageDraw, ImageFilter

from cosmos_generator.core.color_palette import ColorPalette, RGBA
from cosmos_generator.utils.logger import logger
from cosmos_generator.core.interfaces import AtmosphereInterface, ColorPaletteInterface

# Type aliases
Color = Tuple[int, int, int]


class Atmosphere(AtmosphereInterface):
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
                 blur_amount: float = 0.5,
                 color_palette: Optional[ColorPaletteInterface] = None):
        """
        Initialize the atmosphere with configurable parameters.

        Args:
            seed: Random seed for reproducible generation
            enabled: Whether the atmosphere is enabled
            glow_intensity: Intensity of the atmospheric glow (0.0-1.0)
            halo_intensity: Intensity of the halo effect (0.0-1.0)
            halo_thickness: Thickness of the halo in pixels (1-10)
            blur_amount: Amount of blur to apply to the atmosphere (0.0-1.0)
            color_palette: Optional color palette instance (will create one if not provided)
        """
        self.seed = seed
        self._enabled = enabled
        self.glow_intensity = max(0.0, min(1.0, glow_intensity))
        self.halo_intensity = max(0.0, min(1.0, halo_intensity))
        self.halo_thickness = max(1, min(10, halo_thickness))
        self.blur_amount = max(0.0, min(1.0, blur_amount))

        # Use provided color palette or create a new one
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=seed)

    @property
    def enabled(self) -> bool:
        """Whether the atmosphere is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether the atmosphere is enabled."""
        self._enabled = value

        # Store the last used color for logging
        self.last_color = None

    def apply_to_planet(self, planet_image: Image.Image, planet_type: str, has_rings: bool = False, color: Optional[RGBA] = None, base_color: Optional[Color] = None, highlight_color: Optional[Color] = None) -> Image.Image:
        """
        Apply atmospheric effects to a planet image.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet (used to get the default color if not provided)
            has_rings: Whether the planet has rings (affects atmosphere padding)
            color: Optional custom color for the atmosphere
            base_color: Optional base color of the planet (used to derive atmosphere color)
            highlight_color: Optional highlight color of the planet (used to derive atmosphere color)

        Returns:
            Planet image with atmosphere applied
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

            # Adjust color intensity based on glow_intensity
            r, g, b, a = atmosphere_color
            adjusted_alpha = int(a * (0.5 + self.glow_intensity * 1.5))  # Scale alpha by glow intensity
            atmosphere_color = (r, g, b, min(255, adjusted_alpha))

            # Get the size of the planet image
            size = planet_image.width

            # Calculate atmosphere padding based on whether the planet has rings
            # For both types of planets, use a consistent padding to ensure the atmosphere isn't cut off
            # This ensures there's enough space for the second halo (blur lumínico)
            if has_rings:
                # For planets with rings, use a slightly larger padding to prevent cutting at the edges
                # Increased from 0.015 to 0.025 to fix the issue with atmosphere being cut off
                atmosphere_padding = int(size * 0.025 * (0.5 + self.glow_intensity))
            else:
                # For planets without rings, use a larger padding
                # Increased from 0.03 to 0.04 to fix the issue with atmosphere being cut off
                atmosphere_padding = int(size * 0.04 * (0.5 + self.glow_intensity))

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
        # Increase the size multiplier to ensure there's enough space for the diffuse glow
        hi_res_size = canvas_size * 2

        # Create a canvas with extra padding to ensure the diffuse glow has room to spread
        # This prevents the glow from being cut off at the edges
        extra_padding = int(thickness * 4 * self.blur_amount)  # Scale padding with blur and thickness
        hi_res_padded_size = hi_res_size + extra_padding * 2

        # Create the result image with the padded size
        hi_res_result = Image.new("RGBA", (hi_res_padded_size, hi_res_padded_size), (0, 0, 0, 0))
        hi_res_draw = ImageDraw.Draw(hi_res_result)

        # Calculate center of the high-res image with padding
        hi_res_center = hi_res_padded_size // 2

        # Calculate the inner and outer radii of the halo
        # Create a gap of 2-3 pixels between the planet edge and the halo
        # Scale up for high resolution
        gap = 2  # Gap between planet and halo
        hi_res_inner_radius = (planet_radius + gap) * 2
        hi_res_outer_radius = hi_res_inner_radius + (thickness * 2)

        # Extract color components and enhance the color for better visibility
        r, g, b, a = color

        # Log the original color for debugging
        logger.debug(f"Atmosphere color: R:{r}, G:{g}, B:{b}, A:{a}", "atmosphere")

        # Enhance the color for better visibility
        r, g, b = self._enhance_halo_color(r, g, b)

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

        # Create TWO separate layers for the outer glow:
        # 1. A sharp glow layer for the visible halo
        # 2. A diffuse glow layer for the second resplandor (blur effect)
        # Use the same size as the main canvas (hi_res_padded_size) for all layers
        sharp_glow_layer = Image.new("RGBA", (hi_res_padded_size, hi_res_padded_size), (0, 0, 0, 0))
        sharp_glow_draw = ImageDraw.Draw(sharp_glow_layer)

        diffuse_glow_layer = Image.new("RGBA", (hi_res_padded_size, hi_res_padded_size), (0, 0, 0, 0))
        diffuse_glow_draw = ImageDraw.Draw(diffuse_glow_layer)

        # Draw the outer glow (gradient ring) with more steps for smoother gradient
        steps = 30  # More steps for smoother gradient

        # Create colors for both glow layers
        # For the sharp glow, use the same color as the main halo to maintain consistency
        sharp_glow_r, sharp_glow_g, sharp_glow_b = r, g, b

        # For the diffuse glow (second resplandor), use a much more vibrant and visible color
        # Make it significantly brighter and more saturated to ensure visibility after blur
        # Preserve the color character but make it more luminous

        # First, determine which channel is dominant to understand the color character
        is_red_dominant = r >= g and r >= b
        is_green_dominant = g >= r and g >= b
        is_blue_dominant = b >= r and b >= g

        if is_red_dominant:
            # For reddish atmospheres (desert planets), enhance the red glow
            diffuse_glow_r = 255  # Maximum red
            diffuse_glow_g = min(255, g + 50)
            diffuse_glow_b = min(255, b + 70)
        elif is_blue_dominant:
            # For bluish atmospheres (ocean planets), enhance the blue glow
            diffuse_glow_r = min(255, r + 50)
            diffuse_glow_g = min(255, g + 70)
            diffuse_glow_b = 255  # Maximum blue
        elif is_green_dominant:
            # For greenish atmospheres, enhance the green glow
            diffuse_glow_r = min(255, r + 50)
            diffuse_glow_g = 255  # Maximum green
            diffuse_glow_b = min(255, b + 70)
        else:
            # For balanced colors, make it brighter overall
            diffuse_glow_r = min(255, r + 70)
            diffuse_glow_g = min(255, g + 70)
            diffuse_glow_b = min(255, b + 90)

        # Log the glow colors for debugging
        logger.debug(f"Sharp glow color: R:{sharp_glow_r}, G:{sharp_glow_g}, B:{sharp_glow_b}", "atmosphere")
        logger.debug(f"Diffuse glow color: R:{diffuse_glow_r}, G:{diffuse_glow_g}, B:{diffuse_glow_b}", "atmosphere")

        # Draw both glow layers with different characteristics
        for i in range(steps):
            t = i / (steps - 1)  # 0 to 1
            current_radius = glow_inner + (glow_outer - glow_inner) * t

            # Calculate alpha factors for both layers
            if t < 0.3:
                # Inner part of the glow - stronger
                sharp_alpha_factor = 0.9 - (t * 0.5)  # Stronger for sharp glow
                diffuse_alpha_factor = 0.8 - (t * 0.5)  # Slightly weaker for diffuse glow
            else:
                # Outer part of the glow - gradual falloff
                sharp_alpha_factor = 0.7 * (1 - ((t - 0.3) / 0.7)) ** 1.5  # Faster falloff for sharp
                diffuse_alpha_factor = 0.65 * (1 - ((t - 0.3) / 0.7)) ** 1.0  # Slower falloff for diffuse

            # Calculate final alpha values
            # Sharp glow has higher alpha but less blur
            sharp_alpha = int(base_alpha * sharp_alpha_factor * 1.5)

            # Diffuse glow has lower alpha but more blur - scaled by blur_amount parameter
            diffuse_alpha = int(base_alpha * diffuse_alpha_factor * self.blur_amount * 3.0)

            # Draw the sharp glow (visible halo line)
            sharp_color = (sharp_glow_r, sharp_glow_g, sharp_glow_b, sharp_alpha)
            outline_width = 2 if t < 0.5 else 1  # Thicker for inner part
            sharp_glow_draw.ellipse(
                (hi_res_center - current_radius - outline_width/2, hi_res_center - current_radius - outline_width/2,
                 hi_res_center + current_radius + outline_width/2, hi_res_center + current_radius + outline_width/2),
                outline=sharp_color, width=outline_width
            )

            # For the diffuse glow (second resplandor), create a much wider and more visible area
            # Draw for all positions to create a complete, continuous glow effect
            # Calculate a dynamic ring width that's wider for the middle positions
            if t < 0.6:  # Draw for 60% of the range to create a more visible glow
                # Calculate a more subtle ring for the diffuse glow
                # Make it wider in the middle for a natural light distribution, but more subtle
                base_ring_width = 12  # Reduced base width for subtlety
                if t < 0.2:
                    # Near the inner edge - medium width
                    ring_width = base_ring_width * 1.2
                elif t < 0.4:
                    # Middle area - maximum width
                    ring_width = base_ring_width * 1.5
                else:
                    # Outer area - gradually decreasing width
                    ring_width = base_ring_width * (1.0 - ((t - 0.4) / 0.2))

                inner_radius = current_radius - ring_width
                outer_radius = current_radius + ring_width

                # Calculate a much more subtle alpha for the diffuse glow
                # Use significantly lower boost factors for a more diffuse, less solid effect
                if t < 0.2:
                    # Inner part - light alpha
                    boost_factor = 1.2
                elif t < 0.4:
                    # Middle part - very light alpha
                    boost_factor = 0.9
                else:
                    # Outer part - extremely light alpha
                    boost_factor = 0.6

                # Apply the boost factor to the alpha
                boosted_alpha = int(diffuse_alpha * boost_factor)
                # Ensure alpha doesn't exceed 255
                boosted_alpha = min(255, boosted_alpha)

                # Create a filled ring by drawing two circles
                diffuse_color = (diffuse_glow_r, diffuse_glow_g, diffuse_glow_b, boosted_alpha)

                # Draw outer circle
                diffuse_glow_draw.ellipse(
                    (hi_res_center - outer_radius, hi_res_center - outer_radius,
                     hi_res_center + outer_radius, hi_res_center + outer_radius),
                    fill=diffuse_color, outline=None
                )

                # Cut out inner circle to create a ring
                diffuse_glow_draw.ellipse(
                    (hi_res_center - inner_radius, hi_res_center - inner_radius,
                     hi_res_center + inner_radius, hi_res_center + inner_radius),
                    fill=(0, 0, 0, 0), outline=None
                )

        # Apply different blur amounts to each glow layer

        # For the sharp glow (visible halo line), apply minimal blur to keep it defined
        sharp_blur = max(1.0, thickness * 0.3)
        logger.debug(f"Applying sharp glow blur: {sharp_blur:.1f}px", "atmosphere")
        sharp_glow_layer = sharp_glow_layer.filter(ImageFilter.GaussianBlur(sharp_blur))

        # For the diffuse glow (second resplandor), apply a much stronger blur
        # Use a large blur radius to create a very diffuse, ethereal glow effect
        # The blur amount is critical - we want it to be very diffuse but still slightly visible
        diffuse_blur = max(12.0, thickness * self.blur_amount * 5.0)
        logger.debug(f"Applying diffuse glow blur: {diffuse_blur:.1f}px", "atmosphere")

        # Apply the blur in three stages for a more diffuse, ethereal effect
        # First stage: Apply a moderate blur to soften the initial shape
        diffuse_glow_layer = diffuse_glow_layer.filter(ImageFilter.GaussianBlur(diffuse_blur * 0.3))

        # Second stage: Apply a stronger blur to create more diffusion
        diffuse_glow_layer = diffuse_glow_layer.filter(ImageFilter.GaussianBlur(diffuse_blur * 0.5))

        # Third stage: Apply a final light blur to smooth out any remaining artifacts
        diffuse_glow_layer = diffuse_glow_layer.filter(ImageFilter.GaussianBlur(diffuse_blur * 0.2))

        # Composite the layers in the correct order:
        # 1. First the diffuse glow (second resplandor)
        hi_res_result = Image.alpha_composite(hi_res_result, diffuse_glow_layer)

        # 2. Then the sharp glow (visible halo line)
        hi_res_result = Image.alpha_composite(hi_res_result, sharp_glow_layer)

        # Apply a very slight final blur to smooth any remaining artifacts
        final_blur = max(0.5, thickness * 0.1)
        hi_res_result = hi_res_result.filter(ImageFilter.GaussianBlur(final_blur))

        # Calculate the crop area to get back to the original hi-res size
        crop_left = (hi_res_padded_size - hi_res_size) // 2
        crop_top = (hi_res_padded_size - hi_res_size) // 2
        crop_right = crop_left + hi_res_size
        crop_bottom = crop_top + hi_res_size

        # Crop the image to remove the extra padding
        hi_res_cropped = hi_res_result.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Resize back to original resolution with high-quality resampling
        result = hi_res_cropped.resize((canvas_size, canvas_size), Image.LANCZOS)

        # Composite the halo with the base image
        final_result = Image.alpha_composite(base_image.copy(), result)

        return final_result

    def _enhance_halo_color(self, r: int, g: int, b: int) -> tuple:
        """
        Enhance a color for better visibility in the halo effect.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)

        Returns:
            Tuple of enhanced (r, g, b) values
        """
        # Store the original color for reference
        original_r, original_g, original_b = r, g, b

        # Force a minimum brightness to ensure visibility
        # But keep the relative proportions between channels to preserve the color
        min_brightness = 80
        min_channel = min(r, g, b)
        if min_channel < min_brightness and max(r, g, b) > 0:
            # Calculate how much we need to boost to reach minimum brightness
            boost_factor = min_brightness / max(1, min_channel)
            # Apply the boost while preserving color relationships
            r = min(255, int(r * boost_factor))
            g = min(255, int(g * boost_factor))
            b = min(255, int(b * boost_factor))

        # Preserve the color's character but make it more vibrant
        # Find the minimum channel value to determine color saturation
        min_channel = min(r, g, b)

        # Use a simpler approach to preserve the original color while making it more vibrant
        # This ensures we don't lose the color character

        # First, determine which channel is dominant to understand the color character
        is_red_dominant = r >= g and r >= b
        is_green_dominant = g >= r and g >= b
        is_blue_dominant = b >= r and b >= g

        # Use the original color directly, just boost its intensity
        # This preserves the exact hue of the original atmosphere color
        intensity_boost = 1.8  # More moderate boost to preserve color

        # Apply different boosts based on the color character
        if is_red_dominant:
            # For reddish atmospheres (desert planets)
            r = min(255, int(r * intensity_boost * 1.2))  # Boost red more
            g = min(255, int(g * intensity_boost * 0.9))  # Reduce green slightly
            b = min(255, int(b * intensity_boost * 0.9))  # Reduce blue slightly
        elif is_blue_dominant:
            # For bluish atmospheres (ocean planets)
            r = min(255, int(r * intensity_boost * 0.9))  # Reduce red slightly
            g = min(255, int(g * intensity_boost * 0.9))  # Reduce green slightly
            b = min(255, int(b * intensity_boost * 1.2))  # Boost blue more
        elif is_green_dominant:
            # For greenish atmospheres
            r = min(255, int(r * intensity_boost * 0.9))  # Reduce red slightly
            g = min(255, int(g * intensity_boost * 1.2))  # Boost green more
            b = min(255, int(b * intensity_boost * 0.9))  # Reduce blue slightly
        else:
            # For balanced colors, boost all equally
            r = min(255, int(r * intensity_boost))
            g = min(255, int(g * intensity_boost))
            b = min(255, int(b * intensity_boost))

        # Log the enhanced color for debugging
        logger.debug(f"Enhanced halo color: R:{r}, G:{g}, B:{b}", "atmosphere")

        # IMPORTANT: If all color channels are equal (gray), restore the original color
        # This fixes the issue where the halo appears gray instead of colored
        if r == g == b and r > 0:
            # Calculate the average intensity
            avg_intensity = r

            # Restore the original color proportions but keep the enhanced intensity
            if max(original_r, original_g, original_b) > 0:
                # Calculate the original color ratios
                orig_max = max(original_r, original_g, original_b)
                r_ratio = original_r / orig_max
                g_ratio = original_g / orig_max
                b_ratio = original_b / orig_max

                # Apply the original ratios to the enhanced intensity
                r = min(255, int(avg_intensity * r_ratio * 1.2))
                g = min(255, int(avg_intensity * g_ratio * 1.2))
                b = min(255, int(avg_intensity * b_ratio * 1.2))

                logger.debug(f"Restored halo color: R:{r}, G:{g}, B:{b}", "atmosphere")

        return (r, g, b)

    # No legacy methods - we only use the main apply_to_planet method