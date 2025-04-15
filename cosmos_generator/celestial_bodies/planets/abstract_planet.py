"""
Abstract base class for all planet types.
"""
from typing import Dict, Any, Optional, Tuple, List
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.utils import image_utils, lighting_utils


class AbstractPlanet(AbstractCelestialBody):
    """
    Base class for all planet types with common generation flow.
    """

    # Planet type identifier
    PLANET_TYPE = "Abstract"

    def __init__(self, seed: Optional[int] = None, size: int = 512, **kwargs):
        """
        Initialize a planet with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            **kwargs: Additional parameters for customization
        """
        # Store the original requested size for later use
        original_size = size

        # Feature flags (need to check these before adjusting size)
        has_atmosphere = kwargs.get("atmosphere", False)
        atmosphere_intensity = kwargs.get("atmosphere_intensity", 0.5)
        has_rings = kwargs.get("rings", False)

        # Create a params dictionary to store additional parameters
        self.params = {"original_size": original_size}

        # Adjust size if the planet has atmosphere to ensure it fits in the viewport
        if has_atmosphere:
            # Reduce size by a small amount to accommodate the atmosphere
            atmosphere_padding = int(size * 0.05 * atmosphere_intensity)  # 2-5% padding
            adjusted_size = size - atmosphere_padding * 2
            super().__init__(seed=seed, size=adjusted_size, **kwargs)
        else:
            super().__init__(seed=seed, size=size, **kwargs)

        # Default lighting parameters
        self.light_angle = kwargs.get("light_angle", 45.0)
        self.light_intensity = kwargs.get("light_intensity", 1.0)
        self.light_falloff = kwargs.get("light_falloff", 0.6)

        # Feature flags
        self.has_rings = has_rings
        self.has_atmosphere = has_atmosphere
        self.atmosphere_intensity = atmosphere_intensity
        self.has_clouds = kwargs.get("clouds", False)
        self.cloud_coverage = kwargs.get("cloud_coverage", 0.5)

    def render(self) -> Image.Image:
        """
        Render the planet with the common generation flow.

        Returns:
            PIL Image of the planet
        """
        # Generate base texture
        texture = self.generate_texture()

        # Apply lighting
        lit_texture = self.apply_lighting(texture)

        # Apply features
        result = self.apply_features(lit_texture)

        return result

    def generate_texture(self) -> Image.Image:
        """
        Generate the base texture for the planet.

        Returns:
            Base texture image
        """
        raise NotImplementedError("Subclasses must implement generate_texture()")

    def apply_lighting(self, texture: Image.Image) -> Image.Image:
        """
        Apply lighting to the planet texture.

        Args:
            texture: Base texture image

        Returns:
            Texture with lighting applied
        """
        return self.texture_gen.apply_lighting(
            texture,
            light_angle=self.light_angle,
            light_intensity=self.light_intensity,
            falloff=self.light_falloff
        )

    def apply_features(self, base_image: Image.Image) -> Image.Image:
        """
        Apply additional features to the planet.

        Args:
            base_image: Base planet image with lighting

        Returns:
            Planet image with features applied
        """
        result = base_image

        # Apply clouds if enabled
        if self.has_clouds:
            result = self._apply_clouds(result)

        # The order of applying features is important:
        # 1. First apply rings if enabled (they need the base planet without atmosphere)
        planet_with_rings = None
        if self.has_rings:
            planet_with_rings = self._apply_rings(result)

        # 2. Then apply atmosphere if enabled
        if self.has_atmosphere:
            # If we have rings, apply atmosphere to the base planet first
            atmosphere_result = self._apply_atmosphere(result)

            # If we have rings, composite the atmosphere with the rings
            if planet_with_rings is not None:
                # Get the size of the rings image
                rings_size = planet_with_rings.width

                # Create a new image with the same size as the rings
                final_result = Image.new("RGBA", (rings_size, rings_size), (0, 0, 0, 0))

                # Calculate the offset to center the atmosphere in the rings image
                offset = (rings_size - atmosphere_result.width) // 2

                # Paste the atmosphere in the center
                final_result.paste(atmosphere_result, (offset, offset), atmosphere_result)

                # Composite with the rings
                result = Image.alpha_composite(final_result, planet_with_rings)
            else:
                # No rings, just use the atmosphere result
                result = atmosphere_result
        elif self.has_rings:
            # We have rings but no atmosphere
            result = planet_with_rings

        return result

    def _apply_atmosphere(self, base_image: Image.Image) -> Image.Image:
        """
        Apply atmospheric glow to the planet with a fine light line around the edge.
        The atmosphere will be darker in shadowed areas and brighter in lit areas.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with atmosphere
        """
        # Get atmosphere color for this planet type
        atmosphere_color = self.color_palette.get_atmosphere_color(self.PLANET_TYPE)

        # Use the atmosphere feature with the light angle
        atmosphere_feature = Atmosphere(seed=self.seed)
        result = atmosphere_feature.apply_atmosphere(
            planet_image=base_image,
            planet_type=self.PLANET_TYPE,
            intensity=self.atmosphere_intensity,
            color=atmosphere_color,
            light_angle=self.light_angle
        )

        return result

    def _apply_clouds(self, base_image: Image.Image) -> Image.Image:
        """
        Apply cloud layer to the planet.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with clouds
        """
        # Generate cloud noise
        cloud_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.4),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.5, 2.0, 3.0)
            )
        )

        # Threshold the noise to create cloud patterns
        cloud_threshold = 1.0 - self.cloud_coverage
        cloud_mask = Image.new("L", (self.size, self.size), 0)
        cloud_data = cloud_mask.load()

        for y in range(self.size):
            for x in range(self.size):
                if cloud_noise[y, x] > cloud_threshold:
                    # Scale alpha based on how far above threshold
                    alpha = int(255 * (cloud_noise[y, x] - cloud_threshold) / (1.0 - cloud_threshold))
                    cloud_data[x, y] = alpha

        # Apply circular mask to the clouds
        circle_mask = image_utils.create_circle_mask(self.size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)

        # Create cloud layer
        cloud_color = (255, 255, 255, 180)  # Semi-transparent white
        clouds = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, self.size-1, self.size-1), fill=cloud_color)

        # Apply the cloud mask
        clouds.putalpha(cloud_mask)

        # Apply lighting to clouds
        lit_clouds = lighting_utils.apply_directional_light(
            clouds,
            lighting_utils.calculate_normal_map(cloud_noise, 2.0),
            light_direction=(
                -math.cos(math.radians(self.light_angle)),
                -math.sin(math.radians(self.light_angle)),
                1.0
            ),
            ambient=0.3,
            diffuse=0.7,
            specular=0.0
        )

        # Composite clouds over the planet
        result = Image.alpha_composite(base_image, lit_clouds)

        return result

    def _apply_rings(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a Saturn-like ring system with multiple concentric rings of varying widths and opacities.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with Saturn-like rings
        """
        # Get base ring color for this planet type
        base_ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)

        # Create a larger image to accommodate the rings
        ring_width_factor = 2.5  # Rings extend this much beyond planet radius
        canvas_size = int(self.size * ring_width_factor)
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate planet position and dimensions
        center_x, center_y = canvas_size // 2, canvas_size // 2
        planet_radius = self.size // 2
        planet_offset = (canvas_size - self.size) // 2

        # Calculate vertical compression factor
        vertical_factor = 0.4  # Vertical radius as a fraction of horizontal radius

        # Create a random number generator with the same seed for consistency
        rng = random.Random(self.seed)

        # Determine the ring system complexity (1-3)
        # 1: Minimal rings (few bands)
        # 2: Medium complexity (moderate number of bands)
        # 3: Full Saturn-like complexity (many bands)
        ring_complexity = rng.randint(1, 3)

        # Create the planet layer (for masking)
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
             center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Create a mask for the front half (only the bottom half of the image)
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Define the Saturn-like ring system with multiple rings and varying widths/opacities
        # Base ring definitions with maximum opacity
        # We'll select from these based on the complexity level
        all_possible_rings = [
            # (inner_radius_factor, outer_radius_factor, opacity, brightness)
            # D Ring (innermost, thin and faint)
            (1.20, 1.23, 0.9, 0.7),
            # C Ring (darker, brownish)
            (1.24, 1.35, 0.98, 0.75),
            # B Ring Inner (bright and dense)
            (1.36, 1.45, 1.0, 0.95),
            # B Ring Middle (brightest section)
            (1.46, 1.55, 1.0, 1.0),
            # B Ring Outer (bright with some structure)
            (1.56, 1.65, 1.0, 0.9),
            # Cassini Division (prominent gap)
            (1.66, 1.70, 0.8, 0.6),
            # A Ring Inner (bright)
            (1.71, 1.85, 0.98, 0.9),
            # Encke Gap (thin dark gap)
            (1.86, 1.87, 0.7, 0.5),
            # A Ring Middle
            (1.88, 1.95, 0.98, 0.85),
            # Keeler Gap (very thin)
            (1.96, 1.965, 0.7, 0.4),
            # A Ring Outer (slightly fainter)
            (1.97, 2.05, 0.95, 0.8),
            # F Ring (thin, isolated outer ring)
            (2.10, 2.12, 0.9, 0.7),
            # G Ring (very faint, wide)
            (2.15, 2.20, 0.85, 0.5)
        ]

        # Select rings based on complexity level
        base_rings_selected = []

        if ring_complexity == 1:  # Minimal rings
            # Select only 3-4 main rings
            main_rings = [
                all_possible_rings[1],  # C Ring
                all_possible_rings[3],  # B Ring Middle
                all_possible_rings[6],  # A Ring Inner
            ]
            # Maybe add one more
            if rng.random() > 0.5:
                main_rings.append(all_possible_rings[10])  # A Ring Outer

            base_rings_selected = main_rings

        elif ring_complexity == 2:  # Medium complexity
            # Select 6-8 rings
            main_rings = [
                all_possible_rings[1],  # C Ring
                all_possible_rings[2],  # B Ring Inner
                all_possible_rings[3],  # B Ring Middle
                all_possible_rings[4],  # B Ring Outer
                all_possible_rings[6],  # A Ring Inner
                all_possible_rings[8],  # A Ring Middle
            ]
            # Maybe add 1-2 more
            if rng.random() > 0.3:
                main_rings.append(all_possible_rings[10])  # A Ring Outer
            if rng.random() > 0.5:
                main_rings.append(all_possible_rings[12])  # F Ring

            base_rings_selected = main_rings

        else:  # Full complexity (all rings)
            base_rings_selected = all_possible_rings

        # Add some random thin rings
        extra_rings = []

        # Determine how many additional thin rings to add based on complexity
        if ring_complexity == 1:
            num_extra_rings = rng.randint(0, 2)  # Few or no additional rings
        elif ring_complexity == 2:
            num_extra_rings = rng.randint(1, 3)  # Some additional rings
        else:
            num_extra_rings = rng.randint(2, 5)  # Many additional rings

        for _ in range(num_extra_rings):
            # Random position between 1.25 and 2.1
            pos = 1.25 + 0.85 * rng.random()
            # Very thin ring
            thickness = 0.005 + 0.015 * rng.random()
            # Random opacity (very high values for solid look)
            opacity = 0.8 + 0.2 * rng.random()
            # Random brightness
            brightness = 0.8 + 0.2 * rng.random()

            extra_rings.append((pos, pos + thickness, opacity, brightness))

        # Combine and sort all rings
        ring_definitions = []

        # Add base rings with variation
        for inner, outer, opacity, brightness in base_rings_selected:
            # Vary the opacity and brightness for more realistic appearance
            # Use minimal variation for opacity to keep rings very solid
            varied_opacity = min(1.0, max(0.7, opacity * (0.9 + 0.15 * rng.random())))
            varied_brightness = min(1.0, max(0.7, brightness * (0.95 + 0.1 * rng.random())))

            ring_definitions.append((inner, outer, varied_opacity, varied_brightness))

        # Add extra rings
        ring_definitions.extend(extra_rings)

        # Sort by inner radius
        ring_definitions.sort(key=lambda x: x[0])

        # Note: We already created the random number generator above

        # Process each ring
        for i, (inner_factor, outer_factor, opacity, brightness) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color slightly for each ring
            r, g, b, a = base_ring_color
            color_variation = 0.1  # Amount to vary the color

            # Apply brightness, opacity and slight color variation
            ring_color = (
                max(0, min(255, int(r * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(g * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(b * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(a * opacity)))
            )

            # Create the ring layer (ellipse with hole)
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Draw outer ellipse
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry, center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Draw inner ellipse (hole)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry, center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # External arcs: difference between the ring and the planet
            ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

            # Intersection between the ring and the planet
            ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

            # The front band is only the front half of the intersection
            ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

            # Apply lighting to the ring color based on light angle
            shadow_factor = 0.6  # Darkness of the shadow

            # Slightly darker color for the arcs (parts behind the planet)
            arcs_color = (
                int(ring_color[0] * shadow_factor),
                int(ring_color[1] * shadow_factor),
                int(ring_color[2] * shadow_factor),
                ring_color[3]
            )

            # Create the colored ring arcs
            ring_arcs_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_arcs_colored.paste(arcs_color, mask=ring_arcs)

            # Create the colored front band
            ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_front_colored.paste(ring_color, mask=ring_front)

            # Composite the rings in the correct Z-buffer order:
            # 1. Ring arcs (behind the planet)
            result.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)

            # Note: We'll add the front bands after the planet is added

        # Add the planet on top of the rings that are behind it
        result.paste(base_image, (planet_offset, planet_offset), base_image)

        # Now add the front bands (parts of rings that pass in front of the planet)
        for i, (inner_factor, outer_factor, opacity, brightness) in enumerate(ring_definitions):
            # Calculate this ring's dimensions
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)  # Apply vertical compression

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)  # Apply vertical compression

            # Vary the color slightly for each ring
            r, g, b, a = base_ring_color
            color_variation = 0.1  # Amount to vary the color

            # Apply brightness, opacity and slight color variation
            ring_color = (
                max(0, min(255, int(r * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(g * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(b * brightness * (1 + (rng.random() - 0.5) * color_variation)))),
                max(0, min(255, int(a * opacity)))
            )

            # Create the ring layer (ellipse with hole)
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Draw outer ellipse
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry, center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Draw inner ellipse (hole)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry, center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # Intersection between the ring and the planet
            ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

            # The front band is only the front half of the intersection
            ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

            # Create the colored front band
            ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_front_colored.paste(ring_color, mask=ring_front)

            # Add the front band on top of the planet
            result.paste(ring_front_colored, (0, 0), ring_front_colored)

        # Resize the result to match the original requested size
        # This ensures that the image with rings respects the viewport size
        original_size = self.params.get("original_size", self.size)
        if canvas_size != original_size:
            result = result.resize((original_size, original_size), Image.LANCZOS)

        return result
