"""
Vital planet implementation.

This module implements Vital-type planets with characteristics
similar to Earth, featuring continents, oceans, and diverse biomes.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class VitalPlanet(AbstractPlanet):
    """
    Vital planet with Earth-like features, continents, oceans, and diverse biomes.

    This type of planet simulates habitable worlds with a balance of land and water,
    diverse ecosystems, and climate patterns similar to Earth.
    """

    # Planet type identifier
    PLANET_TYPE = "Vital"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a vital planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("earthlike", "archipelago", or "pangaea")
                - ocean_level: Level of ocean coverage (default: 0.6)
                - land_detail: Detail level of landmasses (default: 1.0)
                - climate_diversity: Diversity of climate zones (default: 1.0)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Vital-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["vital"])
        self.ocean_level = kwargs.get("ocean_level", 0.6)
        self.land_detail = kwargs.get("land_detail", 1.0)
        self.climate_diversity = kwargs.get("climate_diversity", 1.0)

        # Select a random color palette (1-3) if not specified
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Ensure the palette ID is in the correct range
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Log the selected palette
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Vital planet", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the vital planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Vital", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "earthlike":
            return self._generate_earthlike_texture(base_image, base_color)
        elif self.variation == "archipelago":
            return self._generate_archipelago_texture(base_image, base_color)
        elif self.variation == "pangaea":
            return self._generate_pangaea_texture(base_image, base_color)
        else:
            # Default to earthlike if variation is not recognized
            return self._generate_earthlike_texture(base_image, base_color)

    def _generate_earthlike_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with balanced continents and oceans similar to Earth.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for continents and oceans
        # Use domain warping with medium frequency for realistic landmasses
        continent_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5 * self.land_detail),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.7, 2.0, 3.0)
            )
        )

        # Generate noise for climate zones (latitude-based)
        climate_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: abs(dy * 2 - 1) * self.climate_diversity  # Latitude-based climate
            )
        )

        # Generate noise for terrain elevation
        elevation_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 4, 0.6, 2.0, 2.5 * self.land_detail)
            )
        )

        # Combine noise maps with weights to create the final pattern
        combined_noise = self.noise_gen.combine_noise_maps(
            [continent_noise, climate_noise, elevation_noise],
            [0.6, 0.2, 0.2]  # Continents are dominant, with climate and elevation as secondary
        )

        # Create color map with the selected palette
        water_color = self.color_palette.get_random_color("Vital", f"water_{self.color_palette_id}")
        land_color = self.color_palette.get_random_color("Vital", f"land_{self.color_palette_id}")
        highlight_color = self.color_palette.get_random_color("Vital", f"highlight_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Vital", f"shadow_{self.color_palette_id}")
        ice_color = self.color_palette.get_random_color("Vital", f"ice_{self.color_palette_id}")

        color_map = {
            "deep_ocean": self.color_palette.adjust_brightness(water_color, 0.7),
            "ocean": water_color,
            "shallow_water": self.color_palette.adjust_brightness(water_color, 1.3),
            "coast": self.color_palette.blend_colors(water_color, land_color, 0.7),
            "lowland": land_color,
            "highland": highlight_color,
            "mountain": shadow_color,
            "ice": ice_color,
        }

        # Create threshold map for the different terrain features
        # Adjust ocean level based on parameter
        ocean_threshold = self.ocean_level
        threshold_map = {
            ocean_threshold * 0.7: "deep_ocean",    # Deep ocean (lowest areas)
            ocean_threshold * 0.9: "ocean",         # Ocean
            ocean_threshold: "shallow_water",       # Shallow water
            ocean_threshold + 0.05: "coast",        # Coastal areas
            0.75: "lowland",                        # Lowlands
            0.85: "highland",                       # Highlands
            0.95: "mountain",                       # Mountains
            1.0: "ice",                             # Ice caps (highest areas)
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_archipelago_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with numerous small islands and archipelagos.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for islands and archipelagos
        # Use cellular noise for scattered island patterns
        island_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.worley_noise(dx, dy, int(10 * self.land_detail), "euclidean")
            )
        )

        # Generate noise for ocean currents and depth
        ocean_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.6, 2.0, 2.5)
            )
        )

        # Generate noise for island elevation and vegetation
        vegetation_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.7),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.7, 2.0, 3.0 * self.climate_diversity)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [island_noise, ocean_noise, vegetation_noise],
            [0.6, 0.2, 0.2]  # Islands are dominant
        )

        # Create color map with the selected palette
        water_color = self.color_palette.get_random_color("Vital", f"water_{self.color_palette_id}")
        land_color = self.color_palette.get_random_color("Vital", f"land_{self.color_palette_id}")
        highlight_color = self.color_palette.get_random_color("Vital", f"highlight_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Vital", f"shadow_{self.color_palette_id}")

        # Create more varied water colors
        deep_water = self.color_palette.adjust_brightness(water_color, 0.6)
        medium_water = self.color_palette.adjust_brightness(water_color, 0.8)
        shallow_water = self.color_palette.adjust_brightness(water_color, 1.2)

        # Create more varied land colors
        beach = self.color_palette.blend_colors(water_color, land_color, 0.7)
        lowland = land_color
        forest = self.color_palette.blend_colors(land_color, highlight_color, 0.6)
        mountain = shadow_color

        color_map = {
            "deep_water": deep_water,
            "medium_water": medium_water,
            "shallow_water": shallow_water,
            "beach": beach,
            "lowland": lowland,
            "forest": forest,
            "mountain": mountain,
        }

        # Create threshold map for the different terrain features
        # Higher ocean level for archipelago
        ocean_threshold = max(0.7, self.ocean_level)
        threshold_map = {
            ocean_threshold * 0.7: "deep_water",    # Deep ocean
            ocean_threshold * 0.85: "medium_water", # Medium depth ocean
            ocean_threshold: "shallow_water",       # Shallow water
            ocean_threshold + 0.05: "beach",        # Beaches
            ocean_threshold + 0.1: "lowland",       # Lowlands
            ocean_threshold + 0.15: "forest",       # Forests
            1.0: "mountain",                        # Mountains
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_pangaea_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with a single large supercontinent and diverse biomes.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the supercontinent
        # Use domain warping with lower frequency for a large continuous landmass
        continent_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3 * self.land_detail),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.8, 2.0, 2.0)
            )
        )

        # Generate noise for biome diversity
        biome_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.0, 4.0 * self.climate_diversity)
            )
        )

        # Generate noise for terrain features (mountains, valleys)
        terrain_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.7, 2.0, 3.0 * self.land_detail)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [continent_noise, biome_noise, terrain_noise],
            [0.7, 0.15, 0.15]  # Continent shape is dominant
        )

        # Create color map with the selected palette
        water_color = self.color_palette.get_random_color("Vital", f"water_{self.color_palette_id}")
        land_color = self.color_palette.get_random_color("Vital", f"land_{self.color_palette_id}")
        highlight_color = self.color_palette.get_random_color("Vital", f"highlight_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Vital", f"shadow_{self.color_palette_id}")
        ice_color = self.color_palette.get_random_color("Vital", f"ice_{self.color_palette_id}")

        # Create diverse biome colors
        desert = self.color_palette.blend_colors(land_color, (255, 215, 0), 0.4)  # Golden tint
        forest = self.color_palette.blend_colors(land_color, highlight_color, 0.7)
        tundra = self.color_palette.blend_colors(land_color, ice_color, 0.4)
        mountain = shadow_color

        color_map = {
            "ocean": water_color,
            "coast": self.color_palette.blend_colors(water_color, land_color, 0.7),
            "desert": desert,
            "plains": land_color,
            "forest": forest,
            "tundra": tundra,
            "mountain": mountain,
            "ice": ice_color,
        }

        # Create threshold map for the different terrain features
        # Lower ocean level for pangaea
        ocean_threshold = min(0.5, self.ocean_level)
        threshold_map = {
            ocean_threshold: "ocean",       # Ocean
            ocean_threshold + 0.05: "coast", # Coastal areas
            0.6: "desert",                  # Desert regions
            0.7: "plains",                  # Plains
            0.8: "forest",                  # Forests
            0.9: "tundra",                  # Tundra
            0.95: "mountain",               # Mountains
            1.0: "ice",                     # Ice caps
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
