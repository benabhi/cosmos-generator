"""
Ocean planet implementation.
"""
from typing import Dict, Any, Optional
from PIL import Image, ImageChops, ImageEnhance, ImageDraw

from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet
from cosmos_generator.utils import image_utils


class OceanPlanet(AbstractPlanet):
    """
    Ocean planet with vast seas, archipelagos, and varying depths.
    """

    # Planet type identifier
    PLANET_TYPE = "Ocean"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize an ocean planet.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
                - variation: Texture variation ("water_world" or "archipelago")
                - wave_scale: Scale of wave patterns (default: 1.0)
                - depth_scale: Scale of depth variations (default: 1.0)
                - island_coverage: Coverage of islands, 0.0-1.0 (default: 0.15)
        """
        super().__init__(seed=seed, size=size, **kwargs)

        # Import here to avoid circular imports
        import config

        # Ocean-specific parameters
        # For backward compatibility, check both 'variation' and 'ocean_style'
        variation = kwargs.get("variation", None)
        ocean_style = kwargs.get("ocean_style", None)

        if variation is not None:
            self.variation = variation
        elif ocean_style is not None:
            self.variation = ocean_style
        else:
            self.variation = config.DEFAULT_PLANET_VARIATIONS["ocean"]

        # Keep ocean_style for backward compatibility
        self.ocean_style = self.variation

        self.wave_scale = kwargs.get("wave_scale", 1.0)
        self.depth_scale = kwargs.get("depth_scale", 1.0)
        self.island_coverage = kwargs.get("island_coverage", 0.15)  # 0.0-1.0, higher means more islands

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the ocean planet.

        Returns:
            Base texture image
        """
        # Create base sphere with ocean color
        base_color = self.color_palette.get_random_color("Ocean", "base")
        base_image = self.texture_gen.create_base_sphere(self.size, base_color)

        # Check if we're generating a water world or archipelago
        if self.ocean_style == "water_world":
            # For water world, create a completely uniform texture with just water
            # Only generate waves noise for reflections
            waves_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.domain_warp(
                    x, y,
                    lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.4 * self.wave_scale),
                    lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.0, 3.0 * self.wave_scale)
                )
            )

            # Create a completely uniform ocean texture for water world
            # Just use the base color for the entire planet
            ocean_color = self.color_palette.get_random_color("Ocean", "base")

            # Create a uniform sphere with the ocean color
            uniform_sphere = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(uniform_sphere)
            draw.ellipse((0, 0, self.size-1, self.size-1), fill=ocean_color)

            # Apply lighting to the uniform sphere
            ocean_image = self.texture_gen.apply_lighting(
                uniform_sphere,
                light_angle=self.light_angle,
                light_intensity=self.light_intensity,
                falloff=self.light_falloff
            )

        else:  # archipelago style
            # Generate more complex noise maps for archipelago

            # 1. Ocean waves - small scale noise for surface texture
            waves_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.domain_warp(
                    x, y,
                    lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.4 * self.wave_scale),
                    lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 5, 0.6, 2.0, 3.0 * self.wave_scale)
                )
            )

            # 2. Ocean depths - larger scale noise for deep vs shallow areas
            depths_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 4, 0.5, 2.0, 2.0 * self.depth_scale)
            )

            # 3. Currents - medium scale noise for ocean currents
            currents_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.domain_warp(
                    x, y,
                    lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.1, 0.2),
                    lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 3, 0.4, 2.0, 6.0)
                )
            )

            # Combine noise maps with different weights
            # Depths and currents have more influence than waves
            ocean_noise = self.noise_gen.combine_noise_maps(
                [waves_noise, depths_noise, currents_noise],
                [0.2, 0.5, 0.3]
            )

            # Create color map for ocean features
            color_map = {
                "deep": self.color_palette.get_random_color("Ocean", "shadow"),  # Deep ocean
                "base": base_color,  # Mid-depth ocean
                "shallow": self.color_palette.get_random_color("Ocean", "highlight"),  # Shallow waters
            }

            # Create threshold map for ocean depths
            threshold_map = {
                0.35: "deep",
                0.7: "base",
                1.0: "shallow",
            }

            # Apply ocean noise to sphere with proper lighting
            # First create the base texture with the noise
            ocean_texture = self.texture_gen.apply_noise_to_sphere(base_image, ocean_noise, color_map, threshold_map)

            # Then apply lighting to ensure all parts are properly shaded
            ocean_image = self.texture_gen.apply_lighting(
                ocean_texture,
                light_angle=self.light_angle,
                light_intensity=self.light_intensity,
                falloff=self.light_falloff
            )

        # For water world style, we're done - just add shimmer
        if self.ocean_style == "water_world":
            # For water world, no islands - just use the ocean image
            result = ocean_image
        else:  # archipelago style with islands
            # Generate islands noise - only needed for archipelago style
            islands_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.ridged_simplex(x, y, 3, 0.7, 2.5, 4.0)
            )

            # Now handle islands separately to have more control
            # Threshold the islands noise to create land masses
            # The threshold is based on the island_coverage parameter
            island_threshold = 1.0 - self.island_coverage

            # Create a mask for the islands
            island_mask = Image.new("L", (self.size, self.size), 0)
            island_data = island_mask.load()

            for y in range(self.size):
                for x in range(self.size):
                    if islands_noise[y, x] > island_threshold:
                        # Scale alpha based on how far above threshold
                        alpha = int(255 * (islands_noise[y, x] - island_threshold) / (1.0 - island_threshold))
                        island_data[x, y] = alpha

            # Apply circular mask to the islands to keep them on the planet
            circle_mask = image_utils.create_circle_mask(self.size)
            island_mask = ImageChops.multiply(island_mask, circle_mask)

            # Create island layer with land color
            land_color = self.color_palette.get_random_color("Ocean", "land")
            islands = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))

            # Fill the islands with the land color
            for y in range(self.size):
                for x in range(self.size):
                    if island_mask.getpixel((x, y)) > 0:
                        # Vary the land color slightly based on the island noise
                        variation = (islands_noise[y, x] - island_threshold) / (1.0 - island_threshold)
                        r, g, b = land_color
                        # Lighter at higher elevations
                        r = min(255, int(r * (1.0 + variation * 0.3)))
                        g = min(255, int(g * (1.0 + variation * 0.3)))
                        b = min(255, int(b * (1.0 + variation * 0.3)))

                        # Set the pixel with alpha based on the mask
                        alpha = island_mask.getpixel((x, y))
                        islands.putpixel((x, y), (r, g, b, alpha))

            # Apply lighting to islands to match the ocean
            # This is a simplified version since we're just adding the islands on top
            islands = self.texture_gen.apply_lighting(
                islands,
                light_angle=self.light_angle,
                light_intensity=self.light_intensity,
                falloff=self.light_falloff
            )

            # Composite the islands over the ocean
            result = Image.alpha_composite(ocean_image, islands)

        # Add a subtle shimmer effect to the water
        shimmer = Image.new("RGBA", (self.size, self.size), (255, 255, 255, 0))
        shimmer_data = shimmer.load()
        circle_mask = image_utils.create_circle_mask(self.size)

        for y in range(self.size):
            for x in range(self.size):
                # For water world, add shimmer everywhere
                # For archipelago, only add shimmer to water areas (not islands)
                add_shimmer = True
                if self.ocean_style == "archipelago":
                    # Check if we're on an island - only if we have an island_mask
                    if 'island_mask' in locals() and island_mask.getpixel((x, y)) > 50:
                        add_shimmer = False

                if add_shimmer:
                    # Use the waves noise for the shimmer effect
                    # Use the same shimmer effect for both styles, but more intense for water world
                    shimmer_intensity = waves_noise[y, x]

                    if self.ocean_style == "water_world":
                        # More intense shimmer for water world
                        if shimmer_intensity > 0.65:  # Lower threshold for more shimmer
                            # Calculate alpha based on intensity
                            alpha = int(255 * (shimmer_intensity - 0.65) * 10)  # More intense
                            # Brighter reflections for water world
                            shimmer_data[x, y] = (255, 255, 255, min(alpha, 100))  # Higher cap
                    else:
                        # Normal shimmer for archipelago
                        if shimmer_intensity > 0.75:  # Higher threshold for less shimmer
                            # Calculate alpha based on intensity
                            alpha = int(255 * (shimmer_intensity - 0.75) * 8)  # Less intense
                            # Normal reflections for archipelago
                            shimmer_data[x, y] = (255, 255, 255, min(alpha, 80))  # Lower cap

        # Apply the circle mask to the shimmer
        shimmer_alpha = shimmer.split()[3]
        shimmer_alpha = ImageChops.multiply(shimmer_alpha, circle_mask)
        shimmer.putalpha(shimmer_alpha)

        # Composite the shimmer over the result
        result = Image.alpha_composite(result, shimmer)

        return result
