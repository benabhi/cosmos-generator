"""
Cloud generation for celestial bodies.
"""
from typing import Tuple, Optional, Dict, Any
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.core.noise_generator import NoiseGenerator
from cosmos_generator.utils import image_utils, lighting_utils


class Clouds:
    """
    Generates cloud layers with varying patterns and opacity.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a cloud generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
        """
        self.noise_gen = NoiseGenerator(seed=seed)
    
    def generate_cloud_layer(self, size: int, coverage: float = 0.5, 
                            density: float = 0.7, detail: float = 1.0,
                            light_angle: float = 45.0) -> Image.Image:
        """
        Generate a cloud layer for a planet.

        Args:
            size: Size of the cloud layer in pixels
            coverage: Cloud coverage (0.0 to 1.0)
            density: Cloud density/opacity (0.0 to 1.0)
            detail: Level of detail in cloud patterns (0.0 to 2.0)
            light_angle: Angle of the light source in degrees

        Returns:
            Cloud layer as PIL Image
        """
        # Generate cloud noise
        cloud_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3 * detail, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.5, 2.0, 3.0 * detail)
            )
        )
        
        # Threshold the noise to create cloud patterns
        cloud_threshold = 1.0 - coverage
        cloud_mask = Image.new("L", (size, size), 0)
        cloud_data = cloud_mask.load()
        
        for y in range(size):
            for x in range(size):
                if cloud_noise[y, x] > cloud_threshold:
                    # Scale alpha based on how far above threshold
                    alpha = int(255 * density * (cloud_noise[y, x] - cloud_threshold) / (1.0 - cloud_threshold))
                    cloud_data[x, y] = alpha
        
        # Apply circular mask to the clouds
        circle_mask = image_utils.create_circle_mask(size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)
        
        # Create cloud layer
        cloud_color = (255, 255, 255, 180)  # Semi-transparent white
        clouds = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, size-1, size-1), fill=cloud_color)
        
        # Apply the cloud mask
        clouds.putalpha(cloud_mask)
        
        # Apply lighting to clouds
        lit_clouds = lighting_utils.apply_directional_light(
            clouds,
            lighting_utils.calculate_normal_map(cloud_noise, 2.0),
            light_direction=(
                -math.cos(math.radians(light_angle)),
                -math.sin(math.radians(light_angle)),
                1.0
            ),
            ambient=0.3,
            diffuse=0.7,
            specular=0.0
        )
        
        return lit_clouds
    
    def apply_clouds(self, planet_image: Image.Image, coverage: float = 0.5, 
                    density: float = 0.7, detail: float = 1.0,
                    light_angle: float = 45.0) -> Image.Image:
        """
        Apply clouds to a planet image.

        Args:
            planet_image: Base planet image
            coverage: Cloud coverage (0.0 to 1.0)
            density: Cloud density/opacity (0.0 to 1.0)
            detail: Level of detail in cloud patterns (0.0 to 2.0)
            light_angle: Angle of the light source in degrees

        Returns:
            Planet image with clouds
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")
            
        # Generate cloud layer
        size = planet_image.width
        clouds = self.generate_cloud_layer(size, coverage, density, detail, light_angle)
        
        # Composite clouds over the planet
        result = Image.alpha_composite(planet_image, clouds)
        
        return result
    
    def generate_banded_clouds(self, size: int, band_count: int = 5, 
                              turbulence: float = 0.3, light_angle: float = 45.0) -> Image.Image:
        """
        Generate banded cloud patterns for gas giants.

        Args:
            size: Size of the cloud layer in pixels
            band_count: Number of cloud bands
            turbulence: Amount of turbulence in the bands (0.0 to 1.0)
            light_angle: Angle of the light source in degrees

        Returns:
            Banded cloud layer as PIL Image
        """
        # Generate base noise
        base_noise = self.noise_gen.generate_noise_map(
            size, size,
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 4, 0.5, 2.0, 2.0)
        )
        
        # Generate band noise
        band_noise = np.zeros((size, size), dtype=np.float32)
        for y in range(size):
            # Calculate normalized y position
            ny = y / size
            
            # Calculate band value
            band_value = math.sin(ny * math.pi * band_count) * 0.5 + 0.5
            
            for x in range(size):
                # Add turbulence
                turbulence_value = base_noise[y, x] * turbulence
                band_noise[y, x] = max(0.0, min(1.0, band_value + turbulence_value))
        
        # Create cloud mask
        cloud_mask = Image.new("L", (size, size), 0)
        cloud_data = cloud_mask.load()
        
        for y in range(size):
            for x in range(size):
                cloud_data[x, y] = int(band_noise[y, x] * 255)
        
        # Apply circular mask
        circle_mask = image_utils.create_circle_mask(size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)
        
        # Create cloud layer
        cloud_color = (255, 255, 255, 180)  # Semi-transparent white
        clouds = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, size-1, size-1), fill=cloud_color)
        
        # Apply the cloud mask
        clouds.putalpha(cloud_mask)
        
        # Apply lighting to clouds
        lit_clouds = lighting_utils.apply_directional_light(
            clouds,
            lighting_utils.calculate_normal_map(band_noise, 1.5),
            light_direction=(
                -math.cos(math.radians(light_angle)),
                -math.sin(math.radians(light_angle)),
                1.0
            ),
            ambient=0.3,
            diffuse=0.7,
            specular=0.0
        )
        
        return lit_clouds
