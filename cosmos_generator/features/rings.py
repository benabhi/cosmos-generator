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
        Apply a ring system to a planet image.

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
        ring_width_factor = 2.0  # Rings extend this much beyond planet radius
        ring_size = int(planet_size * ring_width_factor)
        result = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        
        # Calculate planet position in the larger image
        planet_offset = (ring_size - planet_size) // 2
        
        # Create ring template
        ring_inner_radius = 0.55  # Just outside the planet
        ring_outer_radius = ring_width_factor * 0.5  # Extend to edge
        
        # Generate ring texture
        ring_height = int(ring_size * (0.5 - 0.25 * abs(math.sin(math.radians(tilt)))))
        ring_template = self.generate_ring_texture(
            ring_size, ring_height,
            ring_inner_radius, ring_outer_radius,
            ring_color, detail
        )
        
        # Position the ring template
        ring_y_offset = (ring_size - ring_height) // 2
        
        # Create a mask for the part of the rings that should be behind the planet
        behind_mask = Image.new("L", (ring_size, ring_size), 0)
        draw = ImageDraw.Draw(behind_mask)
        draw.rectangle((0, ring_y_offset, ring_size-1, ring_y_offset+ring_height-1), fill=255)
        
        # Create a mask for the planet
        planet_mask = Image.new("L", (ring_size, ring_size), 0)
        draw = ImageDraw.Draw(planet_mask)
        draw.ellipse((planet_offset, planet_offset, planet_offset+planet_size-1, planet_offset+planet_size-1), fill=255)
        
        # Subtract planet mask from behind mask to get only the parts of rings behind the planet
        behind_mask = ImageChops.subtract(behind_mask, planet_mask)
        
        # Create a mask for the parts of rings in front of the planet
        front_mask = ImageChops.subtract(ImageChops.invert(behind_mask), planet_mask)
        
        # Apply lighting to rings
        # Simplistic lighting: just darken the rings based on light angle
        darkened_rings = image_utils.adjust_brightness(ring_template, 0.7)
        
        # Composite the images in the correct order:
        # 1. Rings behind planet
        result.paste(darkened_rings, (0, ring_y_offset), behind_mask)
        
        # 2. Planet
        result.paste(planet_image, (planet_offset, planet_offset), planet_image)
        
        # 3. Rings in front of planet
        result.paste(ring_template, (0, ring_y_offset), front_mask)
        
        return result
