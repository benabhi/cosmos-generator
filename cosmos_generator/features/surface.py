"""
Surface details for celestial bodies.
"""
from typing import Tuple, Optional, List, Dict, Any
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.utils import image_utils, lighting_utils, math_utils


class Surface:
    """
    Adds terrain details like craters, mountains, etc.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a surface generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)
        self.noise_gen = FastNoiseGenerator(seed=self.seed)

    def generate_height_map(self, size: int, terrain_type: str,
                           roughness: float = 1.0) -> np.ndarray:
        """
        Generate a height map for a planet surface.

        Args:
            size: Size of the height map in pixels
            terrain_type: Type of terrain ("mountainous", "cratered", "smooth", etc.)
            roughness: Roughness of the terrain (0.0 to 2.0)

        Returns:
            2D numpy array of height values in range [0, 1]
        """
        if terrain_type == "mountainous":
            # Generate mountainous terrain with ridged noise
            height_map = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.ridged_simplex(x, y, 6, 0.5, 2.0, 4.0 * roughness)
            )
        elif terrain_type == "cratered":
            # Generate cratered terrain with worley noise
            base_noise = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 10, "euclidean")
            )

            # Add some simplex noise for variation
            simplex_noise = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 4, 0.5, 2.0, 3.0)
            )

            # Combine the noise maps
            height_map = self.noise_gen.combine_noise_maps(
                [base_noise, simplex_noise],
                [0.7, 0.3]
            )

            # Apply power function to create more distinct craters
            height_map = np.power(height_map, 2.0 * roughness)
        elif terrain_type == "smooth":
            # Generate smooth terrain with low-frequency simplex noise
            height_map = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 3, 0.4, 2.0, 2.0 * roughness)
            )
        elif terrain_type == "canyon":
            # Generate canyon terrain with domain-warped noise
            height_map = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.domain_warp(
                    x, y,
                    lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.4 * roughness),
                    lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.6, 2.2, 3.0)
                )
            )
        elif terrain_type == "volcanic":
            # Generate volcanic terrain with a mix of worley and simplex noise
            worley_noise = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 8, "euclidean")
            )

            simplex_noise = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 5, 0.5, 2.0, 3.0)
            )

            # Combine the noise maps
            height_map = self.noise_gen.combine_noise_maps(
                [worley_noise, simplex_noise],
                [0.6, 0.4]
            )

            # Apply power function to create more distinct volcanic features
            height_map = np.power(height_map, 1.5 * roughness)
        else:
            # Default to simplex noise
            height_map = self.noise_gen.generate_noise_map(
                size, size,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 6, 0.5, 2.0, 3.0 * roughness)
            )

        return height_map

    def add_craters(self, height_map: np.ndarray, count: int = 20,
                   min_size: float = 0.02, max_size: float = 0.1) -> np.ndarray:
        """
        Add craters to a height map.

        Args:
            height_map: Base height map
            count: Number of craters to add
            min_size: Minimum crater size as a fraction of the height map size
            max_size: Maximum crater size as a fraction of the height map size

        Returns:
            Height map with craters
        """
        size = height_map.shape[0]
        result = height_map.copy()

        for _ in range(count):
            # Random crater position
            x = self.rng.randint(0, size-1)
            y = self.rng.randint(0, size-1)

            # Random crater size
            crater_size = self.rng.uniform(min_size, max_size) * size
            crater_radius = int(crater_size / 2)

            # Random crater depth
            crater_depth = self.rng.uniform(0.2, 0.8)

            # Create crater
            for cy in range(max(0, y - crater_radius), min(size, y + crater_radius + 1)):
                for cx in range(max(0, x - crater_radius), min(size, x + crater_radius + 1)):
                    # Calculate distance from crater center
                    dx = cx - x
                    dy = cy - y
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Skip if outside crater
                    if distance > crater_radius:
                        continue

                    # Calculate crater profile
                    # 1.0 at the rim, -crater_depth at the center
                    if distance < crater_radius * 0.2:
                        # Crater floor
                        crater_value = -crater_depth
                    else:
                        # Crater wall
                        t = (distance - crater_radius * 0.2) / (crater_radius * 0.8)
                        crater_value = -crater_depth + (1.0 + crater_depth) * t

                        # Add rim
                        if t > 0.8:
                            rim_t = (t - 0.8) / 0.2
                            crater_value += 0.2 * math.sin(rim_t * math.pi)

                    # Apply crater to height map
                    result[cy, cx] += crater_value

        # Normalize the height map
        return self.noise_gen.normalize_noise_map(result)

    def add_mountains(self, height_map: np.ndarray, count: int = 10,
                     min_size: float = 0.05, max_size: float = 0.2) -> np.ndarray:
        """
        Add mountains to a height map.

        Args:
            height_map: Base height map
            count: Number of mountain ranges to add
            min_size: Minimum mountain size as a fraction of the height map size
            max_size: Maximum mountain size as a fraction of the height map size

        Returns:
            Height map with mountains
        """
        size = height_map.shape[0]
        result = height_map.copy()

        for _ in range(count):
            # Random mountain position
            x = self.rng.randint(0, size-1)
            y = self.rng.randint(0, size-1)

            # Random mountain size
            mountain_size = self.rng.uniform(min_size, max_size) * size
            mountain_radius = int(mountain_size / 2)

            # Random mountain height
            mountain_height = self.rng.uniform(0.3, 1.0)

            # Create mountain
            for cy in range(max(0, y - mountain_radius), min(size, y + mountain_radius + 1)):
                for cx in range(max(0, x - mountain_radius), min(size, x + mountain_radius + 1)):
                    # Calculate distance from mountain center
                    dx = cx - x
                    dy = cy - y
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Skip if outside mountain
                    if distance > mountain_radius:
                        continue

                    # Calculate mountain profile
                    # mountain_height at the center, 0.0 at the edge
                    t = distance / mountain_radius
                    mountain_value = mountain_height * (1.0 - t*t)

                    # Apply mountain to height map
                    result[cy, cx] += mountain_value

        # Normalize the height map
        return self.noise_gen.normalize_noise_map(result)

    def apply_height_map(self, planet_image: Image.Image, height_map: np.ndarray,
                        light_angle: float = 45.0, strength: float = 1.0) -> Image.Image:
        """
        Apply a height map to a planet image using normal mapping.

        Args:
            planet_image: Base planet image
            height_map: Height map as a 2D numpy array
            light_angle: Angle of the light source in degrees
            strength: Strength of the height map effect

        Returns:
            Planet image with surface details
        """
        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # Calculate normal map from height map
        normal_map = lighting_utils.calculate_normal_map(height_map, strength)

        # Apply directional lighting
        light_rad = math.radians(light_angle)
        light_dir = (
            -math.cos(light_rad),
            -math.sin(light_rad),
            1.0
        )

        result = lighting_utils.apply_directional_light(
            planet_image,
            normal_map,
            light_direction=light_dir,
            ambient=0.3,
            diffuse=0.7,
            specular=0.0
        )

        return result

    def add_surface_details(self, planet_image: Image.Image, terrain_type: str,
                           roughness: float = 1.0, light_angle: float = 45.0) -> Image.Image:
        """
        Add surface details to a planet image.

        Args:
            planet_image: Base planet image
            terrain_type: Type of terrain
            roughness: Roughness of the terrain (0.0 to 2.0)
            light_angle: Angle of the light source in degrees

        Returns:
            Planet image with surface details
        """
        # Generate height map
        size = planet_image.width
        height_map = self.generate_height_map(size, terrain_type, roughness)

        # Add specific features based on terrain type
        if terrain_type == "cratered":
            height_map = self.add_craters(height_map, 30, 0.02, 0.1)
        elif terrain_type == "mountainous":
            height_map = self.add_mountains(height_map, 15, 0.05, 0.2)

        # Apply height map to the planet image
        result = self.apply_height_map(planet_image, height_map, light_angle, roughness)

        return result
