"""
Toxic planet implementation.

This module implements Toxic-type planets with characteristics
of extreme toxicity, corrosion, and alien environments hostile to life.
"""
from typing import Dict, Any, Optional
from PIL import Image

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet


class ToxicPlanet(AbstractPlanet):
    """
    Toxic planet with corrosive atmospheres, acid pools, and toxic environments.

    This type of planet simulates worlds with extreme toxicity, where the environment
    has been consumed by corrosive elements, toxic gases, and acidic compounds that
    would destroy any form of life as we know it.
    """

    # Planet type identifier
    PLANET_TYPE = "Toxic"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a toxic planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("toxic_veins", "acid_lakes", or "corrosive_storms")
                - color_palette_id: ID of the color palette to use (1-3, default: random)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Toxic-specific parameters
        self.variation = kwargs.get("variation", config.DEFAULT_PLANET_VARIATIONS["toxic"])

        # Generate toxicity level and corrosion detail based on the seed
        # This ensures consistent results for the same seed
        self.toxicity_level = 0.6 + (self.rng.random() * 0.4)  # Range: 0.6-1.0
        self.corrosion_detail = 0.7 + (self.rng.random() * 0.6)  # Range: 0.7-1.3

        # Select a random color palette (1-3) if not specified
        self.color_palette_id = kwargs.get("color_palette_id", self.rng.randint(1, 3))

        # Ensure the palette ID is in the correct range
        if self.color_palette_id < 1 or self.color_palette_id > 3:
            self.color_palette_id = self.rng.randint(1, 3)

        # Log the selected palette and parameters
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Selected color palette {self.color_palette_id} for Toxic planet", "planet")
        logger.debug(f"Generated toxicity level: {self.toxicity_level:.2f}, corrosion detail: {self.corrosion_detail:.2f}", "planet")

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the toxic planet.

        Returns:
            Base texture image
        """
        # Create base sphere with the selected color palette
        base_color = self.color_palette.get_random_color("Toxic", f"base_{self.color_palette_id}")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Select the appropriate generation method based on the variation
        if self.variation == "toxic_veins":
            return self._generate_toxic_veins_texture(base_image, base_color)
        elif self.variation == "acid_lakes":
            return self._generate_acid_lakes_texture(base_image, base_color)
        elif self.variation == "corrosive_storms":
            return self._generate_corrosive_storms_texture(base_image, base_color)
        else:
            # Default to toxic_veins if variation is not recognized
            return self._generate_toxic_veins_texture(base_image, base_color)

    def _generate_toxic_veins_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with dark dead surface and branching toxic veins like lightning.

        This creates a stark contrast between a dark, lifeless planetary surface
        and bright, fluorescent toxic veins that branch out in multiple directions
        like lightning or electrical discharges.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        from cosmos_generator.utils.logger import logger
        logger.debug(f"Generating toxic_veins texture with toxicity level {self.toxicity_level} and corrosion detail {self.corrosion_detail}", "planet")

        # Generate noise for the dark, dead surface
        # Use cellular noise for a cracked, lifeless appearance
        surface_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.cellular_noise(dx, dy, 2.5)
            )
        )

        # Generate the main toxic veins pattern
        # Use ridged noise with high frequency and strong warping for lightning-like patterns
        # The ridged noise creates ridge-like structures that work well for veins
        veins_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Strong warping creates more chaotic, branching patterns
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 1.5 * self.corrosion_detail),
                # High octave count and high frequency for detailed, thin veins
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 7, 0.9, 2.2, 4.0 * self.toxicity_level)
            )
        )

        # Generate a secondary veins pattern with different parameters
        # This will intersect with the primary pattern to create more branching
        secondary_veins = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Different warping parameters for variety
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 1.2),
                # Invert the noise (1.0 - noise) to get a different pattern that complements the first
                lambda dx, dy: 1.0 - self.noise_gen.ridged_simplex(dx, dy, 6, 0.8, 2.0, 3.5)
            )
        )

        # Generate a detail pattern for finer veins and connections
        detail_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.7),
                # Higher frequency for finer details
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.7, 2.5, 5.0)
            )
        )

        # Combine the noise patterns to create the final texture
        # The weights determine how much each pattern contributes to the final result
        combined_noise = self.noise_gen.combine_noise_maps(
            [surface_noise, veins_noise, secondary_veins, detail_noise],
            [0.3, 0.4, 0.2, 0.1]  # Surface is the base, veins are prominent, details are subtle
        )

        # Create color map with extreme contrast between dead surface and toxic veins
        # Get a very dark gray for the dead surface
        dead_surface = (15, 15, 20)  # Almost black with slight blue tint for dead appearance

        # Get a slightly lighter gray for surface variations
        surface_color = self.color_palette.get_random_color("Toxic", f"shadow_{self.color_palette_id}")
        surface_variation = self.color_palette.blend_colors(
            surface_color,
            dead_surface,
            0.7  # Mostly dead surface with slight variation
        )

        # Get extremely bright fluorescent colors for the veins
        vein_color = self.color_palette.get_random_color("Toxic", f"highlight_{self.color_palette_id}")
        # Make the vein color more intense/saturated
        bright_vein = self.color_palette.blend_colors(
            vein_color,
            (255, 255, 255),  # Pure white
            0.4  # Add brightness for better visibility
        )

        # Get a glowing version of the vein color for the halo effect
        glow_color = self.color_palette.get_random_color("Toxic", f"special_{self.color_palette_id}")

        # Create a darker version of the vein color for transition areas
        vein_shadow = self.color_palette.blend_colors(
            vein_color,
            dead_surface,
            0.5  # Blend between vein color and dark surface
        )

        color_map = {
            "dead": dead_surface,           # Darkest areas (dead planet)
            "surface": surface_variation,   # Slight variations in the surface
            "vein_shadow": vein_shadow,     # Transition areas around veins
            "vein": bright_vein,           # The toxic veins themselves
            "glow": glow_color,            # Brightest parts of the veins
        }

        # Create threshold map with sharp transitions for high contrast
        # The thresholds determine where each color appears based on the noise value
        # Higher thresholds mean the color appears in smaller areas (higher noise values)
        threshold_map = {
            0.3: "dead",         # Most of the planet is dead/dark
            0.6: "surface",      # Some surface variations
            0.8: "vein_shadow",  # Transition areas around veins
            0.9: "vein",         # The toxic veins themselves
            0.95: "glow",        # Brightest parts of the veins (tips and intersections)
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_acid_lakes_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with toxic surface and acid lakes.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the toxic surface
        surface_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.7, 2.0, 2.5)
            )
        )

        # Generate noise for the acid lakes with smoother transitions
        lakes_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.6),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.8, 2.0, 3.0 * self.toxicity_level)
            )
        )

        # Generate noise for the acid bubbles and foam
        bubble_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.6, 0.9 * self.corrosion_detail),
                lambda dx, dy: self.noise_gen.worley_noise(dx, dy, 12, "euclidean")
            )
        )

        # Combine noise maps with different weights
        combined_noise = self.noise_gen.combine_noise_maps(
            [surface_noise, lakes_noise, bubble_noise],
            [0.3, 0.5, 0.2]  # More emphasis on lakes, with surface and bubbles as accents
        )

        # Create color map with the selected palette
        surface_color = self.color_palette.get_random_color("Toxic", f"base_{self.color_palette_id}")
        acid_color = self.color_palette.get_random_color("Toxic", f"special_{self.color_palette_id}")
        bubble_color = self.color_palette.get_random_color("Toxic", f"highlight_{self.color_palette_id}")

        # Create a darker version of the surface color for shadows
        shadow_color = self.color_palette.get_random_color("Toxic", f"shadow_{self.color_palette_id}")

        color_map = {
            "surface": surface_color,
            "shadow": shadow_color,
            "acid": acid_color,
            "bubble": bubble_color,
        }

        # Create threshold map for the different terrain features
        threshold_map = {
            0.4: "shadow",     # Shadows in the lowest areas
            0.6: "surface",    # Surface covers middle elevations
            0.8: "acid",       # Acid lakes at higher elevations
            0.95: "bubble",    # Bubbles and foam at the highest points
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image

    def _generate_corrosive_storms_texture(self, base_image: Image.Image, base_color: tuple) -> Image.Image:
        """
        Generate a texture with corrosive storm patterns.

        Args:
            base_image: Base sphere image
            base_color: Base color for the planet

        Returns:
            Textured image
        """
        # Generate noise for the base surface
        surface_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.7, 2.0, 2.0)
            )
        )

        # Generate noise for the corrosive storm patterns with swirling effects
        storm_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.7 * self.corrosion_detail),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 6, 0.6, 2.0, 4.0 * self.toxicity_level)
            )
        )

        # Generate noise for the lightning and electrical discharges
        lightning_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.6, 0.9),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 7, 0.8, 2.2, 5.0)
            )
        )

        # Combine noise maps with different weights
        combined_noise = self.noise_gen.combine_noise_maps(
            [surface_noise, storm_noise, lightning_noise],
            [0.3, 0.5, 0.2]  # More emphasis on storms, with surface and lightning as accents
        )

        # Create color map with the selected palette
        surface_color = self.color_palette.get_random_color("Toxic", f"base_{self.color_palette_id}")
        storm_color = self.color_palette.get_random_color("Toxic", f"shadow_{self.color_palette_id}")
        lightning_color = self.color_palette.get_random_color("Toxic", f"highlight_{self.color_palette_id}")

        # Create a more intense version of the lightning color for electrical discharges
        discharge_color = self.color_palette.get_random_color("Toxic", f"special_{self.color_palette_id}")

        color_map = {
            "surface": surface_color,
            "storm": storm_color,
            "lightning": lightning_color,
            "discharge": discharge_color,
        }

        # Create threshold map for the different terrain features
        threshold_map = {
            0.4: "surface",     # Surface in the lowest areas
            0.7: "storm",       # Storm patterns cover most of the planet
            0.9: "lightning",   # Lightning appears at higher elevations
            0.97: "discharge",  # Electrical discharges at the highest points
        }

        # Apply noise to sphere
        textured_image = self.texture_gen.apply_noise_to_sphere(base_image, combined_noise, color_map, threshold_map)

        return textured_image
