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
        Apply ring system to the planet.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with rings
        """
        # Get ring color for this planet type
        ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)
        
        # Create a larger image to accommodate the rings
        ring_width_factor = 2.0  # Rings extend this much beyond planet radius
        ring_size = int(self.size * ring_width_factor)
        result = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        
        # Calculate planet position in the larger image
        planet_offset = (ring_size - self.size) // 2
        
        # Create ring template
        ring_inner_radius = int(self.size * 0.55)  # Just outside the planet
        ring_outer_radius = int(self.size * ring_width_factor * 0.5)  # Extend to edge
        ring_template = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ring_template)
        
        # Draw the outer ellipse (full ring)
        draw.ellipse((0, ring_size//4, ring_size-1, ring_size*3//4), fill=ring_color)
        
        # Draw the inner ellipse (hole) with transparent color
        inner_left = (ring_size - ring_inner_radius*2) // 2
        inner_top = (ring_size - ring_inner_radius) // 2
        inner_right = inner_left + ring_inner_radius*2
        inner_bottom = inner_top + ring_inner_radius
        draw.ellipse((inner_left, inner_top, inner_right, inner_bottom), fill=(0, 0, 0, 0))
        
        # Create a mask for the part of the rings that should be behind the planet
        behind_mask = Image.new("L", (ring_size, ring_size), 0)
        draw = ImageDraw.Draw(behind_mask)
        draw.ellipse((0, ring_size//4, ring_size-1, ring_size*3//4), fill=255)
        
        # Create a mask for the planet
        planet_mask = Image.new("L", (ring_size, ring_size), 0)
        draw = ImageDraw.Draw(planet_mask)
        draw.ellipse((planet_offset, planet_offset, planet_offset+self.size-1, planet_offset+self.size-1), fill=255)
        
        # Subtract planet mask from behind mask to get only the parts of rings behind the planet
        behind_mask = ImageChops.subtract(behind_mask, planet_mask)
        
        # Create a mask for the parts of rings in front of the planet
        front_mask = ImageChops.subtract(ImageChops.invert(behind_mask), planet_mask)
        
        # Apply lighting to rings
        # Simplistic lighting: just darken the rings based on light angle
        darkened_rings = image_utils.adjust_brightness(ring_template, 0.7)
        
        # Composite the images in the correct order:
        # 1. Rings behind planet
        result.paste(darkened_rings, (0, 0), behind_mask)
        
        # 2. Planet
        result.paste(base_image, (planet_offset, planet_offset), base_image)
        
        # 3. Rings in front of planet
        result.paste(ring_template, (0, 0), front_mask)
        
        return result
