"""
Furnace planet implementation.

Este módulo implementa planetas abrasadores tipo Furnace con características
como ríos de magma, tierras de brasas y paisajes volcánicos.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class FurnacePlanet(AbstractPlanet):
    """
    Furnace planet with magma rivers, ember wastes, and volcanic hellscapes.
    
    Este tipo de planeta simula mundos abrasadores con altas temperaturas,
    actividad volcánica intensa y superficies incandescentes.
    """

    # Planet type identifier
    PLANET_TYPE = "Furnace"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a furnace planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("magma_rivers", "ember_wastes", or "volcanic_hellscape")
                - magma_scale: Scale of magma patterns (default: 1.0)
                - heat_intensity: Intensity of heat effects (default: 1.0)
                - volcanic_activity: Scale of volcanic features (default: 1.0)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Furnace-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["furnace"])
        self.magma_scale = kwargs.get("magma_scale", 1.0)
        self.heat_intensity = kwargs.get("heat_intensity", 1.0)
        self.volcanic_activity = kwargs.get("volcanic_activity", 1.0)

        # Seleccionar una paleta de colores aleatoria (1-3) si no se especifica
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Asegurarse de que el ID de la paleta esté en el rango correcto
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Registrar la paleta seleccionada
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Furnace planet", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the furnace planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Furnace", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "magma_rivers":
            return self._generate_magma_rivers_texture(base_image, base_color)
        elif self.variation == "ember_wastes":
            return self._generate_ember_wastes_texture(base_image, base_color)
        elif self.variation == "volcanic_hellscape":
            return self._generate_volcanic_hellscape_texture(base_image, base_color)
        else:
            # Default to magma_rivers if variation is not recognized
            return self._generate_magma_rivers_texture(base_image, base_color)

    def _generate_magma_rivers_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a furnace texture with flowing magma rivers on a dark surface.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise maps for the magma river patterns
        # Use domain warping with higher frequency for flowing magma patterns
        magma_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.8 * self.magma_scale),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.65, 2.0, 4.0 * self.magma_scale)
            )
        )

        # Generate noise for the dark crust between magma rivers
        crust_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.5, 2.0, 3.0)
            )
        )

        # Generate heat distortion effect
        heat_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 8, 0.7, 2.0, 5.0 * self.heat_intensity)
        )

        # Combine noise maps with weights to create the final pattern
        combined_noise = self.noise_gen.combine_noise_maps(
            [magma_noise, crust_noise, heat_noise],
            [0.6, 0.3, 0.1]  # Magma is dominant, with crust and heat effects as secondary
        )

        # Create color map with the selected palette
        magma_color = self.color_palette.get_random_color("Furnace", f"highlight_{self.color_palette_id}")
        crust_color = self.color_palette.get_random_color("Furnace", f"shadow_{self.color_palette_id}")
        
        # Create a glowing magma color by blending with a bright yellow/orange
        glow_color = self.color_palette.get_random_color("Furnace", f"special_{self.color_palette_id}")
        magma_glow = self.color_palette.blend_colors(magma_color, glow_color, 0.7)
        
        color_map = {
            "base": base_color,
            "magma": magma_color,
            "magma_glow": magma_glow,
            "crust": crust_color,
        }

        # Create threshold map for the different terrain features
        threshold_map = {
            0.3: "crust",      # Dark crust (lowest areas)
            0.6: "base",       # Base terrain (mid-level)
            0.8: "magma",      # Magma rivers
            1.0: "magma_glow", # Glowing magma (highest intensity)
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_ember_wastes_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a furnace texture with vast expanses of coal and ash with glowing embers.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the coal/ash base
        coal_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.3),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.0, 3.5)
            )
        )

        # Generate noise for the ember patterns (scattered glowing points)
        ember_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.6),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 7, 0.7, 2.0, 6.0 * self.heat_intensity)
            )
        )

        # Generate noise for ash deposits
        ash_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.5, 2.0, 2.5)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [coal_noise, ember_noise, ash_noise],
            [0.5, 0.3, 0.2]  # Coal is dominant, with embers and ash as secondary
        )

        # Create color map with the selected palette
        coal_color = self.color_palette.get_random_color("Furnace", f"shadow_{self.color_palette_id}")
        ash_color = self.color_palette.blend_colors(
            coal_color,
            (128, 128, 128),  # Medium gray
            0.4
        )
        ember_color = self.color_palette.get_random_color("Furnace", f"highlight_{self.color_palette_id}")
        glow_color = self.color_palette.get_random_color("Furnace", f"special_{self.color_palette_id}")
        
        color_map = {
            "coal": coal_color,
            "ash": ash_color,
            "ember": ember_color,
            "glow": glow_color,
        }

        # Create threshold map for the different terrain features
        # Use a sharper transition for more defined ember points
        threshold_map = {
            0.4: "coal",  # Dark coal/carbon surface (lowest areas)
            0.7: "ash",   # Ash deposits (mid-level)
            0.9: "ember", # Glowing embers
            1.0: "glow",  # Brightest ember points (highest intensity)
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_volcanic_hellscape_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a furnace texture with volcanic craters and lava flows.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the volcanic terrain with craters
        crater_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.25, 0.5),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.7, 2.0, 5.0 * self.volcanic_activity)
            )
        )

        # Generate noise for lava flows
        lava_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.7 * self.magma_scale),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.65, 2.0, 4.0)
            )
        )

        # Generate noise for volcanic rock formations
        rock_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.6, 2.0, 3.0)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [crater_noise, lava_noise, rock_noise],
            [0.4, 0.4, 0.2]  # Equal emphasis on craters and lava, with rock as secondary
        )

        # Create color map with the selected palette
        rock_color = self.color_palette.get_random_color("Furnace", f"shadow_{self.color_palette_id}")
        lava_color = self.color_palette.get_random_color("Furnace", f"highlight_{self.color_palette_id}")
        crater_color = self.color_palette.blend_colors(
            rock_color,
            (50, 50, 50),  # Very dark gray
            0.6
        )
        glow_color = self.color_palette.get_random_color("Furnace", f"special_{self.color_palette_id}")
        
        color_map = {
            "rock": rock_color,
            "crater": crater_color,
            "lava": lava_color,
            "glow": glow_color,
        }

        # Create threshold map for the different terrain features
        threshold_map = {
            0.3: "crater", # Dark crater bottoms (lowest areas)
            0.6: "rock",   # Volcanic rock (mid-level)
            0.8: "lava",   # Lava flows
            1.0: "glow",   # Glowing lava (highest intensity)
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
