"""
Ice planet implementation.

This module implements Ice-type planets with characteristics
of frozen worlds, glaciers, ice caps, and eternal winter landscapes.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class IcePlanet(AbstractPlanet):
    """
    Ice planet with frozen landscapes, glaciers, and snow-covered terrain.

    This type of planet simulates worlds locked in eternal winter, with
    various ice formations, frozen oceans, and snow-covered mountains.
    The extreme cold has created beautiful but harsh landscapes of ice.
    """

    # Planet type identifier
    PLANET_TYPE = "Ice"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize an ice planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("glacier", "tundra", or "frozen_ocean")
                - ice_crystal_size: Size of ice crystal formations (default: random 0.7-1.3)
                - snow_coverage: Coverage of snow features (default: random 0.6-1.0)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Ice-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["ice"])
        
        # Generate ice parameters based on the seed
        # This ensures consistent results for the same seed
        self.ice_crystal_size = kwargs.get("ice_crystal_size", 0.7 + (self.rng.random() * 0.6))  # Range: 0.7-1.3
        self.snow_coverage = kwargs.get("snow_coverage", 0.6 + (self.rng.random() * 0.4))  # Range: 0.6-1.0

        # Select a random color palette (1-3) if not specified
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Ensure the palette ID is in the correct range
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Log the selected palette and parameters
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Ice planet", "planet")
        logger.debug(f"Generated ice crystal size: {self.ice_crystal_size:.2f}, snow coverage: {self.snow_coverage:.2f}", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the ice planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Ice", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "glacier":
            return self._generate_glacier_texture(base_image, base_color)
        elif self.variation == "tundra":
            return self._generate_tundra_texture(base_image, base_color)
        elif self.variation == "frozen_ocean":
            return self._generate_frozen_ocean_texture(base_image, base_color)
        else:
            # Default to glacier if variation is not recognized
            return self._generate_glacier_texture(base_image, base_color)

    def _generate_glacier_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with massive ice formations and deep crevasses.

        This variation features large glaciers with deep blue ice, crevasses,
        and crystalline structures. The surface has a mix of smooth ice sheets
        and jagged ice formations.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the glacier surface
        # Use domain warping with ridged noise for crevasses and ice formations
        glacier_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5 * self.ice_crystal_size),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.8, 2.0, 3.5)
            )
        )

        # Generate noise for ice crevasses
        # Use cellular noise for cracks and crevasses in the ice
        crevasse_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 2.0 * self.ice_crystal_size)
            )
        )

        # Generate noise for crystalline structures
        # Use fractal noise for the crystalline patterns in the ice
        crystal_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.7, 2.2, 4.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [glacier_noise, crevasse_noise, crystal_noise],
            [0.5, 0.3, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        ice_base = self.color_palette.get_random_color("Ice", f"base_{self.color_palette_id}")
        ice_highlight = self.color_palette.get_random_color("Ice", f"highlight_{self.color_palette_id}")
        ice_shadow = self.color_palette.get_random_color("Ice", f"shadow_{self.color_palette_id}")
        ice_deep = self.color_palette.get_random_color("Ice", f"deep_{self.color_palette_id}")

        # Create color map
        color_map = {
            "deep": ice_deep,           # Deep crevasses and shadows
            "shadow": ice_shadow,       # Shadowed areas
            "base": ice_base,           # Main ice color
            "highlight": ice_highlight, # Reflective ice surfaces
        }

        # Create threshold map
        threshold_map = {
            0.3: "deep",      # Deep crevasses
            0.5: "shadow",    # Shadowed areas
            0.8: "base",      # Main ice surface
            1.0: "highlight", # Reflective peaks and ridges
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_tundra_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with snow-covered plains and rocky outcrops.

        This variation features vast snow-covered plains with occasional
        rocky outcrops and frozen vegetation. The surface has a mix of
        smooth snow fields and rough, icy terrain.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the snow plains
        # Use fractal simplex noise for gentle snow drifts
        snow_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.0, 3.0 * self.snow_coverage)
            )
        )

        # Generate noise for rocky outcrops
        # Use cellular noise for rocky areas poking through the snow
        rock_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 3.0)
            )
        )

        # Generate noise for frozen vegetation patterns
        # Use ridged noise for patterns resembling frozen vegetation
        vegetation_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.5),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 4, 0.7, 2.0, 4.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [snow_noise, rock_noise, vegetation_noise],
            [0.6, 0.25, 0.15]  # Weights for each noise map
        )

        # Get colors from the palette
        snow_color = self.color_palette.get_random_color("Ice", f"highlight_{self.color_palette_id}")
        ice_color = self.color_palette.get_random_color("Ice", f"base_{self.color_palette_id}")
        rock_color = self.color_palette.get_random_color("Ice", f"rock_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Ice", f"shadow_{self.color_palette_id}")

        # Create color map
        color_map = {
            "rock": rock_color,     # Rocky outcrops
            "shadow": shadow_color, # Shadowed areas
            "ice": ice_color,       # Icy areas
            "snow": snow_color,     # Snow-covered areas
        }

        # Create threshold map
        threshold_map = {
            0.3: "rock",    # Rocky outcrops
            0.5: "shadow",  # Shadowed areas
            0.7: "ice",     # Icy areas
            1.0: "snow",    # Snow-covered areas
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_frozen_ocean_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with a frozen ocean surface and ice floes.

        This variation features a frozen ocean with cracked ice sheets,
        pressure ridges, and ice floes. The surface has a mix of smooth
        ice and jagged pressure ridges where ice sheets have collided.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the frozen ocean surface
        # Use domain warping with cellular noise for ice floes and cracks
        ocean_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 2.5)
            )
        )

        # Generate noise for pressure ridges
        # Use ridged noise for pressure ridges where ice sheets meet
        ridge_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5 * self.ice_crystal_size),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.8, 2.0, 3.0)
            )
        )

        # Generate noise for ice cracks
        # Use cellular noise with a different scale for cracks in the ice
        crack_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: 1.0 - self.noise_gen.cellular_noise(dx, dy, 4.0)  # Invert for cracks
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [ocean_noise, ridge_noise, crack_noise],
            [0.5, 0.3, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        ice_color = self.color_palette.get_random_color("Ice", f"base_{self.color_palette_id}")
        water_color = self.color_palette.get_random_color("Ice", f"water_{self.color_palette_id}")
        ridge_color = self.color_palette.get_random_color("Ice", f"highlight_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Ice", f"shadow_{self.color_palette_id}")

        # Create color map
        color_map = {
            "water": water_color,   # Exposed water in cracks
            "shadow": shadow_color, # Shadowed areas
            "ice": ice_color,       # Main ice surface
            "ridge": ridge_color,   # Pressure ridges
        }

        # Create threshold map
        threshold_map = {
            0.3: "water",   # Water in cracks
            0.5: "shadow",  # Shadowed areas
            0.8: "ice",     # Main ice surface
            1.0: "ridge",   # Pressure ridges
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
