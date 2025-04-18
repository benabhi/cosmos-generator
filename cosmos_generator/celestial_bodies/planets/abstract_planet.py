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
import math
import os
import time
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from cosmos_generator.utils.logger import logger

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
from cosmos_generator.features.rings import Rings
from cosmos_generator.utils import image_utils, lighting_utils


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
        self.cloud_coverage = kwargs.get("cloud_coverage", 0.5)

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
            if self.has_clouds and hasattr(self, "cloud_coverage"):
                params["cloud_coverage"] = self.cloud_coverage

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
                coverage = getattr(self, "cloud_coverage", 0.5)
                logger.debug(f"Applying clouds to {self.PLANET_TYPE} planet (coverage: {coverage:.2f})", "planet")
                result = self._apply_clouds(result)
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
                # Muy poca atmósfera para planetas con anillos para evitar el borde translúcido
                atmosphere_padding = int(size * 0.01)  # Solo 1% de padding para planetas con anillos
            else:
                atmosphere_padding = int(size * 0.02)  # 2% padding para planetas sin anillos
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
            halo = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            halo_draw = ImageDraw.Draw(halo)

            # Draw a thin ring at the exact edge of the planet
            halo_radius = planet_radius + 1  # Just 1 pixel larger than the planet

            # If the planet will have rings, make the halo more visible
            if self.has_rings:
                halo_color = (r, g, b, 255)  # Full opacity for the halo
                halo_width = 3  # Slightly thicker halo for planets with rings

                # Add a second, outer halo for extra visibility with rings
                outer_halo_radius = planet_radius + 3
                halo_draw.ellipse(
                    (center - outer_halo_radius, center - outer_halo_radius,
                     center + outer_halo_radius, center + outer_halo_radius),
                    outline=halo_color, width=1
                )
            else:
                halo_color = (r, g, b, 255)  # Full opacity for the halo
                halo_width = 3  # Increased width for planets without rings (was 2)

                # Add a second, outer halo for planets without rings to make it more visible
                outer_halo_radius = planet_radius + 2
                halo_draw.ellipse(
                    (center - outer_halo_radius, center - outer_halo_radius,
                     center + outer_halo_radius, center + outer_halo_radius),
                    outline=halo_color, width=1
                )

            # Draw the halo as a thin ring
            halo_draw.ellipse(
                (center - halo_radius, center - halo_radius,
                 center + halo_radius, center + halo_radius),
                outline=halo_color, width=halo_width
            )

            # Apply a very small blur to soften the halo slightly
            # For planets with rings, use less blur to keep the halo more defined
            # For planets without rings, use even less blur to make the halo more visible
            blur_amount = 0.5 if self.has_rings else 0.3  # Reduced blur for planets without rings
            halo = halo.filter(ImageFilter.GaussianBlur(blur_amount))

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

    def _enhance_cloud_contrast(self, cloud_image: Image.Image, light_direction: tuple) -> Image.Image:
        """
        Enhance the contrast of clouds, particularly in illuminated areas.

        Args:
            cloud_image: Cloud image with lighting applied
            light_direction: Light direction vector (x, y, z)

        Returns:
            Cloud image with enhanced contrast in illuminated areas
        """
        # Convert to numpy array for processing
        img_array = np.array(cloud_image)
        size = img_array.shape[0]
        center = size // 2

        # Extract light direction components
        light_x, light_y = light_direction[0], light_direction[1]

        # Create a contrast enhancement mask based on light direction
        # We'll enhance contrast more on the illuminated side
        result_array = img_array.copy()

        # Process each pixel
        for y in range(size):
            for x in range(size):
                # Only process pixels with some opacity
                if img_array[y, x, 3] > 0:
                    # Calculate position relative to center
                    rel_x = (x - center) / center
                    rel_y = (y - center) / center

                    # Calculate dot product with light direction (2D projection)
                    dot_product = rel_x * light_x + rel_y * light_y

                    # Convert to a 0-1 range where 1 is fully illuminated
                    illumination = 1.0 - (dot_product + 1.0) / 2.0

                    # Apply stronger contrast enhancement in illuminated areas
                    if illumination > 0.5:  # More illuminated side
                        # Calculate contrast factor - stronger in more illuminated areas
                        contrast_factor = 1.0 + (illumination - 0.5) * 0.6  # Up to 30% increase

                        # Apply contrast enhancement to RGB channels
                        for i in range(3):
                            # Apply contrast enhancement
                            # Formula: new_value = 128 + (old_value - 128) * contrast_factor
                            pixel_value = float(img_array[y, x, i])
                            adjusted_value = 128 + (pixel_value - 128) * contrast_factor
                            result_array[y, x, i] = np.clip(adjusted_value, 0, 255).astype(np.uint8)

        # Convert back to PIL Image
        return Image.fromarray(result_array)

    def _create_light_based_opacity_mask(self, cloud_mask: Image.Image, light_direction: tuple) -> Image.Image:
        """
        Create an opacity adjustment mask based on light direction to make clouds more visible in illuminated areas.
        This implementation creates a completely new mask to avoid any artifacts.

        Args:
            cloud_mask: Original cloud mask
            light_direction: Light direction vector (x, y, z)

        Returns:
            Adjusted cloud mask with increased opacity in illuminated areas
        """
        # Get the size of the mask
        size = cloud_mask.width
        center = size // 2

        # Extract light direction components
        light_x, light_y = light_direction[0], light_direction[1]

        # Create a completely new illumination gradient
        # This is a simple hemisphere lighting model
        gradient = Image.new('L', (size, size), 0)
        gradient_draw = ImageDraw.Draw(gradient)

        # Draw a radial gradient from the light direction
        # The center of the gradient is offset in the direction opposite to the light
        # This creates a smooth illumination effect with the brightest part opposite to the light source
        light_center_x = int(center - light_x * center * 0.7)  # Offset center in direction opposite to light
        light_center_y = int(center - light_y * center * 0.7)

        # Draw concentric circles with decreasing brightness from the light center
        max_radius = int(size * 0.8)  # Slightly larger than the planet radius
        for r in range(max_radius, 0, -1):
            # Calculate brightness based on distance from light center
            # Closer to light center = brighter
            brightness = int(255 * (1.0 - r / max_radius))
            gradient_draw.ellipse(
                (light_center_x - r, light_center_y - r, light_center_x + r, light_center_y + r),
                fill=brightness
            )

        # Apply a circular mask to the gradient to match the planet shape
        circle_mask = image_utils.create_circle_mask(size)
        gradient = ImageChops.multiply(gradient, circle_mask)

        # Apply a blur to smooth the gradient
        gradient = gradient.filter(ImageFilter.GaussianBlur(size // 20))

        # We'll create the final adjusted mask by combining the original mask with the gradient

        # Convert to numpy arrays for faster processing
        mask_array = np.array(cloud_mask)
        gradient_array = np.array(gradient)
        adjusted_array = np.zeros_like(mask_array)

        # Apply the gradient to the mask
        for y in range(size):
            for x in range(size):
                if mask_array[y, x] > 0:  # Only process cloud pixels
                    # Get the illumination factor from the gradient (0-255)
                    illumination = gradient_array[y, x] / 255.0

                    # Apply a curve to enhance the effect
                    # Brighter areas get more boost
                    opacity_boost = 1.0 + illumination * 0.5  # Up to 50% boost in fully lit areas

                    # Apply the boost to the original opacity
                    new_opacity = min(255, int(mask_array[y, x] * opacity_boost))
                    adjusted_array[y, x] = new_opacity

        # Convert back to PIL Image
        return Image.fromarray(adjusted_array)

    def _apply_clouds(self, base_image: Image.Image) -> Image.Image:
        """
        Apply cloud layer to the planet.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with clouds
        """
        start_time = time.time()
        try:
            # Ensure the planet image has an alpha channel
            if base_image.mode != "RGBA":
                base_image = base_image.convert("RGBA")

            # Get the size of the planet image (may include atmosphere)
            size = base_image.width

            # SOFT STYLIZED CLOUD GENERATION
            # Base cloud layer - larger, softer cloud formations with less detail
            base_cloud_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                lambda x, y: self.noise_gen.domain_warp(
                    x, y,
                    # Use a gentler warp with lower frequency for softer shapes
                    lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.15, 0.2),
                    # Fewer octaves (3 instead of 4) for less detail and smoother appearance
                    lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 3, 0.5, 2.0, 1.8)
                )
            )

            # Detail layer - very subtle detail to avoid graininess
            detail_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                # Use only 2 octaves for minimal detail
                lambda x, y: self.noise_gen.fractal_simplex(x, y, 2, 0.4, 2.0, 1.5)
            )

            # Edge definition layer - softer edges for a more painterly look
            edge_noise = self.noise_gen.generate_noise_map(
                self.size, self.size,
                # Use a gentler ridge function with fewer octaves
                lambda x, y: self.noise_gen.ridged_simplex(x, y, 2, 0.6, 2.0, 2.0)
            )

            # Combine the noise layers to create balanced cloud formations
            # Create a new array for the combined noise
            combined_noise = np.zeros((self.size, self.size), dtype=np.float32)

            for y in range(self.size):
                for x in range(self.size):
                    # Base shape (70%) - dominant soft cloud formations
                    base = base_cloud_noise[y, x]
                    # Add minimal detail (15%) - just enough texture to avoid flatness
                    detail = detail_noise[y, x]
                    # Add soft edge definition (15%) - gentle cloud boundaries
                    edge = edge_noise[y, x]

                    # Combine with weights favoring the base layer for softer appearance
                    combined = base * 0.7 + detail * 0.15 + edge * 0.15

                    # Apply a gentler curve for softer transitions
                    if combined > 0.35 and combined < 0.65:
                        # Wider, more gradual transition zone
                        factor = (combined - 0.35) / 0.3  # 0 to 1 in the 0.35-0.65 range
                        # Smaller adjustment for more subtle edges
                        combined = 0.35 + factor * 0.3  # Gentler transition

                    # Add very minimal variation to maintain smoothness
                    variation = (self.rng.random() - 0.5) * 0.02  # Smaller random variation (-0.01 to 0.01)
                    combined = max(0.0, min(1.0, combined + variation))  # Keep within 0-1 range

                    # Store the result
                    combined_noise[y, x] = combined

            # Use the combined noise for cloud generation
            cloud_noise = combined_noise

            # Create the cloud mask
            cloud_mask = Image.new("L", (self.size, self.size), 0)
            cloud_data = cloud_mask.load()

            # Adjust threshold for cloud coverage with a gentler curve
            # Lower threshold = more clouds
            # Use a more aggressive threshold to increase cloud visibility
            cloud_threshold = 0.45 - (self.cloud_coverage * 0.45)  # More aggressive adjustment for higher visibility

            # Fill the cloud mask with a balanced approach for cloud-like appearance
            for y in range(self.size):
                for x in range(self.size):
                    # Get the noise value at this pixel
                    value = cloud_noise[y, x]

                    # Use a wider, more gradual transition zone for softer cloud edges
                    if value > cloud_threshold - 0.15:  # Wider transition zone (0.15 instead of 0.08)
                        if value < cloud_threshold:  # Edge zone
                            # More gradual transition for softer edges
                            edge_factor = (value - (cloud_threshold - 0.15)) / 0.15  # 0 to 1 over wider range
                            # Increased minimum opacity for more visible edges
                            alpha = int(80 * edge_factor)  # 0 to 80 opacity for edges (increased from 0-60)
                        else:  # Main cloud zone
                            # Calculate normalized distance from threshold
                            normalized = (value - cloud_threshold) / (1.0 - cloud_threshold)

                            # Simplified two-zone curve for smoother appearance
                            if normalized < 0.4:  # Outer and mid-cloud zone combined
                                # More gradual transition throughout the cloud
                                # Start at 80 (matching edge transition) and go up to 220
                                alpha = int(80 + normalized * 350)  # 80-220 range for most of the cloud
                            else:  # Dense cloud center
                                # Higher opacity for more visible cloud centers
                                alpha = int(220 + (normalized - 0.4) * 87.5)  # 220-255 range for centers

                        # Apply a smaller random variation for smoother appearance
                        # Just enough to avoid perfectly flat areas
                        variation = int((self.rng.random() - 0.5) * 8)  # Reduced variation (-4 to +4)
                        alpha = max(0, min(255, alpha + variation))  # Keep within 0-255 range
                        cloud_data[x, y] = alpha

            # Apply circular mask to the clouds
            circle_mask = image_utils.create_circle_mask(self.size)
            cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)

            # Create softer off-white clouds for a more stylized appearance
            # Pure white can look too harsh - a gentle cream tint looks more natural and stylized
            cloud_color = (255, 250, 245, 255)  # Warmer off-white with maximum opacity

            # Create the cloud layer
            clouds = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(clouds)
            draw.ellipse((0, 0, self.size-1, self.size-1), fill=cloud_color)

            # Apply the cloud mask
            clouds.putalpha(cloud_mask)

            # Store the original cloud mask for reference and debugging if needed
            # We'll use this later if we need to compare the original and adjusted masks

            # Import here to avoid circular imports
            import config
            from cosmos_generator.utils.directory_utils import ensure_directory_exists

            # Create a seed-specific directory for cloud textures
            seed_clouds_dir = os.path.join(config.PLANETS_CLOUDS_TEXTURES_DIR, str(self.seed))
            ensure_directory_exists(seed_clouds_dir)

            # Save the original cloud mask
            cloud_mask.save(os.path.join(seed_clouds_dir, "mask.png"))

            # Save a copy of the cloud mask with better visibility for reference
            enhanced_mask = cloud_mask.copy()
            # Enhance contrast for better visibility when viewed directly
            for y in range(self.size):
                for x in range(self.size):
                    pixel = enhanced_mask.getpixel((x, y))
                    if pixel > 0:  # If there's any cloud at all
                        # Boost low values for better visibility
                        enhanced_mask.putpixel((x, y), min(255, pixel + 50))
            enhanced_mask.save(os.path.join(seed_clouds_dir, "texture.png"))

            # Create a normal map from the cloud noise for 3D lighting effect
            # Use the original cloud_noise directly since it's already in the right format
            # We don't need to create a separate height map

            # Calculate light direction vector for later use
            light_direction_vector = (
                -math.cos(math.radians(self.light_angle)),
                -math.sin(math.radians(self.light_angle)),
                1.0
            )

            # Create an opacity adjustment mask based on light direction
            # This will increase opacity in illuminated areas to make clouds more visible
            opacity_adjustment_mask = self._create_light_based_opacity_mask(
                cloud_mask, light_direction_vector
            )

            # Apply the opacity adjustment to the clouds
            clouds_adjusted = clouds.copy()
            clouds_adjusted.putalpha(opacity_adjustment_mask)

            # Save the adjusted mask for debugging
            opacity_adjustment_mask.save(os.path.join(seed_clouds_dir, "adjusted_mask.png"))

            # Softer lighting for a more stylized cloud appearance
            # Higher ambient and lower diffuse for a gentler lighting effect
            lit_clouds = lighting_utils.apply_directional_light(
                clouds_adjusted,
                lighting_utils.calculate_normal_map(cloud_noise, 1.5),  # Reduced height (1.5) for gentler depth
                light_direction=light_direction_vector,
                ambient=0.85,  # Higher ambient light (0.85) for softer overall illumination
                diffuse=0.6,   # Reduced diffuse (0.6) for gentler shadows
                specular=0.05  # Minimal specular (0.05) for subtle highlights
            )

            # Apply a slightly stronger blur for a softer, more stylized appearance
            # This creates a more painterly cloud-like appearance
            lit_clouds = lit_clouds.filter(ImageFilter.GaussianBlur(0.8))  # Increased blur (0.8)

            # Apply spherical distortion to the clouds for a more realistic curved appearance
            lit_clouds = image_utils.apply_spherical_distortion(lit_clouds, strength=0.15)

            # Apply post-processing to enhance contrast in illuminated areas
            lit_clouds = self._enhance_cloud_contrast(lit_clouds, light_direction_vector)

            # If the image size is different from the planet size (due to atmosphere or rings),
            # we need to center the clouds on the planet
            if size != self.size:
                # Create a new image with the same size as the base image
                centered_clouds = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                # Calculate the offset to center the clouds
                offset = (size - self.size) // 2
                # Paste the clouds in the center
                centered_clouds.paste(lit_clouds, (offset, offset), lit_clouds)
                lit_clouds = centered_clouds

            # Composite clouds over the planet
            result = Image.alpha_composite(base_image, lit_clouds)

            duration_ms = (time.time() - start_time) * 1000
            # Log details about the clouds with enhanced parameters
            threshold = cloud_threshold
            # Calculate illuminated and shadowed opacity boost factors for logging
            illuminated_boost = 1.0 + 0.6 * 0.5  # Max boost in illuminated areas (at illumination=1.0)
            shadowed_boost = 1.0 + 0.2 * 0.5     # Max boost in shadowed areas (at illumination=0.5)

            # Log enhanced details including opacity adjustments and lighting parameters
            logger.log_step("apply_clouds", duration_ms,
                          f"Coverage: {self.cloud_coverage:.2f}, Threshold: {threshold:.2f}, " +
                          f"Opacity: base=80-255, illuminated_boost={illuminated_boost:.2f}, shadowed_boost={shadowed_boost:.2f}, " +
                          f"Lighting: ambient=0.85, diffuse=0.6, specular=0.05, blur=0.8, " +
                          f"Style: enhanced soft stylized clouds with improved visibility, Spherical distortion: 15%")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_clouds", duration_ms, f"Error: {str(e)}")
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