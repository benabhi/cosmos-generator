"""
Abstract base class for all planet types.
"""
from typing import Dict, Any, Optional, Tuple, List
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
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
        super().__init__(seed=seed, size=size, **kwargs)

        # Default lighting parameters
        self.light_angle = kwargs.get("light_angle", 45.0)
        self.light_intensity = kwargs.get("light_intensity", 1.0)
        self.light_falloff = kwargs.get("light_falloff", 0.6)

        # Feature flags
        self.has_rings = kwargs.get("rings", False)
        self.has_atmosphere = kwargs.get("atmosphere", False)
        self.atmosphere_intensity = kwargs.get("atmosphere_intensity", 0.5)
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

        # Apply atmosphere if enabled
        if self.has_atmosphere:
            result = self._apply_atmosphere(result)

        # Apply clouds if enabled
        if self.has_clouds:
            result = self._apply_clouds(result)

        # Apply rings if enabled
        if self.has_rings:
            result = self._apply_rings(result)

        return result

    def _apply_atmosphere(self, base_image: Image.Image) -> Image.Image:
        """
        Apply atmospheric glow to the planet.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with atmosphere
        """
        # Get atmosphere color for this planet type
        atmosphere_color = self.color_palette.get_atmosphere_color(self.PLANET_TYPE)

        # Create a larger circle for the atmosphere
        atmosphere_size = int(self.size * (1.0 + 0.1 * self.atmosphere_intensity))
        atmosphere = Image.new("RGBA", (atmosphere_size, atmosphere_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(atmosphere)

        # Draw the atmosphere circle
        draw.ellipse((0, 0, atmosphere_size-1, atmosphere_size-1), fill=atmosphere_color)

        # Blur the atmosphere
        blur_radius = int(self.size * 0.05 * self.atmosphere_intensity)
        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))

        # Create a new image for the result
        result = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))

        # Paste the atmosphere centered on the result
        offset = (self.size - atmosphere_size) // 2
        result.paste(atmosphere, (offset, offset), atmosphere)

        # Paste the planet on top
        result.paste(base_image, (0, 0), base_image)

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
        Apply ring system to the planet using the minimal ring implementation algorithm.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with rings
        """
        # Get ring color for this planet type
        ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)

        # Create a larger image to accommodate the rings
        ring_width_factor = 2.5  # Rings extend this much beyond planet radius
        canvas_size = int(self.size * ring_width_factor)
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate planet position and dimensions
        center_x, center_y = canvas_size // 2, canvas_size // 2
        planet_radius = self.size // 2
        planet_offset = (canvas_size - self.size) // 2

        # Calculate ring dimensions (ellipse)
        # The outer radius should be significantly larger than the planet
        outer_rx = int(planet_radius * 2.0)  # Horizontal radius (2x planet radius)

        # The vertical radius should be smaller to create the elliptical appearance
        outer_ry = int(planet_radius * 0.4)  # Vertical radius (40% of planet radius)

        # Inner radius should be just outside the planet
        inner_rx = int(planet_radius * 1.2)  # 20% larger than planet radius
        inner_ry = int(outer_ry * (inner_rx / outer_rx))  # Maintain aspect ratio

        # Step 1: Create the ring layer (ellipse with hole)
        # ------------------------------------------------
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

        # Step 2: Create the planet layer
        # ------------------------------
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
             center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Step 3: Create the masks for different parts of the rings
        # -------------------------------------------------------

        # External arcs: difference between the ring and the planet
        ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

        # Create a mask for the front half (only the bottom half of the image)
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Intersection between the ring and the planet
        ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

        # The front band is only the front half of the intersection
        ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

        # Step 4: Apply colors and lighting
        # -------------------------------

        # Apply lighting to the ring color based on light angle
        shadow_factor = 0.7  # Darkness of the shadow
        r, g, b, a = ring_color

        # Slightly darker color for the arcs (parts behind the planet)
        arcs_color = (int(r * shadow_factor), int(g * shadow_factor), int(b * shadow_factor), a)

        # Create the colored ring arcs
        ring_arcs_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        ring_arcs_colored.paste(arcs_color, mask=ring_arcs)

        # Create the colored front band
        ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        ring_front_colored.paste(ring_color, mask=ring_front)

        # Step 5: Composite the final image
        # -------------------------------

        # Composite in the correct Z-buffer order:
        # 1. Ring arcs (behind the planet)
        result.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)

        # 2. Planet
        result.paste(base_image, (planet_offset, planet_offset), base_image)

        # 3. Front band (in front of the planet)
        result.paste(ring_front_colored, (0, 0), ring_front_colored)

        return result
