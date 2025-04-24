"""
Jovian (gas giant) planet implementation.

Este módulo implementa planetas gaseosos tipo Jovian con características
como bandas horizontales de gas, remolinos, vórtices y patrones turbulentos.
"""
from typing import Optional
from PIL import Image, ImageFilter

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class JovianPlanet(AbstractPlanet):
    """
    Jovian planet with gaseous bands, storms, and turbulent patterns.

    Este tipo de planeta simula gigantes gaseosos como Júpiter, Saturno o Neptuno,
    con diferentes variaciones de patrones atmosféricos y composiciones gaseosas.
    """

    # Planet type identifier
    PLANET_TYPE = "Jovian"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a Jovian planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("bands", "storm", or "nebulous")
                - band_scale: Scale of band patterns (default: 1.0)
                - turbulence_scale: Scale of turbulence patterns (default: 1.0)
                - color_palette_id: ID of the color palette to use (1-5, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Jovian-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["jovian"])
        self.band_scale = kwargs.get("band_scale", 1.0)
        self.turbulence_scale = kwargs.get("turbulence_scale", 1.0)

        # Seleccionar una paleta de colores aleatoria (1-5) si no se especifica
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 5))

        # Asegurarse de que el ID de la paleta esté en el rango correcto
        if self.color_palette_id < 1 or self.color_palette_id > 5:
            self.color_palette_id = self.rng.randint(1, 5)

        # Registrar la paleta seleccionada
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Jovian planet", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the Jovian planet.

        Returns:
            Base texture image
        """
        # Select the appropriate generation method based on the variation
        if self.variation == "bands":
            return self._generate_bands_texture()
        elif self.variation == "storm":
            return self._generate_storm_texture()
        elif self.variation == "nebulous":
            return self._generate_nebulous_texture()
        else:
            # Default to bands if variation is not recognized
            return self._generate_bands_texture()

    def _generate_bands_texture(self) -> Image.Image:
        """
        Generate a texture with horizontal gas bands similar to Jupiter.

        Returns:
            Texture with horizontal gas bands
        """
        # Create base sphere with appropriate color from the selected palette
        base_color = self.color_palette.get_random_color("Jovian", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Generate horizontal bands noise
        # Use a higher frequency in the y-direction to create horizontal bands
        bands_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Use simplex warp with different scales for x and y to create horizontal bands
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy * 5.0, 0.1, 0.3 * self.band_scale),
                # Use fractal simplex for the base noise
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy * 5.0, 5, 0.6, 2.0, 3.0 * self.band_scale)
            )
        )

        # Generate turbulence noise for the swirling patterns within bands
        turbulence_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4 * self.turbulence_scale),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.7, 2.0, 4.0 * self.turbulence_scale)
            )
        )

        # Combine the noise maps with more weight on the bands
        combined_noise = self.noise_gen.combine_noise_maps(
            [bands_noise, turbulence_noise],
            [0.7, 0.3]
        )

        # Create color map with multiple colors for different gas compositions
        # Usar la paleta de colores seleccionada
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Jovian", f"highlight_{self.color_palette_id}"),
            "midtone": self.color_palette.get_random_color("Jovian", f"midtone_{self.color_palette_id}"),
            "shadow": self.color_palette.get_random_color("Jovian", f"shadow_{self.color_palette_id}"),
        }

        # Create threshold map for more distinct bands
        threshold_map = {
            0.25: "shadow",
            0.5: "base",
            0.75: "midtone",
            1.0: "highlight",
        }

        # Apply the noise to the sphere
        result = self.texture_gen.apply_noise_to_sphere(
            base_image, combined_noise, color_map, threshold_map
        )

        return result

    def _generate_storm_texture(self) -> Image.Image:
        """
        Generate a texture dominated by storm patterns and turbulence.

        Returns:
            Texture with storm patterns
        """
        # Create base sphere with appropriate color from the selected palette
        base_color = self.color_palette.get_random_color("Jovian", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Generate primary storm noise with more turbulence and vortices
        storm_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Use stronger warping for more chaotic patterns
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.6 * self.turbulence_scale),
                # Use ridged simplex for more defined storm structures
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.7, 2.2, 3.5 * self.turbulence_scale)
            )
        )

        # Generate secondary vortex noise using cellular patterns
        vortex_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 8, "euclidean")
        )

        # Generate some horizontal banding for structure
        bands_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.fractal_simplex(x, y * 4.0, 4, 0.5, 2.0, 2.0 * self.band_scale)
        )

        # Combine the noise maps with emphasis on storms and vortices
        combined_noise = self.noise_gen.combine_noise_maps(
            [storm_noise, vortex_noise, bands_noise],
            [0.5, 0.3, 0.2]
        )

        # Create color map with more contrasting colors for dramatic storm appearance
        # Usar la paleta de colores seleccionada
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Jovian", f"highlight_{self.color_palette_id}"),
            "midtone": self.color_palette.get_random_color("Jovian", f"midtone_{self.color_palette_id}"),
            "shadow": self.color_palette.get_random_color("Jovian", f"shadow_{self.color_palette_id}"),
            "storm": self.color_palette.get_random_color("Jovian", "storm"),
        }

        # Create threshold map with more distinct transitions
        threshold_map = {
            0.2: "shadow",
            0.4: "base",
            0.6: "midtone",
            0.8: "highlight",
            1.0: "storm",
        }

        # Apply the noise to the sphere
        result = self.texture_gen.apply_noise_to_sphere(
            base_image, combined_noise, color_map, threshold_map
        )

        return result

    def _generate_nebulous_texture(self) -> Image.Image:
        """
        Generate a texture with a more diffuse, nebulous appearance.

        Returns:
            Texture with nebulous patterns
        """
        # Create base sphere with appropriate color from the selected palette
        base_color = self.color_palette.get_random_color("Jovian", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Generate primary nebulous noise with smoother transitions
        nebula_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Use gentler warping for smoother flows
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.05, 0.2 * self.turbulence_scale),
                # Use fractal simplex with more octaves for smoother gradients
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 8, 0.5, 2.0, 2.0 * self.turbulence_scale)
            )
        )

        # Generate secondary flow noise for subtle directional patterns
        flow_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y * 2.0,  # Stretch in y direction for subtle horizontal flow
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.3),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.6, 2.0, 3.0)
            )
        )

        # Combine the noise maps with emphasis on smooth transitions
        combined_noise = self.noise_gen.combine_noise_maps(
            [nebula_noise, flow_noise],
            [0.7, 0.3]
        )

        # Create color map with more subtle, gradient-friendly colors
        # Usar la paleta de colores seleccionada
        color_map = {
            "base": base_color,
            "highlight": self.color_palette.get_random_color("Jovian", f"highlight_{self.color_palette_id}"),
            "midtone": self.color_palette.get_random_color("Jovian", f"midtone_{self.color_palette_id}"),
            "shadow": self.color_palette.get_random_color("Jovian", f"shadow_{self.color_palette_id}"),
        }

        # Create threshold map with smoother transitions
        threshold_map = {
            0.3: "shadow",
            0.5: "base",
            0.7: "midtone",
            1.0: "highlight",
        }

        # Apply the noise to the sphere
        result = self.texture_gen.apply_noise_to_sphere(
            base_image, combined_noise, color_map, threshold_map
        )

        # Apply a subtle blur to enhance the nebulous quality
        result = result.filter(ImageFilter.GaussianBlur(radius=1.2))

        return result


