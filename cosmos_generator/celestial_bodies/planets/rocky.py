"""
Rocky planet implementation.

This module implements Rocky-type planets with characteristics
of rugged, cratered, and fractured terrains with harsh mountainous landscapes.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class RockyPlanet(AbstractPlanet):
    """
    Rocky planet with rugged terrains, craters, and fractured landscapes.

    This type of planet simulates barren worlds with extreme geological features,
    including jagged mountains, deep canyons, massive craters, and fractured
    terrain. The harsh conditions have created dramatic and inhospitable landscapes
    dominated by exposed rock formations.
    """

    # Planet type identifier
    PLANET_TYPE = "Rocky"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a rocky planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("cratered", "fractured", or "mountainous")
                - crater_density: Density of crater formations (default: random 0.6-1.0)
                - terrain_roughness: Roughness of the terrain (default: random 0.7-1.2)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Rocky-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["rocky"])

        # Generate rocky parameters based on the seed
        # This ensures consistent results for the same seed
        self.crater_density = kwargs.get("crater_density", 0.6 + (self.rng.random() * 0.4))  # Range: 0.6-1.0
        self.terrain_roughness = kwargs.get("terrain_roughness", 0.7 + (self.rng.random() * 0.5))  # Range: 0.7-1.2

        # Select a random color palette (1-3) if not specified
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Ensure the palette ID is in the correct range
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Log the selected palette and parameters
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Rocky planet", "planet")
        logger.debug(f"Generated crater density: {self.crater_density:.2f}, terrain roughness: {self.terrain_roughness:.2f}", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the rocky planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Rocky", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "cratered":
            return self._generate_cratered_texture(base_image, base_color)
        elif self.variation == "fractured":
            return self._generate_fractured_texture(base_image, base_color)
        elif self.variation == "mountainous":
            return self._generate_mountainous_texture(base_image, base_color)
        else:
            # Default to cratered if variation is not recognized
            return self._generate_cratered_texture(base_image, base_color)

    def _generate_cratered_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with a heavily cratered surface.

        This variation features a surface dominated by impact craters of various sizes,
        similar to Mercury or the Moon. The terrain is rough and uneven with
        overlapping crater rims and ejecta blankets.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the base rocky terrain
        # Use domain warping with cellular noise for a cratered appearance
        base_terrain = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 2.0 * self.terrain_roughness)
            )
        )

        # Generate noise for craters
        # Use cellular noise with different parameters for crater formations
        crater_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: 1.0 - self.noise_gen.worley_noise(dx, dy, int(15 * self.crater_density), "euclidean")
            )
        )

        # Generate noise for crater rims and ejecta
        # Use ridged noise for crater rims and ejecta patterns
        rim_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.35),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 4, 0.7, 2.0, 3.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [base_terrain, crater_noise, rim_noise],
            [0.3, 0.5, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        rock_base = self.color_palette.get_random_color("Rocky", f"base_{self.color_palette_id}")
        rock_highlight = self.color_palette.get_random_color("Rocky", f"highlight_{self.color_palette_id}")
        rock_shadow = self.color_palette.get_random_color("Rocky", f"shadow_{self.color_palette_id}")
        crater_color = self.color_palette.get_random_color("Rocky", f"crater_{self.color_palette_id}")

        # Create color map
        color_map = {
            "shadow": rock_shadow,       # Deep shadows in craters
            "crater": crater_color,      # Crater floors
            "base": rock_base,           # Main rocky surface
            "highlight": rock_highlight, # Crater rims and elevated areas
        }

        # Create threshold map
        threshold_map = {
            0.3: "shadow",    # Deep shadows in craters
            0.5: "crater",    # Crater floors
            0.8: "base",      # Main rocky surface
            1.0: "highlight", # Crater rims and elevated areas
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_fractured_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with a heavily fractured and cracked surface.

        This variation features a surface dominated by deep canyons, fissures,
        and tectonic fractures. The terrain appears broken and split apart by
        powerful geological forces, creating a network of cracks across the surface.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the base rocky terrain
        # Use domain warping with ridged noise for a rough, broken appearance
        base_terrain = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.8, 2.0, 3.0 * self.terrain_roughness)
            )
        )

        # Generate noise for fractures and canyons
        # Use cellular noise with high frequency for fracture patterns
        fracture_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 4.0)
            )
        )

        # Generate noise for secondary fractures
        # Use different cellular noise parameters for smaller fractures
        secondary_fracture = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.7),
                lambda dx, dy: 1.0 - self.noise_gen.cellular_noise(dx, dy, 6.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [base_terrain, fracture_noise, secondary_fracture],
            [0.4, 0.4, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        rock_base = self.color_palette.get_random_color("Rocky", f"base_{self.color_palette_id}")
        rock_highlight = self.color_palette.get_random_color("Rocky", f"highlight_{self.color_palette_id}")
        rock_shadow = self.color_palette.get_random_color("Rocky", f"shadow_{self.color_palette_id}")
        fracture_color = self.color_palette.get_random_color("Rocky", f"fracture_{self.color_palette_id}")

        # Create color map
        color_map = {
            "deep": rock_shadow,        # Deep canyons and fractures
            "fracture": fracture_color, # Fracture zones
            "base": rock_base,          # Main rocky surface
            "ridge": rock_highlight,    # Elevated ridges and plateaus
        }

        # Create threshold map with sharp transitions for fractures
        threshold_map = {
            0.3: "deep",      # Deep canyons and fractures
            0.5: "fracture",  # Fracture zones
            0.8: "base",      # Main rocky surface
            1.0: "ridge",     # Elevated ridges and plateaus
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_mountainous_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with extreme jagged mountainous terrain.

        This variation features a surface dominated by sharp, jagged mountain ranges,
        deep chasms, and dramatic peaks. The terrain has extreme elevation changes
        with angular ridgelines and steep cliff faces, creating a harsh, forbidding landscape.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the primary mountain ridges
        # Use domain warping with ridged noise for sharp mountain ranges
        ridge_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3 * self.terrain_roughness),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 8, 0.95, 2.5, 5.0)
            )
        )

        # Generate noise for secondary mountain formations
        # Use different ridged noise parameters for varied mountain shapes
        secondary_ridge = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.9, 2.2, 3.5)
            )
        )

        # Generate noise for deep chasms and canyons
        # Use cellular noise with high contrast for deep valleys
        chasm_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.35),
                lambda dx, dy: 1.0 - self.noise_gen.cellular_noise(dx, dy, 4.0)
            )
        )

        # Generate noise for rocky texture details
        # Use cellular noise for fine rocky details
        rock_detail = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.7),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 5.0)
            )
        )

        # Combine the noise maps with weights that emphasize the jagged mountains
        combined_noise = self.noise_gen.combine_noise_maps(
            [ridge_noise, secondary_ridge, chasm_noise, rock_detail],
            [0.45, 0.25, 0.2, 0.1]  # Weights for each noise map
        )

        # Get colors from the palette
        rock_base = self.color_palette.get_random_color("Rocky", f"base_{self.color_palette_id}")
        rock_highlight = self.color_palette.get_random_color("Rocky", f"highlight_{self.color_palette_id}")
        rock_shadow = self.color_palette.get_random_color("Rocky", f"shadow_{self.color_palette_id}")
        peak_color = self.color_palette.get_random_color("Rocky", f"peak_{self.color_palette_id}")
        fracture_color = self.color_palette.get_random_color("Rocky", f"fracture_{self.color_palette_id}")

        # Create color map with more distinct color zones
        color_map = {
            "chasm": fracture_color,  # Deep chasms and fractures
            "valley": rock_shadow,    # Deep valleys and canyons
            "base": rock_base,        # Main rocky surface
            "ridge": rock_highlight,  # Mountain ridges
            "peak": peak_color,       # Mountain peaks
        }

        # Create threshold map with sharper transitions for more dramatic terrain
        threshold_map = {
            0.2: "chasm",     # Deep chasms and fractures
            0.4: "valley",    # Deep valleys and canyons
            0.7: "base",      # Main rocky surface
            0.9: "ridge",     # Mountain ridges
            1.0: "peak",      # Mountain peaks
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
