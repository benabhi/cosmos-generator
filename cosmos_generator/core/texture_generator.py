"""
Texture generation utilities for celestial bodies.
"""
from typing import Dict, Optional
import math
import random
import numpy as np
from PIL import Image, ImageDraw

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette, Color
from cosmos_generator.core.interfaces import TextureGeneratorInterface, NoiseGeneratorInterface, ColorPaletteInterface


class TextureGenerator(TextureGeneratorInterface):
    """
    Creates base textures for different planet types using noise algorithms.
    """

    def __init__(self, seed: Optional[int] = None, noise_gen: Optional[NoiseGeneratorInterface] = None, color_palette: Optional[ColorPaletteInterface] = None):
        """
        Initialize a texture generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible texture generation
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)

        # Use provided instances or create new ones
        self.noise_gen = noise_gen if noise_gen is not None else FastNoiseGenerator(seed=self.seed)
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=self.seed)

    def create_base_sphere(self, size: int, color: Color = (255, 255, 255)) -> Image.Image:
        """
        Create a base sphere image with the specified size and color.

        Args:
            size: Size of the image (width and height)
            color: Base color of the sphere

        Returns:
            PIL Image of a sphere

        Raises:
            ValueError: If size is not positive
            TypeError: If color is not a valid RGB or RGBA tuple
        """
        # Validate parameters
        if not isinstance(size, int):
            raise TypeError(f"size must be an integer, got {type(size).__name__}")

        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        if not isinstance(color, tuple):
            raise TypeError(f"color must be a tuple, got {type(color).__name__}")

        if len(color) not in (3, 4):
            raise ValueError(f"color must be an RGB or RGBA tuple, got {color}")

        try:
            # Create a transparent image
            image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Draw a filled circle
            radius = size // 2
            center = radius
            draw.ellipse((0, 0, size-1, size-1), fill=color)

            return image
        except Exception as e:
            # Handle specific PIL exceptions
            if "invalid color specifier" in str(e).lower():
                raise ValueError(f"Invalid color format: {color}. Must be RGB or RGBA tuple with values 0-255.") from e
            else:
                # Re-raise the original exception with more context
                raise RuntimeError(f"Error creating base sphere: {e}") from e

    def apply_spherical_mask(self, image: Image.Image) -> Image.Image:
        """
        Apply a spherical mask to an image to make it round.

        Args:
            image: Input image

        Returns:
            Masked spherical image
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        size = image.width
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)

        # Draw a filled circle
        draw.ellipse((0, 0, size-1, size-1), fill=255)

        # Apply the mask
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(image, (0, 0), mask)

        return result

    def apply_noise_to_sphere(self, base_image: Image.Image,
                              noise_map: np.ndarray,
                              color_map: Dict[str, Color],
                              threshold_map: Optional[Dict[float, str]] = None) -> Image.Image:
        """
        Apply a noise map to a base sphere image using a color map.

        Args:
            base_image: Base sphere image
            noise_map: 2D numpy array of noise values in range [0, 1]
            color_map: Dictionary mapping categories to colors
            threshold_map: Optional dictionary mapping noise thresholds to color categories

        Returns:
            Textured sphere image
        """
        if base_image.mode != "RGBA":
            base_image = base_image.convert("RGBA")

        # Create a new image with the same size
        result = Image.new("RGBA", base_image.size, (0, 0, 0, 0))

        # Get pixel data
        base_pixels = np.array(base_image)
        result_pixels = np.array(result)

        # Resize noise map if needed
        if noise_map.shape != (base_image.height, base_image.width):
            from PIL import Image as PILImage
            noise_image = PILImage.fromarray((noise_map * 255).astype(np.uint8), mode="L")
            noise_image = noise_image.resize((base_image.width, base_image.height), PILImage.LANCZOS)
            noise_map = np.array(noise_image) / 255.0

        # Apply noise to the image
        height, width = noise_map.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)

        for y in range(height):
            for x in range(width):
                # Skip if the base pixel is transparent
                if base_pixels[y, x, 3] == 0:
                    continue

                # Calculate distance from center for spherical mapping
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)

                # Skip if outside the sphere
                if distance > radius:
                    continue

                # Get noise value
                noise_value = noise_map[y, x]

                # Determine color based on noise value and threshold map
                color_key = "base"
                if threshold_map:
                    for threshold, key in sorted(threshold_map.items()):
                        if noise_value <= threshold:
                            color_key = key
                            break

                # Get color from color map
                color = color_map.get(color_key, color_map.get("base", (255, 255, 255)))

                # Apply color to result
                if len(color) == 3:
                    result_pixels[y, x] = [color[0], color[1], color[2], 255]
                else:
                    result_pixels[y, x] = color

        # Create new image from the modified pixel data
        return Image.fromarray(result_pixels)

    def apply_lighting(self, image: Image.Image, light_angle: float = 45.0,
                       light_intensity: float = 1.0, falloff: float = 0.6) -> Image.Image:
        """
        Apply directional lighting to a spherical image.

        Args:
            image: Input spherical image
            light_angle: Angle of the light source in degrees (0 = right, 90 = top)
            light_intensity: Intensity of the light (0.0-2.0)
            falloff: Light falloff factor (higher values create sharper shadows) (0.0-1.0)

        Returns:
            Image with lighting applied

        Raises:
            TypeError: If image is not a PIL Image
            ValueError: If light_intensity or falloff are outside their valid ranges
        """
        # Validate parameters
        if not isinstance(image, Image.Image):
            raise TypeError("image must be a PIL Image")

        if not 0 <= light_intensity <= 2.0:
            raise ValueError(f"light_intensity must be between 0.0 and 2.0, got {light_intensity}")

        if not 0 <= falloff <= 1.0:
            raise ValueError(f"falloff must be between 0.0 and 1.0, got {falloff}")

        # Ensure image is in RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Create a new image with the same size
        result = Image.new("RGBA", image.size, (0, 0, 0, 0))

        # Get pixel data
        pixels = np.array(image)
        result_pixels = np.array(result)

        # Calculate light direction
        light_rad = math.radians(light_angle)
        light_x = math.cos(light_rad)
        light_y = -math.sin(light_rad)  # Negative because y increases downward in images

        # Apply lighting to the image
        height, width = pixels.shape[:2]
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)

        for y in range(height):
            for x in range(width):
                # Skip if the pixel is transparent
                if pixels[y, x, 3] == 0:
                    continue

                # Calculate position relative to center
                dx = (x - center_x) / radius
                dy = (y - center_y) / radius
                distance = math.sqrt(dx*dx + dy*dy)

                # Skip if outside the sphere
                if distance > 1.0:
                    continue

                # Calculate surface normal at this point
                # For a sphere, the normal is just the normalized vector from center to point
                z = math.sqrt(1.0 - distance*distance)
                nx, ny, nz = dx, dy, z

                # Calculate dot product with light direction
                dot = nx * light_x + ny * light_y + nz * 1.0

                # Apply lighting factor
                if dot < 0:
                    # Point is facing away from light
                    factor = 0.1  # Ambient light
                else:
                    # Apply light intensity and falloff
                    factor = 0.1 + 0.9 * light_intensity * (dot ** falloff)

                # Apply lighting to color
                r = min(255, int(pixels[y, x, 0] * factor))
                g = min(255, int(pixels[y, x, 1] * factor))
                b = min(255, int(pixels[y, x, 2] * factor))

                # Set result pixel
                result_pixels[y, x] = [r, g, b, pixels[y, x, 3]]

        # Create new image from the modified pixel data
        return Image.fromarray(result_pixels)

    # Removed unused texture generation methods
    # These methods are now implemented in the specific planet classes
    # and are no longer needed in the TextureGenerator class
