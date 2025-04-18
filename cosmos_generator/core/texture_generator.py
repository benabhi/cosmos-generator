"""
Texture generation utilities for celestial bodies.
"""
from typing import Dict, List, Tuple, Optional, Any, Callable
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette, Color, RGB, RGBA


class TextureGenerator:
    """
    Creates base textures for different planet types using noise algorithms.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a texture generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible texture generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.noise_gen = FastNoiseGenerator(seed=self.seed)
        self.color_palette = ColorPalette(seed=self.seed)

    def create_base_sphere(self, size: int, color: Color = (255, 255, 255)) -> Image.Image:
        """
        Create a base sphere image with the specified size and color.

        Args:
            size: Size of the image (width and height)
            color: Base color of the sphere

        Returns:
            PIL Image of a sphere
        """
        # Create a transparent image
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw a filled circle
        radius = size // 2
        center = radius
        draw.ellipse((0, 0, size-1, size-1), fill=color)

        return image

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
            light_intensity: Intensity of the light
            falloff: Light falloff factor (higher values create sharper shadows)

        Returns:
            Image with lighting applied
        """
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

    def generate_desert_texture(self, size: int) -> Image.Image:
        """
        Generate a texture for a desert planet.

        Args:
            size: Size of the texture

        Returns:
            Desert planet texture
        """
        # Create base sphere
        base_color = self.color_palette.get_random_color("Desert", "base")
        base_image = self.create_base_sphere(size, base_color)

        # Generate noise maps
        dunes_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.5, 2.0, 4.0)
            )
        )

        canyon_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: self.noise_gen.ridged_simplex(x, y, 4, 0.6, 2.5, 3.0)
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [dunes_noise, canyon_noise],
            [0.7, 0.3]
        )

        # Create color map
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Desert", "highlight"),
            "shadow": self.color_palette.get_random_color("Desert", "shadow"),
        }

        # Create threshold map
        threshold_map = {
            0.3: "shadow",
            0.7: "base",
            1.0: "highlight",
        }

        # Apply noise to sphere
        textured_image = self.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        # Apply lighting
        lit_image = self.apply_lighting(textured_image, 45.0, 1.0, 0.6)

        return lit_image

    def generate_furnace_texture(self, size: int) -> Image.Image:
        """
        Generate a texture for a furnace (volcanic) planet.

        Args:
            size: Size of the texture

        Returns:
            Furnace planet texture
        """
        # Create base sphere
        base_color = self.color_palette.get_random_color("Furnace", "base")
        base_image = self.create_base_sphere(size, base_color)

        # Generate noise maps
        lava_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.2, 3.0)
            )
        )

        volcano_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 8, "euclidean")
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [lava_noise, volcano_noise],
            [0.6, 0.4]
        )

        # Create color map
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Furnace", "highlight"),
            "shadow": self.color_palette.get_random_color("Furnace", "shadow"),
            "special": self.color_palette.get_random_color("Furnace", "special"),
        }

        # Create threshold map
        threshold_map = {
            0.2: "shadow",
            0.5: "base",
            0.8: "highlight",
            1.0: "special",
        }

        # Apply noise to sphere
        textured_image = self.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        # Apply lighting
        lit_image = self.apply_lighting(textured_image, 30.0, 1.2, 0.5)

        return lit_image

    # Additional planet texture generation methods would be implemented here
    # For brevity, I'm only including two examples

    def generate_texture(self, planet_type: str, size: int) -> Image.Image:
        """
        Generate a texture for the specified planet type.

        Args:
            planet_type: Type of planet
            size: Size of the texture

        Returns:
            Planet texture
        """
        # Map planet types to their respective texture generation methods
        texture_methods = {
            "Desert": self.generate_desert_texture,
            "Furnace": self.generate_furnace_texture,
            # Other planet types would be added here
        }

        if planet_type not in texture_methods:
            raise ValueError(f"Unknown planet type: {planet_type}")

        return texture_methods[planet_type](size)
