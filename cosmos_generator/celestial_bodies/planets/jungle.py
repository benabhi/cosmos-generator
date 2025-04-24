"""
Jungle planet implementation.

This module implements Jungle-type planets with characteristics
of dense vegetation, massive flora growth, and diverse plant ecosystems.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class JunglePlanet(AbstractPlanet):
    """
    Jungle planet with dense vegetation, massive flora growth, and diverse plant ecosystems.

    This type of planet simulates worlds dominated by extreme vegetation growth,
    where the entire surface has been consumed by plant life. The dense canopies,
    massive root systems, and intertwining vines create a complex and vibrant ecosystem
    that has overtaken every available surface.
    """

    # Planet type identifier
    PLANET_TYPE = "Jungle"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a jungle planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("overgrown", "canopy", or "bioluminescent")
                - vegetation_density: Density of vegetation (default: random 0.7-1.0)
                - growth_pattern: Pattern of vegetation growth (default: random 0.6-1.2)
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Jungle-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["jungle"])
        
        # Generate jungle parameters based on the seed
        # This ensures consistent results for the same seed
        self.vegetation_density = kwargs.get("vegetation_density", 0.7 + (self.rng.random() * 0.3))  # Range: 0.7-1.0
        self.growth_pattern = kwargs.get("growth_pattern", 0.6 + (self.rng.random() * 0.6))  # Range: 0.6-1.2

        # Select a random color palette (1-3) if not specified
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Ensure the palette ID is in the correct range
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Log the selected palette and parameters
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Jungle planet", "planet")
        logger.debug(f"Generated vegetation density: {self.vegetation_density:.2f}, growth pattern: {self.growth_pattern:.2f}", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the jungle planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Jungle", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "overgrown":
            return self._generate_overgrown_texture(base_image, base_color)
        elif self.variation == "canopy":
            return self._generate_canopy_texture(base_image, base_color)
        elif self.variation == "bioluminescent":
            return self._generate_bioluminescent_texture(base_image, base_color)
        else:
            # Default to overgrown if variation is not recognized
            return self._generate_overgrown_texture(base_image, base_color)

    def _generate_overgrown_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with dense, chaotic vegetation growth.

        This variation features a surface completely overtaken by wild, untamed vegetation.
        Massive vines, roots, and plant structures intertwine in a chaotic pattern,
        creating a dense, impenetrable jungle that covers the entire planet.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the base vegetation layer
        # Use domain warping with fractal noise for organic, chaotic patterns
        vegetation_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.5 * self.growth_pattern),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.8, 2.2, 3.0 * self.vegetation_density)
            )
        )

        # Generate noise for vine and root structures
        # Use domain warping with ridged noise for intertwining vine patterns
        vine_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.7, 2.0, 4.0)
            )
        )

        # Generate noise for undergrowth and smaller plants
        # Use cellular noise for clustered vegetation patterns
        undergrowth_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.7),
                lambda dx, dy: 1.0 - self.noise_gen.cellular_noise(dx, dy, 3.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [vegetation_noise, vine_noise, undergrowth_noise],
            [0.5, 0.3, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        jungle_base = self.color_palette.get_random_color("Jungle", f"base_{self.color_palette_id}")
        jungle_highlight = self.color_palette.get_random_color("Jungle", f"highlight_{self.color_palette_id}")
        jungle_shadow = self.color_palette.get_random_color("Jungle", f"shadow_{self.color_palette_id}")
        vine_color = self.color_palette.get_random_color("Jungle", f"vine_{self.color_palette_id}")
        undergrowth_color = self.color_palette.get_random_color("Jungle", f"undergrowth_{self.color_palette_id}")

        # Create color map
        color_map = {
            "shadow": jungle_shadow,          # Deep shadows in dense vegetation
            "undergrowth": undergrowth_color, # Undergrowth and smaller plants
            "base": jungle_base,              # Main jungle canopy
            "vine": vine_color,               # Vines and root structures
            "highlight": jungle_highlight,    # Sunlit areas of vegetation
        }

        # Create threshold map
        threshold_map = {
            0.2: "shadow",       # Deep shadows in dense vegetation
            0.4: "undergrowth",  # Undergrowth and smaller plants
            0.7: "base",         # Main jungle canopy
            0.9: "vine",         # Vines and root structures
            1.0: "highlight",    # Sunlit areas of vegetation
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_canopy_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with a layered, structured canopy.

        This variation features a more organized vegetation pattern with distinct
        canopy layers. The surface shows a structured ecosystem with different
        vegetation zones, from dense canopy tops to mid-level growth and understory.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the upper canopy layer
        # Use domain warping with fractal noise for organic, flowing patterns
        canopy_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.35 * self.growth_pattern),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.75, 2.0, 2.5 * self.vegetation_density)
            )
        )

        # Generate noise for mid-level vegetation
        # Use domain warping with different parameters for varied patterns
        midlevel_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.25, 0.45),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.65, 2.0, 3.0)
            )
        )

        # Generate noise for understory vegetation
        # Use cellular noise for clustered understory patterns
        understory_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.35, 0.55),
                lambda dx, dy: 1.0 - self.noise_gen.cellular_noise(dx, dy, 2.5)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [canopy_noise, midlevel_noise, understory_noise],
            [0.4, 0.4, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        canopy_color = self.color_palette.get_random_color("Jungle", f"canopy_{self.color_palette_id}")
        midlevel_color = self.color_palette.get_random_color("Jungle", f"midlevel_{self.color_palette_id}")
        understory_color = self.color_palette.get_random_color("Jungle", f"understory_{self.color_palette_id}")
        shadow_color = self.color_palette.get_random_color("Jungle", f"shadow_{self.color_palette_id}")
        highlight_color = self.color_palette.get_random_color("Jungle", f"highlight_{self.color_palette_id}")

        # Create color map
        color_map = {
            "shadow": shadow_color,        # Deep shadows in dense vegetation
            "understory": understory_color, # Understory vegetation
            "midlevel": midlevel_color,     # Mid-level vegetation
            "canopy": canopy_color,         # Upper canopy
            "highlight": highlight_color,   # Sunlit areas of canopy
        }

        # Create threshold map with distinct layers
        threshold_map = {
            0.2: "shadow",      # Deep shadows in dense vegetation
            0.4: "understory",  # Understory vegetation
            0.6: "midlevel",    # Mid-level vegetation
            0.85: "canopy",     # Upper canopy
            1.0: "highlight",   # Sunlit areas of canopy
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_bioluminescent_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with bioluminescent vegetation.

        This variation features a dark jungle environment with bioluminescent plants
        that create patterns of glowing vegetation across the surface. The contrast
        between the dark background and the glowing flora creates a striking visual effect.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the base dark vegetation
        # Use domain warping with fractal noise for organic patterns
        dark_vegetation_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4 * self.growth_pattern),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.7, 2.0, 3.0 * self.vegetation_density)
            )
        )

        # Generate noise for bioluminescent patterns
        # Use domain warping with cellular noise for clustered glowing patterns
        bioluminescent_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.5),
                lambda dx, dy: 1.0 - self.noise_gen.worley_noise(dx, dy, int(12 * self.vegetation_density), "euclidean")
            )
        )

        # Generate noise for glowing veins and patterns
        # Use domain warping with ridged noise for vein-like patterns
        vein_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.25, 0.45),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.8, 2.2, 4.0)
            )
        )

        # Combine the noise maps
        combined_noise = self.noise_gen.combine_noise_maps(
            [dark_vegetation_noise, bioluminescent_noise, vein_noise],
            [0.4, 0.4, 0.2]  # Weights for each noise map
        )

        # Get colors from the palette
        dark_base = self.color_palette.get_random_color("Jungle", f"dark_base_{self.color_palette_id}")
        glow_bright = self.color_palette.get_random_color("Jungle", f"glow_bright_{self.color_palette_id}")
        glow_medium = self.color_palette.get_random_color("Jungle", f"glow_medium_{self.color_palette_id}")
        glow_dim = self.color_palette.get_random_color("Jungle", f"glow_dim_{self.color_palette_id}")
        shadow = self.color_palette.get_random_color("Jungle", f"shadow_{self.color_palette_id}")

        # Create color map
        color_map = {
            "shadow": shadow,       # Deep shadows
            "dark": dark_base,      # Dark vegetation
            "dim": glow_dim,        # Dimly glowing vegetation
            "medium": glow_medium,  # Medium glowing vegetation
            "bright": glow_bright,  # Brightly glowing vegetation
        }

        # Create threshold map with sharp transitions for glowing elements
        threshold_map = {
            0.2: "shadow",   # Deep shadows
            0.5: "dark",     # Dark vegetation
            0.7: "dim",      # Dimly glowing vegetation
            0.85: "medium",  # Medium glowing vegetation
            1.0: "bright",   # Brightly glowing vegetation
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
