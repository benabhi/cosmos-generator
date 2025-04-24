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
                - variation: Texture variation ("arid", "dunes", or "mesa")
                - dune_scale: Scale of dune patterns (default: 1.0)
                - canyon_scale: Scale of canyon patterns (default: 1.0)
                - erosion_scale: Scale of erosion patterns (default: 1.0)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Desert-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["desert"])
        self.dune_scale = kwargs.get("dune_scale", 1.0)
        self.canyon_scale = kwargs.get("canyon_scale", 1.0)
        self.erosion_scale = kwargs.get("erosion_scale", 1.0)

        # Seleccionar una paleta de colores aleatoria (1-3) si no se especifica
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Asegurarse de que el ID de la paleta esté en el rango correcto
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Registrar la paleta seleccionada
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Desert planet", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the desert planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Desert", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "arid":
            return self._generate_arid_texture(base_image, base_color)
        elif self.variation == "dunes":
            return self._generate_dunes_texture(base_image, base_color)
        elif self.variation == "mesa":
            return self._generate_mesa_texture(base_image, base_color)
        else:
            # Default to arid if variation is not recognized
            return self._generate_arid_texture(base_image, base_color)

    def _generate_arid_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate the arid desert texture (original desert texture).

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
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

        # Create color map with the selected palette
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Desert", f"highlight_{self.color_palette_id}"),
            "shadow": self.color_palette.get_random_color("Desert", f"shadow_{self.color_palette_id}"),
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

    def _generate_dunes_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a desert texture with prominent dune patterns.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise maps with more pronounced dune patterns
        # Use domain warping with higher frequency and amplitude for dune ridges
        dunes_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.6 * self.dune_scale),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 8, 0.7, 2.2, 5.0 * self.dune_scale)
            )
        )

        # Secondary dune pattern at different scale for more natural look
        secondary_dunes = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.05, 0.4 * self.dune_scale),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 4, 0.6, 2.0, 8.0 * self.dune_scale)
            )
        )

        # Wind erosion patterns
        wind_erosion = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.4 * self.erosion_scale),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.5, 2.0, 3.0 * self.erosion_scale)
            )
        )

        # Combine noise maps with higher weight on dune patterns
        combined_noise = self.noise_gen.combine_noise_maps(
            [dunes_noise, secondary_dunes, wind_erosion],
            [0.6, 0.3, 0.1]  # More emphasis on primary dune patterns
        )

        # Create color map with more contrast between highlights and shadows
        # for better definition of dune ridges, using the selected palette
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Desert", f"highlight_{self.color_palette_id}"),
            "shadow": self.color_palette.get_random_color("Desert", f"shadow_{self.color_palette_id}"),
        }

        # Create threshold map with sharper transitions
        threshold_map = {
            0.35: "shadow",  # Slightly larger shadow areas
            0.65: "base",   # Narrower base color band
            1.0: "highlight",
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_mesa_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a desert texture with mesa-like formations and plateaus.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise maps for mesa formations
        # Use cellular noise for mesa/plateau formations
        mesa_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.cellular_noise(x, y, 0.3 * self.canyon_scale)
        )

        # Plateau tops with some variation
        plateau_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.2),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.4, 2.0, 3.0)
            )
        )

        # Erosion patterns for cliff faces and canyons
        erosion_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.3 * self.erosion_scale),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.6, 2.0, 4.0 * self.erosion_scale)
            )
        )

        # Combine noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [mesa_noise, plateau_noise, erosion_noise],
            [0.5, 0.2, 0.3]  # Emphasis on mesa formations and erosion
        )

        # Create color map with more reddish tones for mesa formations
        # Get a slightly reddish base color for mesa variant, using the selected palette
        mesa_base = self.color_palette.blend_colors(
            base_color,
            (180, 70, 20),  # Reddish tone
            0.3  # 30% blend towards reddish
        )

        mesa_highlight = self.color_palette.blend_colors(
            self.color_palette.get_random_color("Desert", f"highlight_{self.color_palette_id}"),
            (220, 150, 100),  # Light reddish-orange
            0.4
        )

        mesa_shadow = self.color_palette.blend_colors(
            self.color_palette.get_random_color("Desert", f"shadow_{self.color_palette_id}"),
            (100, 40, 20),  # Dark reddish-brown
            0.4
        )

        color_map = {
            "base": mesa_base,
            "highlight": mesa_highlight,
            "shadow": mesa_shadow,
        }

        # Create threshold map with sharper transitions for cliff-like features
        threshold_map = {
            0.4: "shadow",   # Larger shadow areas for cliff faces
            0.7: "base",
            1.0: "highlight", # Plateau tops
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
