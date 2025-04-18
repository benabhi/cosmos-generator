"""
Abstract base class for all planet types.

Esta clase proporciona la estructura base para todos los tipos de planetas,
incluye la lógica para generar planetas con características como atmósfera,
nubes y anillos. También maneja la iluminación y el renderizado final.

Los planetas generados pueden tener un tamaño fijo de 512x512 píxeles,
pero cuando tienen anillos, se genera un canvas más grande (3x el tamaño)
para acomodar los anillos. Cuando tienen atmósfera, se ajusta el tamaño
del planeta para que la atmósfera quepa en el tamaño original.
"""
from typing import Optional
import os
import time
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from cosmos_generator.utils.logger import logger

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
from cosmos_generator.features.rings import Rings
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.utils import image_utils


class AbstractPlanet(AbstractCelestialBody):
    """
    Base class for all planet types with common generation flow.

    Esta clase implementa el flujo de generación común para todos los planetas:
    1. Generar la textura base del planeta
    2. Aplicar iluminación a la textura
    3. Aplicar características adicionales (nubes, atmósfera, anillos)

    Las clases derivadas deben implementar el método generate_texture() para
    crear la textura específica de cada tipo de planeta.
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
        has_rings = kwargs.get("rings", False)

        # Create a params dictionary to store additional parameters
        self.params = {"original_size": original_size}

        # No need to adjust size for atmosphere anymore, as we handle it in _apply_atmosphere
        super().__init__(seed=seed, size=size, **kwargs)

        # Default lighting parameters
        self.light_angle = kwargs.get("light_angle", 45.0)
        self.light_intensity = kwargs.get("light_intensity", 1.0)
        self.light_falloff = kwargs.get("light_falloff", 0.6)

        # Feature flags
        self.has_rings = has_rings
        self.has_atmosphere = has_atmosphere
        self.has_clouds = kwargs.get("clouds", False)

        # Initialize cloud system
        cloud_coverage = kwargs.get("cloud_coverage", 0.5)
        self.clouds = Clouds(
            seed=self.seed,
            coverage=cloud_coverage,
            enabled=self.has_clouds,
            size=self.size
        )
        # Set the light angle for the clouds to match the planet
        self.clouds.set_light_angle(self.light_angle)

        # Create a rings generator with the same seed
        self.rings_generator = Rings(seed=self.seed)

    def render(self) -> Image.Image:
        """
        Render the planet with the common generation flow.

        Returns:
            PIL Image of the planet
        """
        try:
            # Start logging generation process
            params = {
                "size": self.size,
                "light_intensity": self.light_intensity,
                "light_angle": self.light_angle,
                "has_rings": self.has_rings,
                "has_atmosphere": self.has_atmosphere,
                "has_clouds": self.has_clouds,
            }
            if self.has_clouds:
                params["cloud_coverage"] = self.clouds.coverage

            # Add any planet-specific parameters
            for key, value in self.params.items():
                if key not in params:
                    params[key] = value

            logger.start_generation(self.PLANET_TYPE, self.seed, params)

            # Generate base texture
            start_time = time.time()
            try:
                logger.debug(f"Generating texture for {self.PLANET_TYPE} planet (size: {self.size}x{self.size})", "planet")
                texture = self.generate_texture()

                # Apply spherical distortion to the terrain texture
                texture = image_utils.apply_spherical_distortion(texture, strength=0.15)

                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("generate_texture", duration_ms, f"Type: {self.PLANET_TYPE}, Size: {self.size}x{self.size}, Spherical distortion: 15%")
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("generate_texture", duration_ms, f"Error: {str(e)}")
                raise

            # Import here to avoid circular imports
            import config
            from cosmos_generator.utils.directory_utils import ensure_directory_exists

            # Save the base texture for debugging
            debug_dir = config.PLANETS_TERRAIN_TEXTURES_DIR
            ensure_directory_exists(debug_dir)
            texture_path = os.path.join(debug_dir, f"{self.seed}.png")
            texture.save(texture_path)
            logger.debug(f"Saved base texture to {texture_path}", "planet")

            # Apply lighting
            start_time = time.time()
            try:
                logger.debug(f"Applying lighting to {self.PLANET_TYPE} planet (angle: {self.light_angle}°, intensity: {self.light_intensity})", "planet")
                lit_texture = self.apply_lighting(texture)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("apply_lighting", duration_ms, f"Angle: {self.light_angle}°, Intensity: {self.light_intensity}, Falloff: {self.light_falloff}")
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("apply_lighting", duration_ms, f"Error: {str(e)}")
                raise

            # Apply features
            result = self.apply_features(lit_texture)

            return result

        except Exception as e:
            logger.error(f"Error rendering planet: {str(e)}", "planet", exc_info=True)
            logger.end_generation(False, error=str(e))
            raise

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
        start_time = time.time()
        try:
            result = base_image
            features_applied = []

            # The order of applying features is important:
            # 1. First apply atmosphere if enabled (before anything else)
            if self.has_atmosphere:
                logger.debug(f"Applying atmosphere to {self.PLANET_TYPE} planet", "planet")
                result = self._apply_atmosphere(result)
                features_applied.append("atmosphere")

            # 2. Then apply clouds if enabled
            if self.has_clouds:
                logger.debug(f"Applying clouds to {self.PLANET_TYPE} planet (coverage: {self.clouds.coverage:.2f})", "planet")
                result = self.clouds.apply_to_planet(result)
                features_applied.append("clouds")

            # 3. Finally apply rings if enabled
            if self.has_rings:
                logger.debug(f"Applying rings to {self.PLANET_TYPE} planet", "planet")
                result = self._apply_rings(result)
                features_applied.append("rings")

            # Log features applied
            if features_applied:
                features_str = ", ".join(features_applied)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("apply_features", duration_ms, f"Applied: {features_str}")
            else:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_step("apply_features", duration_ms, "No features applied")

            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_features", duration_ms, f"Error: {str(e)}")
            raise

    def _apply_atmosphere(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a simple atmospheric glow to the planet with a fine light line around the edge.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with atmosphere
        """
        start_time = time.time()
        try:
            # Ensure the planet image has an alpha channel
            if base_image.mode != "RGBA":
                base_image = base_image.convert("RGBA")

            # Get atmosphere color for this planet type
            atmosphere_color = self.color_palette.get_atmosphere_color(self.PLANET_TYPE)

            # Make atmosphere more visible by increasing opacity
            r, g, b, a = atmosphere_color
            atmosphere_color = (r, g, b, min(255, a * 2))  # Double the opacity, max 255

            # Get the size of the planet image
            size = base_image.width

            # Create a canvas for the atmosphere - much smaller padding for planets without rings
            if self.has_rings:
                # Very thin atmosphere for planets with rings to avoid translucent edge
                atmosphere_padding = int(size * 0.01)  # Only 1% padding for planets with rings
            else:
                atmosphere_padding = int(size * 0.02)  # 2% padding for planets without rings
            canvas_size = size + atmosphere_padding * 2
            result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

            # Calculate center and planet radius
            center = canvas_size // 2
            planet_radius = size // 2

            # Create the atmosphere layer
            atmosphere = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            atmosphere_draw = ImageDraw.Draw(atmosphere)

            # Draw the atmosphere as a larger circle
            atmosphere_radius = planet_radius + atmosphere_padding
            atmosphere_draw.ellipse(
                (center - atmosphere_radius, center - atmosphere_radius,
                 center + atmosphere_radius, center + atmosphere_radius),
                fill=atmosphere_color
            )

            # Apply blur for a nice glow effect - use smaller blur for sharper edge
            if self.has_rings:
                blur_radius = atmosphere_padding // 3
            else:
                # Almost no blur for planets without rings - just enough to smooth the edge
                blur_radius = max(1, atmosphere_padding // 10)  # Minimum blur of 1 pixel
            atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(blur_radius))

            # Paste the atmosphere onto the result
            result.paste(atmosphere, (0, 0), atmosphere)

            # Paste the planet in the center
            planet_pos = (center - planet_radius, center - planet_radius)
            result.paste(base_image, planet_pos, base_image)

            # Add a thin bright halo right at the edge of the planet for extra visibility
            # We'll use a different approach to create a cleaner, more consistent halo

            # Create a larger canvas for the halo to avoid edge artifacts
            halo_canvas_size = canvas_size + 10  # Add padding to avoid edge artifacts
            halo_center = halo_canvas_size // 2

            # Create two images: one for the inner circle and one for the outer circle
            inner_circle = Image.new("L", (halo_canvas_size, halo_canvas_size), 0)
            outer_circle = Image.new("L", (halo_canvas_size, halo_canvas_size), 0)

            # Create drawing objects
            inner_draw = ImageDraw.Draw(inner_circle)
            outer_draw = ImageDraw.Draw(outer_circle)

            # Set up the halo parameters
            # Make the inner radius slightly smaller to ensure it overlaps with the planet edge
            # This helps prevent gaps between the halo and the planet due to the spherical distortion
            inner_radius = planet_radius - 1  # Slightly smaller to ensure overlap
            outer_radius = planet_radius + 3  # Outer edge of halo (3px thick)

            # Draw filled circles (not outlines) for clean edges
            inner_draw.ellipse(
                (halo_center - inner_radius, halo_center - inner_radius,
                 halo_center + inner_radius, halo_center + inner_radius),
                fill=255
            )

            outer_draw.ellipse(
                (halo_center - outer_radius, halo_center - outer_radius,
                 halo_center + outer_radius, halo_center + outer_radius),
                fill=255
            )

            # Create the halo by subtracting the inner circle from the outer circle
            # This creates a perfect ring with clean edges
            halo_mask = ImageChops.subtract(outer_circle, inner_circle)

            # Apply a very small blur for anti-aliasing only
            # Just enough to smooth the edges without creating artifacts
            blur_amount = 0.3  # Minimal blur for clean edges
            halo_mask = halo_mask.filter(ImageFilter.GaussianBlur(blur_amount))

            # Create the colored halo with the mask
            halo = Image.new("RGBA", (halo_canvas_size, halo_canvas_size), (0, 0, 0, 0))
            halo_array = np.array(halo)
            mask_array = np.array(halo_mask)

            # Apply the color with the mask
            for y in range(halo_canvas_size):
                for x in range(halo_canvas_size):
                    if mask_array[y, x] > 0:
                        # Use the mask value as the alpha
                        alpha = mask_array[y, x]
                        halo_array[y, x] = [r, g, b, alpha]

            # Convert back to PIL Image
            halo = Image.fromarray(halo_array)

            # Crop the halo to match the canvas size
            crop_offset = (halo_canvas_size - canvas_size) // 2
            halo = halo.crop((crop_offset, crop_offset,
                             crop_offset + canvas_size,
                             crop_offset + canvas_size))

            # Composite the halo onto the result
            result = Image.alpha_composite(result, halo)

            duration_ms = (time.time() - start_time) * 1000
            # Log details about the atmosphere
            padding_percent = atmosphere_padding / planet_radius * 100
            blur_info = f"blur: {blur_radius}px"
            logger.log_step("apply_atmosphere", duration_ms, f"Padding: {padding_percent:.1f}%, {blur_info}")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_atmosphere", duration_ms, f"Error: {str(e)}")
            raise



    def _apply_rings(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a Saturn-like ring system with multiple concentric rings of varying widths and opacities.

        Args:
            base_image: Base planet image (may include atmosphere)

        Returns:
            Planet image with Saturn-like rings
        """
        start_time = time.time()
        try:
            # Get the ring color for this planet type
            ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)

            # IMPORTANT: Pass the original planet size to the rings generator
            # This ensures rings are based on the actual planet size, not the image with atmosphere
            original_planet_size = self.size

            # Apply rings using the Rings class
            result = self.rings_generator.apply_rings(
                planet_image=base_image,
                planet_type=self.PLANET_TYPE,
                color=ring_color,
                original_planet_size=original_planet_size  # Pass the original planet size
            )

            # Get ring complexity and count from the rings generator
            ring_complexity = self.rng.randint(1, 3)  # Same logic as in Rings class
            ring_count = len(self.rings_generator.last_ring_definitions) if hasattr(self.rings_generator, 'last_ring_definitions') else 0
            ring_width_factor = 3.0  # Standard factor used in Rings class

            duration_ms = (time.time() - start_time) * 1000
            # Log details about the rings
            logger.log_step("apply_rings", duration_ms, f"Complexity: {ring_complexity}, Rings: {ring_count}, Factor: {ring_width_factor}")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_rings", duration_ms, f"Error: {str(e)}")
            raise