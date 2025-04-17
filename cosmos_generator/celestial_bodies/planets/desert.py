"""
Desert planet implementation.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class DesertPlanet(AbstractPlanet):
    """
    Desert planet with dunes, canyons, and erosion patterns.
    """

    # Planet type identifier
    PLANET_TYPE = "Desert"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a desert planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("arid" by default)
                - dune_scale: Scale of dune patterns (default: 1.0)
                - canyon_scale: Scale of canyon patterns (default: 1.0)
                - erosion_scale: Scale of erosion patterns (default: 1.0)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Desert-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["desert"])
        self.dune_scale = kwargs.get("dune_scale", 1.0)
        self.canyon_scale = kwargs.get("canyon_scale", 1.0)
        self.erosion_scale = kwargs.get("erosion_scale", 1.0)

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the desert planet.

        Returns:
            Base texture image
        """
        # Create base sphere
        base_color = self.color_palette.get_random_color("Desert", "base")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Generate noise maps
        dunes_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3 * self.dune_scale),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.5, 2.0, 4.0 * self.dune_scale)
            )
        )

        canyon_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.ridged_simplex(x, y, 4, 0.6, 2.5, 3.0 * self.canyon_scale)
        )

        erosion_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5 * self.erosion_scale),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 3, 0.4, 2.0, 5.0 * self.erosion_scale)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [dunes_noise, canyon_noise, erosion_noise],
            [0.5, 0.3, 0.2]
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
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
