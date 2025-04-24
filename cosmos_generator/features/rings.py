"""
Planetary ring systems with proper perspective.
"""
from typing import Tuple, Optional, List
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.core.color_palette import ColorPalette, RGBA
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.utils import image_utils, math_utils
from cosmos_generator.core.interfaces import RingsInterface, NoiseGeneratorInterface, ColorPaletteInterface


class Rings(RingsInterface):
    """
    Generates realistic planetary ring systems.
    """

    def __init__(self, seed: Optional[int] = None,
                 noise_gen: Optional[NoiseGeneratorInterface] = None,
                 color_palette: Optional[ColorPaletteInterface] = None,
                 enabled: bool = True):
        """
        Initialize a ring generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
            enabled: Whether rings are enabled
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

        # Use provided instances or create new ones
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=self.seed)
        self.noise_gen = noise_gen if noise_gen is not None else FastNoiseGenerator(seed=self.seed)

        # Feature flag
        self._enabled = enabled

        # Store the last ring definitions for reference
        self.last_ring_definitions = []

    @property
    def enabled(self) -> bool:
        """Whether rings are enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether rings are enabled."""
        self._enabled = value

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
                   color: Optional[RGBA] = None, detail: float = 1.0,
                   original_planet_size: Optional[int] = None,
                   ring_complexity: Optional[int] = None) -> Image.Image:
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
        # If rings are disabled, return the original image
        if not self.enabled:
            return planet_image
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Get base ring color
        if color is None:
            base_ring_color = self.color_palette.get_ring_color(planet_type)
        else:
            base_ring_color = color

        # Get the size of the planet image (may include atmosphere)
        planet_image_size = planet_image.width

        # Use the original planet size if provided, otherwise use the image size
        # This is important for planets with atmosphere, where the image is larger than the actual planet
        actual_planet_size = original_planet_size if original_planet_size is not None else planet_image_size

        # Create a larger image to accommodate the rings
        ring_width_factor = 3.0  # Rings extend this much beyond planet radius (same as in AbstractPlanet)
        canvas_size = int(planet_image_size * ring_width_factor)  # Use image size for canvas
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate planet position and dimensions
        center_x, center_y = canvas_size // 2, canvas_size // 2

        # Detect if the planet image already has padding (e.g., from atmosphere)
        # We need to find the actual planet radius within the image
        # First, check if the image has an alpha channel and find the non-transparent area
        if planet_image.mode == "RGBA":
            # Get the alpha channel
            alpha = planet_image.split()[3]
            # Find the bounding box of the non-transparent area
            bbox = alpha.getbbox()
            if bbox:
                # Calculate the actual planet radius from the bounding box
                actual_width = bbox[2] - bbox[0]
                actual_height = bbox[3] - bbox[1]
                # Use the smaller dimension to ensure we're inside the planet
                actual_size = min(actual_width, actual_height)
                planet_radius = actual_size // 2
            else:
                # Fallback if no non-transparent area is found
                planet_radius = actual_planet_size // 2
        else:
            # If no alpha channel, use the image size
            planet_radius = actual_planet_size // 2

        planet_offset = (canvas_size - planet_image_size) // 2

        # Calculate vertical compression factor based on tilt
        # Convert tilt from degrees to a vertical compression factor
        # tilt of 0 degrees = vertical_factor of 0.0 (rings seen edge-on)
        # tilt of 90 degrees = vertical_factor of 1.0 (rings seen face-on)
        # Default tilt is 20 degrees if not specified
        tilt = 20.0 if tilt is None else max(0.0, min(90.0, tilt))
        vertical_factor = math.sin(math.radians(tilt))

        # Ensure a minimum vertical factor to avoid completely flat rings
        vertical_factor = max(0.05, vertical_factor)

        # Create the planet layer (for masking)
        # We need to create a mask that matches the actual planet, not including atmosphere
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)

        # Draw the planet as a circle with the calculated radius
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
             center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Create a mask for the front half (only the bottom half of the image)
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Generate a variable number of rings with varying properties
        # We'll use the seed to determine the number and properties of rings
        rng = self.rng  # Use the existing random generator initialized with the seed

        # Determine the ring system complexity (1-3)
        # 1: Minimal rings (few bands)
        # 2: Medium complexity (moderate number of bands)
        # 3: Full Saturn-like complexity (many bands)
        # Use the provided complexity if available, otherwise use random
        ring_complexity = ring_complexity if ring_complexity is not None else rng.randint(1, 3)

        # Base ring definitions for Saturn-like appearance with maximum opacity
        # We'll select from these based on the complexity level
        # Format: (inner_radius_factor, outer_radius_factor, opacity, brightness, is_solid)
        all_possible_rings = [
            # (inner_radius_factor, outer_radius_factor, opacity, brightness, is_solid)
            # D Ring (innermost, thin and faint)
            (1.20, 1.23, 0.9, 0.7, False),
            # C Ring (darker, brownish)
            (1.24, 1.35, 0.98, 0.75, False),
            # B Ring Inner (bright and dense)
            (1.36, 1.45, 1.0, 0.95, True),  # Solid ring
            # B Ring Middle (brightest section)
            (1.46, 1.55, 1.0, 1.0, True),   # Solid ring
            # B Ring Outer (bright with some structure)
            (1.56, 1.65, 1.0, 0.9, False),
            # Cassini Division (prominent gap)
            (1.66, 1.70, 0.8, 0.6, False),
            # A Ring Inner (bright)
            (1.71, 1.85, 0.98, 0.9, True),  # Solid ring
            # Encke Gap (thin dark gap)
            (1.86, 1.87, 0.7, 0.5, False),
            # A Ring Middle
            (1.88, 1.95, 0.98, 0.85, False),
            # Keeler Gap (very thin)
            (1.96, 1.965, 0.7, 0.4, False),
            # A Ring Outer (slightly fainter)
            (1.97, 2.05, 0.95, 0.8, False),
            # F Ring (thin, isolated outer ring)
            (2.10, 2.12, 0.9, 0.7, True),   # Solid ring
            # G Ring (very faint, wide)
            (2.15, 2.20, 0.85, 0.5, False)
        ]

        # Select rings based on complexity level
        base_ring_definitions = []

        if ring_complexity == 1:  # Minimal rings
            # Select only 3-4 main rings
            main_rings = [
                all_possible_rings[1],  # C Ring
                all_possible_rings[3],  # B Ring Middle
                all_possible_rings[6],  # A Ring Inner
            ]
            # Maybe add one more
            if rng.random() > 0.5:
                main_rings.append(all_possible_rings[10])  # A Ring Outer

            base_ring_definitions = main_rings

        elif ring_complexity == 2:  # Medium complexity
            # Select 6-8 rings
            main_rings = [
                all_possible_rings[1],  # C Ring
                all_possible_rings[2],  # B Ring Inner
                all_possible_rings[3],  # B Ring Middle
                all_possible_rings[4],  # B Ring Outer
                all_possible_rings[6],  # A Ring Inner
                all_possible_rings[8],  # A Ring Middle
            ]
            # Maybe add 1-2 more
            if rng.random() > 0.3:
                main_rings.append(all_possible_rings[10])  # A Ring Outer
            if rng.random() > 0.5:
                main_rings.append(all_possible_rings[12])  # F Ring

            base_ring_definitions = main_rings

        else:  # Full complexity (all rings)
            base_ring_definitions = all_possible_rings

        # Add some random variation to the rings
        ring_definitions = []

        # Determine how many additional thin rings to add based on complexity
        if ring_complexity == 1:
            num_additional_rings = rng.randint(0, 2)  # Few or no additional rings
        elif ring_complexity == 2:
            num_additional_rings = rng.randint(1, 3)  # Some additional rings
        else:
            num_additional_rings = rng.randint(2, 5)  # Many additional rings

        # Add the base rings with some variation
        for inner, outer, opacity, brightness, is_solid in base_ring_definitions:
            # Vary the opacity and brightness for more realistic appearance
            # Use minimal variation for opacity to keep rings very solid
            varied_opacity = min(1.0, max(0.7, opacity * (0.9 + 0.15 * rng.random())))
            varied_brightness = min(1.0, max(0.7, brightness * (0.95 + 0.1 * rng.random())))

            # For solid rings, set opacity to 1.0
            if is_solid:
                varied_opacity = 1.0

            # Add to the ring definitions
            ring_definitions.append((inner, outer, varied_opacity, varied_brightness, is_solid))

        # Add some additional thin rings at random positions
        for _ in range(num_additional_rings):
            # Random position between 1.25 and 2.1 times planet radius
            position = 1.25 + 0.85 * rng.random()
            # Very thin ring
            thickness = 0.005 + 0.01 * rng.random()
            # Random opacity and brightness
            # Use very high opacity values for solid look
            opacity = 0.8 + 0.2 * rng.random()
            brightness = 0.8 + 0.2 * rng.random()
            # Randomly decide if this ring is solid (25% chance)
            is_solid = rng.random() < 0.25

            # If solid, set opacity to 1.0
            if is_solid:
                opacity = 1.0

            # Add to the ring definitions
            ring_definitions.append((position, position + thickness, opacity, brightness, is_solid))

        # Sort the rings by inner radius
        ring_definitions.sort(key=lambda x: x[0])

        # Store the ring definitions for later reference
        self.last_ring_definitions = ring_definitions

        # Process each ring
        for i, (inner_factor, outer_factor, opacity, brightness, is_solid) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color for each ring
            r, g, b, a = base_ring_color

            # For solid rings, ensure full opacity
            if is_solid:
                opacity = 1.0

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
        for i, (inner_factor, outer_factor, opacity, brightness, is_solid) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color for each ring
            r, g, b, a = base_ring_color

            # For solid rings, ensure full opacity
            if is_solid:
                opacity = 1.0

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
