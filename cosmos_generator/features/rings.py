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
        Apply a ring system to a planet image using the minimal ring implementation algorithm.

        Args:
            planet_image: Base planet image
            planet_type: Type of planet
            tilt: Tilt angle of the rings in degrees
            light_angle: Angle of the light source in degrees
            color: Optional custom color for the rings
            detail: Level of detail in ring patterns

        Returns:
            Planet image with rings
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Get ring color
        if color is None:
            ring_color = self.color_palette.get_ring_color(planet_type)
        else:
            ring_color = color

        # Create a larger image to accommodate the rings
        planet_size = planet_image.width
        ring_width_factor = 2.5  # Rings extend this much beyond planet radius
        canvas_size = int(planet_size * ring_width_factor)
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate planet position and dimensions
        center_x, center_y = canvas_size // 2, canvas_size // 2
        planet_radius = planet_size // 2
        planet_offset = (canvas_size - planet_size) // 2

        # Calculate ring dimensions (ellipse)
        # The outer radius should be significantly larger than the planet
        outer_rx = int(planet_radius * 2.0)  # Horizontal radius (2x planet radius)

        # The vertical radius should be smaller to create the elliptical appearance
        # Adjust based on tilt angle if provided
        tilt_factor = abs(math.sin(math.radians(tilt)))
        outer_ry = int(planet_radius * (0.3 + 0.2 * (1 - tilt_factor)))  # Vertical radius (30-50% of planet radius)

        # Inner radius should be just outside the planet
        inner_rx = int(planet_radius * 1.2)  # 20% larger than planet radius
        inner_ry = int(outer_ry * (inner_rx / outer_rx))  # Maintain aspect ratio

        # Step 1: Create the ring layer (ellipse with hole)
        # ------------------------------------------------
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

        # Step 2: Create the planet layer
        # ------------------------------
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
             center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Step 3: Create the masks for different parts of the rings
        # -------------------------------------------------------

        # External arcs: difference between the ring and the planet
        ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

        # Create a mask for the front half (only the bottom half of the image)
        # This assumes the light is coming from above
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Intersection between the ring and the planet
        ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

        # The front band is only the front half of the intersection
        ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

        # Step 4: Apply colors and lighting
        # -------------------------------

        # Apply lighting to the ring color based on light angle
        shadow_factor = 0.7  # Darkness of the shadow
        r, g, b, a = ring_color

        # Slightly darker color for the arcs (parts behind the planet)
        arcs_color = (int(r * shadow_factor), int(g * shadow_factor), int(b * shadow_factor), a)

        # Create the colored ring arcs
        ring_arcs_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        ring_arcs_colored.paste(arcs_color, mask=ring_arcs)

        # Create the colored front band
        ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        ring_front_colored.paste(ring_color, mask=ring_front)

        # Step 5: Composite the final image
        # -------------------------------

        # Composite in the correct Z-buffer order:
        # 1. Ring arcs (behind the planet)
        result.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)

        # 2. Planet
        result.paste(planet_image, (planet_offset, planet_offset), planet_image)

        # 3. Front band (in front of the planet)
        result.paste(ring_front_colored, (0, 0), ring_front_colored)

        return result
