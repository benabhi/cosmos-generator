"""
Planetary ring systems with proper perspective.
"""
from typing import Tuple, Optional, List
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.core.color_palette import ColorPalette, RGBA
from cosmos_generator.core.noise_generator import NoiseGenerator
from cosmos_generator.utils import image_utils, math_utils


class Rings:
    """
    Generates realistic planetary ring systems.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a ring generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)
        self.color_palette = ColorPalette(seed=self.seed)
        self.noise_gen = NoiseGenerator(seed=self.seed)

    def generate_ring_texture(self, width: int, height: int,
                             inner_radius: float, outer_radius: float,
                             color: RGBA, detail: float = 1.0) -> Image.Image:
        """
        Generate a texture for planetary rings.

        Args:
            width: Width of the texture
            height: Height of the texture
            inner_radius: Inner radius of the rings as a fraction of width/2
            outer_radius: Outer radius of the rings as a fraction of width/2
            color: Base color of the rings
            detail: Level of detail in ring patterns

        Returns:
            Ring texture as PIL Image
        """
        # Create a transparent image
        texture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(texture)

        # Calculate pixel radii
        center_x = width // 2
        center_y = height // 2
        inner_pixel_radius = int(inner_radius * center_x)
        outer_pixel_radius = int(outer_radius * center_x)

        # Draw the outer ellipse (full ring)
        draw.ellipse((0, 0, width-1, height-1), fill=color)

        # Draw the inner ellipse (hole) with transparent color
        inner_left = center_x - inner_pixel_radius
        inner_top = center_y - inner_pixel_radius
        inner_right = center_x + inner_pixel_radius
        inner_bottom = center_y + inner_pixel_radius
        draw.ellipse((inner_left, inner_top, inner_right, inner_bottom), fill=(0, 0, 0, 0))

        # Generate noise for ring details
        if detail > 0:
            ring_noise = self.noise_gen.generate_noise_map(
                width, height,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 4, 0.5, 2.0, 5.0 * detail)
            )

            # Apply noise to the texture
            texture_array = np.array(texture)
            for y in range(height):
                for x in range(width):
                    # Skip transparent pixels
                    if texture_array[y, x, 3] == 0:
                        continue

                    # Calculate distance from center
                    dx = x - center_x
                    dy = y - center_y
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Skip pixels outside the ring
                    if distance < inner_pixel_radius or distance > outer_pixel_radius:
                        continue

                    # Apply noise to alpha channel
                    noise_value = ring_noise[y, x]
                    # More noise near edges
                    edge_factor = min(
                        (distance - inner_pixel_radius) / (inner_pixel_radius * 0.2),
                        (outer_pixel_radius - distance) / (outer_pixel_radius * 0.2)
                    )
                    edge_factor = max(0.0, min(1.0, edge_factor))

                    # Apply noise and edge factor to alpha
                    alpha = texture_array[y, x, 3]
                    alpha = int(alpha * (0.8 + 0.2 * noise_value) * edge_factor)
                    texture_array[y, x, 3] = alpha

            # Convert back to image
            texture = Image.fromarray(texture_array)

        return texture

    def apply_rings(self, planet_image: Image.Image, planet_type: str,
                   tilt: float = 0.0, light_angle: float = 45.0,
                   color: Optional[RGBA] = None, detail: float = 1.0) -> Image.Image:
        """
        Apply a Saturn-like ring system with multiple concentric rings of varying widths and opacities.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            tilt: Tilt angle of the rings in degrees
            light_angle: Angle of the light source in degrees
            color: Optional custom color for the rings
            detail: Level of detail in ring patterns

        Returns:
            Planet image with Saturn-like rings
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Get base ring color
        if color is None:
            base_ring_color = self.color_palette.get_ring_color(planet_type)
        else:
            base_ring_color = color

        # Create a larger image to accommodate the rings
        planet_size = planet_image.width
        ring_width_factor = 2.5  # Rings extend this much beyond planet radius
        canvas_size = int(planet_size * ring_width_factor)
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate planet position and dimensions
        center_x, center_y = canvas_size // 2, canvas_size // 2
        planet_radius = planet_size // 2
        planet_offset = (canvas_size - planet_size) // 2

        # Calculate vertical compression factor based on tilt
        tilt_factor = abs(math.sin(math.radians(tilt)))
        vertical_factor = 0.3 + 0.2 * (1 - tilt_factor)  # Between 30-50% based on tilt

        # Create the planet layer (for masking)
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
             center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Create a mask for the front half (only the bottom half of the image)
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Define the Saturn-like ring system with multiple rings and varying widths/opacities
        ring_definitions = [
            # (inner_radius_factor, outer_radius_factor, opacity, brightness)
            # D Ring (innermost, thin and faint)
            (1.20, 1.23, 0.7, 0.7),
            # C Ring (darker, brownish)
            (1.24, 1.35, 0.85, 0.75),
            # B Ring Inner (bright and dense)
            (1.36, 1.45, 0.95, 0.95),
            # B Ring Middle (brightest section)
            (1.46, 1.55, 1.0, 1.0),
            # B Ring Outer (bright with some structure)
            (1.56, 1.65, 0.95, 0.9),
            # Cassini Division (prominent gap)
            (1.66, 1.70, 0.5, 0.6),
            # A Ring Inner (bright)
            (1.71, 1.85, 0.9, 0.9),
            # Encke Gap (thin dark gap)
            (1.86, 1.87, 0.4, 0.5),
            # A Ring Middle
            (1.88, 1.95, 0.9, 0.85),
            # Keeler Gap (very thin)
            (1.96, 1.965, 0.3, 0.4),
            # A Ring Outer (slightly fainter)
            (1.97, 2.05, 0.85, 0.8),
            # F Ring (thin, isolated outer ring)
            (2.10, 2.12, 0.7, 0.7),
            # G Ring (very faint, wide)
            (2.15, 2.20, 0.6, 0.5)
        ]

        # Process each ring
        for i, (inner_factor, outer_factor, opacity, brightness) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color for each ring
            r, g, b, a = base_ring_color

            # Apply brightness and opacity adjustments
            ring_color = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
                int(a * opacity)
            )

            # Create the ring layer (ellipse with hole)
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Draw outer ellipse
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry, center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Draw inner ellipse (hole)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry, center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # External arcs: difference between the ring and the planet
            ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

            # Intersection between the ring and the planet
            ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

            # The front band is only the front half of the intersection
            ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

            # Apply lighting to the ring color based on light angle
            shadow_factor = 0.6  # Darkness of the shadow

            # Slightly darker color for the arcs (parts behind the planet)
            arcs_color = (
                int(ring_color[0] * shadow_factor),
                int(ring_color[1] * shadow_factor),
                int(ring_color[2] * shadow_factor),
                ring_color[3]
            )

            # Create the colored ring arcs
            ring_arcs_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_arcs_colored.paste(arcs_color, mask=ring_arcs)

            # Create the colored front band
            ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_front_colored.paste(ring_color, mask=ring_front)

            # Composite the rings in the correct Z-buffer order:
            # 1. Ring arcs (behind the planet)
            result.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)

            # Note: We'll add the front bands after the planet is added

        # Add the planet on top of the rings that are behind it
        result.paste(planet_image, (planet_offset, planet_offset), planet_image)

        # Now add the front bands (parts of rings that pass in front of the planet)
        for i, (inner_factor, outer_factor, opacity, brightness) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color for each ring
            r, g, b, a = base_ring_color

            # Apply brightness and opacity adjustments
            ring_color = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
                int(a * opacity)
            )

            # Create the ring layer (ellipse with hole)
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Draw outer ellipse
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry, center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Draw inner ellipse (hole)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry, center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # Intersection between the ring and the planet
            ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

            # The front band is only the front half of the intersection
            ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

            # Create the colored front band
            ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_front_colored.paste(ring_color, mask=ring_front)

            # Add the front band on top of the planet
            result.paste(ring_front_colored, (0, 0), ring_front_colored)

        return result
