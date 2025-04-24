"""
Cloud generation for celestial bodies with a stylized appearance.
"""
from typing import Tuple, Optional, Dict, Any, List
import math
import os
import time
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.utils import image_utils, lighting_utils
from cosmos_generator.utils.logger import logger
from cosmos_generator.core.interfaces import CloudsInterface, NoiseGeneratorInterface, ColorPaletteInterface
from cosmos_generator.core.color_palette import ColorPalette


class Clouds(CloudsInterface):
    """
    Generates cloud layers with a stylized appearance that matches the planet textures.

    This class handles all cloud-related functionality including:
    - Cloud texture generation with stylized patterns
    - Cloud mask creation with customizable coverage
    - Lighting effects based on planet illumination
    - Spherical distortion for realistic planet curvature
    """

    def __init__(self, seed: Optional[int] = None, coverage: float = 0.5,
                 enabled: bool = False, size: int = 512,
                 noise_gen: Optional[NoiseGeneratorInterface] = None,
                 color_palette: Optional[ColorPaletteInterface] = None,
                 planet_type: str = "Desert"):
        """
        Initialize a stylized cloud generator with customizable properties.

        Args:
            seed: Random seed for reproducible generation
            coverage: Cloud coverage (0.0 to 1.0, where 1.0 is maximum coverage)
            enabled: Whether clouds are enabled
            size: Size of the cloud textures in pixels
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
            planet_type: Type of planet (used to determine cloud color)
        """
        self.seed = seed
        self.rng = random.Random(seed)

        # Use provided noise generator or create a new one
        self.noise_gen = noise_gen if noise_gen is not None else FastNoiseGenerator(seed=seed)

        # Store planet type for cloud color selection
        self.planet_type = planet_type

        # Use provided color palette or create a new one
        self.color_palette = color_palette if color_palette is not None else ColorPalette(seed=seed)

        # Cloud properties
        self._enabled = enabled
        self._coverage = max(0.0, min(1.0, coverage))
        self.size = size
        self.detail_level = 1.0  # Default detail level
        self.density = 0.7  # Cloud density (0.0 to 1.0)

        # Get cloud color based on planet type
        self.cloud_color = self.color_palette.get_cloud_color(self.planet_type)

        # Lighting settings
        self.light_angle = 45.0
        self.ambient_light = 0.75  # Ambient light level (0.0 to 1.0)
        self.diffuse_light = 0.7  # Diffuse light level (0.0 to 1.0)
        self.specular_light = 0.02  # Specular light level (0.0 to 1.0)
        self.light_intensity = 1.0  # Light intensity (0.0 to 1.0)
        self.light_falloff = 0.8  # Light falloff (0.0 to 1.0)
        # Generate a random wind effect between 0.0 and 1.0
        self.wind_effect = self.rng.uniform(0.0, 1.0)  # Wind effect strength (0.0 to 1.0)

        # Initialize texture attributes to None
        self.cloud_noise = None
        self.cloud_mask = None
        self.cloud_texture = None

    @property
    def enabled(self) -> bool:
        """Whether clouds are enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether clouds are enabled."""
        self._enabled = value

    @property
    def coverage(self) -> float:
        """Cloud coverage (0.0 to 1.0)."""
        return self._coverage

    @coverage.setter
    def coverage(self, value: float) -> None:
        """Set cloud coverage."""
        self._coverage = max(0.0, min(1.0, value))

        # Default cloud appearance settings
        self.density = 0.8  # Cloud density/opacity (0.0 to 1.0)
        self.detail_level = 1.0  # Level of detail in cloud patterns (0.0 to 2.0)
        # Keep the current wind effect or generate a new random one if not set
        if not hasattr(self, 'wind_effect') or self.wind_effect == 0.0:
            self.wind_effect = self.rng.uniform(0.0, 1.0)  # Wind effect strength (0.0 to 1.0)

        # Get cloud color based on planet type
        if hasattr(self, 'color_palette') and hasattr(self, 'planet_type'):
            self.cloud_color = self.color_palette.get_cloud_color(self.planet_type)
        else:
            # Fallback to default color if color_palette or planet_type is not set
            self.cloud_color = (250, 250, 255, 255)  # Slightly blue-tinted white for stylized clouds

        # Lighting settings
        self.light_angle = 45.0
        self.ambient_light = 0.75  # Ambient light level (0.0 to 1.0)
        self.diffuse_light = 0.7  # Diffuse light level (0.0 to 1.0)
        self.specular_light = 0.02  # Specular light level (0.0 to 1.0)
        self.light_intensity = 1.0  # Light intensity (0.0 to 1.0)
        self.light_falloff = 0.8  # Light falloff (0.0 to 1.0)

        # Reset generated textures when coverage changes
        self.cloud_noise = None
        self.cloud_mask = None
        self.cloud_texture = None

    def generate_cloud_texture(self) -> Image.Image:
        """
        Generate a stylized cloud texture that matches the planet texture style.

        Returns:
            Cloud texture as PIL Image with all effects applied
        """
        start_time = time.time()
        try:
            # Generate the base cloud noise with a more stylized approach
            self._generate_cloud_noise()

            # Create the cloud mask from the noise with more defined edges
            self._create_cloud_mask()

            # Create the initial cloud texture
            self._create_initial_cloud_texture()

            # Apply lighting effects
            self._apply_lighting_to_clouds()

            # Wind effect removed as requested
            # No longer applying wind effect to clouds

            # Apply spherical distortion for realistic planet curvature
            self._apply_spherical_distortion()

            # Save debug textures
            self._save_debug_textures()

            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("generate_cloud_texture", duration_ms,
                          f"Coverage: {self.coverage:.2f}, Density: {self.density:.2f}, " +
                          f"Detail: {self.detail_level:.2f}, " +
                          f"Lighting: ambient={self.ambient_light:.2f}, diffuse={self.diffuse_light:.2f}, " +
                          f"Spherical distortion: 15%")

            return self.cloud_texture
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("generate_cloud_texture", duration_ms, f"Error: {str(e)}")
            raise

    def _generate_cloud_noise(self) -> None:
        """
        Generate realistic cloud noise patterns that form interconnected cumulus-like formations.
        Creates cloud patterns that are identifiable as clouds while leaving gaps to show terrain.
        """
        # CUMULUS CLOUD GENERATION
        # Base cloud layer - creates the main cloud formations with clear definition
        base_cloud_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Medium frequency for distinct cloud formations
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.03, 0.1),
                # Use more octaves for better cloud definition
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 3, 0.7, 2.0, 1.3 * self.detail_level)
            )
        )

        # Cellular component for creating distinct cloud "cells" (cumulus formations)
        cellular_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            # More cells for distinct cumulus formations
            lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 5, "euclidean")
        )

        # Detail layer - adds texture to the clouds
        detail_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            # Higher frequency for cloud texture details
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 3, 0.5, 2.2, 2.0 * self.detail_level)
        )

        # Connection layer - helps create bridges between cloud formations
        connection_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Lower frequency for larger connecting structures
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.02, 0.06),
                # Fewer octaves for smoother connections
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 2, 0.6, 1.8, 1.0)
            )
        )

        # Large-scale organization layer - creates overall cloud systems
        organization_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            # Very low frequency for large-scale organization
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 1, 0.5, 2.0, 0.6)
        )

        # Combine the noise layers to create realistic cloud formations
        combined_noise = np.zeros((self.size, self.size), dtype=np.float32)

        for y in range(self.size):
            for x in range(self.size):
                # Base shape (40%) - main cloud formations
                base = base_cloud_noise[y, x]
                # Cellular component (25%) - creates distinct cumulus shapes
                cellular = cellular_noise[y, x]
                # Detail (10%) - adds texture to clouds
                detail = detail_noise[y, x]
                # Connection (15%) - creates bridges between cloud formations
                connection = connection_noise[y, x]
                # Organization (10%) - large-scale structure
                organization = organization_noise[y, x]

                # Combine with weights for realistic cloud formations
                combined = (base * 0.4 +
                           cellular * 0.25 +
                           detail * 0.1 +
                           connection * 0.15 +
                           organization * 0.1)

                # Create more defined cloud edges
                if combined > 0.45:
                    # Boost higher values to create more defined clouds
                    boost_factor = (combined - 0.45) * 0.5
                    combined += boost_factor
                    combined = min(1.0, combined)  # Cap at 1.0

                # Create clear separation between clouds and gaps
                if combined < 0.4:
                    # Reduce lower values to create clearer gaps
                    reduction_factor = (0.4 - combined) * 0.5
                    combined -= reduction_factor
                    combined = max(0.0, combined)  # Keep within 0-1 range

                # Apply a non-linear curve to create puffy cloud shapes
                if combined > 0.4 and combined < 0.7:
                    # Create more pronounced edges for cumulus appearance
                    factor = (combined - 0.4) / 0.3  # 0 to 1 in the 0.4-0.7 range
                    # Use a steeper curve for more defined cloud edges
                    curve_factor = math.pow(factor, 1.5)  # Steeper curve for puffy appearance
                    combined = 0.4 + curve_factor * 0.3  # More defined transition

                # Add slight variation for natural appearance
                variation = (self.rng.random() - 0.5) * 0.01  # Small random variation
                combined = max(0.0, min(1.0, combined + variation))  # Keep within 0-1 range

                # Store the result
                combined_noise[y, x] = combined

        # Store the cloud noise for later use
        self.cloud_noise = combined_noise

    def _create_cloud_mask(self) -> None:
        """
        Create a realistic cloud mask from the generated noise.
        Creates interconnected cumulus-like cloud formations with well-defined edges.
        """
        # Create the cloud mask
        cloud_mask = Image.new("L", (self.size, self.size), 0)
        cloud_data = cloud_mask.load()

        # Adjust threshold based on coverage
        # Use a more responsive curve to maintain the requested coverage level
        base_threshold = 0.42  # Lower base threshold for better cloud formation
        # Use a non-linear coverage factor that responds well to the coverage parameter
        coverage_factor = math.pow(self.coverage, 0.7) * 0.55
        cloud_threshold = base_threshold - coverage_factor

        # Create a connectivity noise layer to help form bridges between cloud formations
        connectivity_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Medium frequency for natural cloud connections
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.02, 0.05),
                # Use fewer octaves for smoother connections
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 2, 0.6, 1.8, 0.8)
            )
        )

        # Fill the cloud mask with a more realistic approach for cumulus-like formations
        for y in range(self.size):
            for x in range(self.size):
                # Get the noise value at this pixel
                value = self.cloud_noise[y, x]

                # Get connectivity value to create bridges between clouds
                connectivity = connectivity_noise[y, x]

                # Boost connectivity in mid-range values to create cloud bridges
                # This helps create interconnected cloud systems
                if connectivity > 0.35 and connectivity < 0.65:
                    # Calculate boost factor based on distance from center of range
                    center_dist = abs(connectivity - 0.5)
                    boost_factor = 0.15 * (1.0 - center_dist * 6.0)  # Max boost at 0.5
                    boost_factor = max(0.0, boost_factor)

                    # Apply boost to the value to create connections
                    if value < cloud_threshold and value > cloud_threshold - 0.15:
                        value += boost_factor

                # Calculate local threshold based on coverage and position
                local_threshold = cloud_threshold

                # Create gaps between cloud formations
                # Less aggressive with gaps when coverage is high
                if connectivity < 0.3:
                    # Scale the threshold increase based on coverage
                    gap_factor = (0.3 - connectivity) * (0.25 - self.coverage * 0.15)
                    local_threshold += gap_factor

                    # Skip pixels that are definitely in gaps
                    if local_threshold > 0.8 or value < local_threshold - 0.2:
                        continue

                # Create cloud formations with well-defined edges
                if value > local_threshold - 0.1:
                    if value < local_threshold:  # Edge zone
                        # Create a smooth transition at cloud edges
                        edge_factor = (value - (local_threshold - 0.1)) / 0.1
                        # Use a curve that creates puffy cloud edges
                        edge_factor = math.pow(edge_factor, 1.2)
                        # Start with moderate opacity for visible edges
                        alpha = int(60 + edge_factor * 60)
                    else:  # Main cloud zone
                        # Calculate normalized distance from threshold
                        normalized = (value - local_threshold) / (1.0 - local_threshold)

                        # Three-zone curve for realistic cloud density
                        if normalized < 0.3:  # Outer cloud zone
                            # Gradual increase in opacity for outer areas
                            alpha = int(120 + normalized * 200)
                        elif normalized < 0.6:  # Middle cloud zone
                            # Higher opacity for middle areas
                            alpha = int(180 + (normalized - 0.3) * 150)
                        else:  # Dense cloud center
                            # Maximum opacity for cloud centers
                            alpha = int(225 + (normalized - 0.6) * 30)

                        # Apply density variation based on connectivity
                        # Higher density in well-connected areas
                        density_factor = 0.9 + connectivity * 0.2
                        alpha = int(alpha * density_factor)

                    # Apply small random variation for natural texture
                    variation = int((self.rng.random() - 0.5) * 5)
                    alpha = max(0, min(255, alpha + variation))
                    cloud_data[x, y] = alpha

        # Apply circular mask to the clouds
        circle_mask = image_utils.create_circle_mask(self.size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)

        # Apply a moderate sharpening to enhance cloud definition
        enhancer = ImageEnhance.Sharpness(cloud_mask)
        cloud_mask = enhancer.enhance(1.4)  # Sharpen the mask for better definition

        # Apply a very slight blur to soften the harshest edges
        cloud_mask = cloud_mask.filter(ImageFilter.GaussianBlur(0.5))

        # Enhance contrast to make cloud formations more distinct
        contrast = ImageEnhance.Contrast(cloud_mask)
        cloud_mask = contrast.enhance(1.15)

        # Store the cloud mask for later use
        self.cloud_mask = cloud_mask

    def apply_to_planet(self, planet_image: Image.Image) -> Image.Image:
        """
        Apply the generated cloud texture to a planet image.

        Args:
            planet_image: Base planet image

        Returns:
            Planet image with clouds applied
        """
        # If clouds are not enabled, return the original image
        if not self.enabled:
            return planet_image

        # Ensure the planet image has an alpha channel
        if planet_image.mode != "RGBA":
            planet_image = planet_image.convert("RGBA")

        # If we don't have a cloud texture yet, generate it
        if self.cloud_texture is None:
            self.generate_cloud_texture()

        # Get the size of the planet image (may include atmosphere)
        planet_size = planet_image.width

        # If the planet size is different from the cloud size,
        # we need to center the clouds on the planet
        if planet_size != self.size:
            # Create a new image with the same size as the planet image
            centered_clouds = Image.new("RGBA", (planet_size, planet_size), (0, 0, 0, 0))
            # Calculate the offset to center the clouds
            offset = (planet_size - self.size) // 2
            # Paste the clouds in the center
            centered_clouds.paste(self.cloud_texture, (offset, offset), self.cloud_texture)
            cloud_texture = centered_clouds
        else:
            cloud_texture = self.cloud_texture

        # Composite clouds over the planet
        result = Image.alpha_composite(planet_image, cloud_texture)

        return result

    def _create_initial_cloud_texture(self) -> None:
        """
        Create the initial stylized cloud texture using the cloud mask.
        """
        # Create the cloud layer
        clouds = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, self.size-1, self.size-1), fill=self.cloud_color)

        # Apply the cloud mask
        clouds.putalpha(self.cloud_mask)

        # Store the initial cloud texture
        self.cloud_texture = clouds





    def _apply_lighting_to_clouds(self) -> None:
        """
        Apply lighting effects to the cloud texture with EXACTLY the same parameters as the planet.
        This ensures perfect alignment of shadows and highlights between terrain and clouds.
        """
        # Calculate light direction vector with the same angle as the planet
        light_rad = math.radians(self.light_angle)
        light_x = math.cos(light_rad)
        light_y = -math.sin(light_rad)  # Negative because y increases downward in images

        # Convert image to numpy array for processing
        img_array = np.array(self.cloud_texture)
        height, width = img_array.shape[:2]
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)

        # Create a new array for the result
        result_array = np.zeros_like(img_array)

        # Process each pixel to apply lighting
        for y in range(height):
            for x in range(width):
                # Skip if the pixel is transparent
                if img_array[y, x, 3] == 0:
                    continue

                # Calculate position relative to center - EXACTLY as in TextureGenerator.apply_lighting
                dx = (x - center_x) / radius
                dy = (y - center_y) / radius
                distance = math.sqrt(dx*dx + dy*dy)

                # Skip if outside the sphere
                if distance > 1.0:
                    continue

                # Calculate surface normal at this point - EXACTLY as in TextureGenerator.apply_lighting
                z = math.sqrt(1.0 - distance*distance)
                nx, ny, nz = dx, dy, z

                # Calculate dot product with light direction - EXACTLY as in TextureGenerator.apply_lighting
                dot = nx * light_x + ny * light_y + nz * 1.0

                # Apply lighting factor - EXACTLY as in TextureGenerator.apply_lighting
                if dot < 0:
                    # Point is facing away from light
                    factor = 0.1  # Ambient light - same as terrain
                else:
                    # Apply light intensity and falloff - same as terrain
                    factor = 0.1 + 0.9 * self.light_intensity * (dot ** self.light_falloff)

                # Apply lighting to color channels
                r = min(255, int(img_array[y, x, 0] * factor))
                g = min(255, int(img_array[y, x, 1] * factor))
                b = min(255, int(img_array[y, x, 2] * factor))

                # Set result pixel with original alpha
                result_array[y, x] = [r, g, b, img_array[y, x, 3]]

        # Convert back to PIL Image
        lit_clouds = Image.fromarray(result_array)

        # Apply post-processing effects to enhance cloud appearance
        # These don't affect the lighting alignment, just the visual quality

        # Apply a very light blur for smoother appearance
        lit_clouds = lit_clouds.filter(ImageFilter.GaussianBlur(0.3))

        # Apply an unsharp mask to enhance the cloud texture definition
        enhancer = ImageEnhance.Sharpness(lit_clouds)
        lit_clouds = enhancer.enhance(1.2)

        # Enhance contrast slightly to make cloud formations more distinct
        contrast_enhancer = ImageEnhance.Contrast(lit_clouds)
        lit_clouds = contrast_enhancer.enhance(1.1)

        # Update the cloud texture
        self.cloud_texture = lit_clouds



    def _apply_wind_effect(self) -> None:
        """
        Apply a wind effect to the cloud texture.
        This creates a more dynamic appearance with directional flow.
        """
        if self.wind_effect <= 0:
            return  # No wind effect to apply

        # Create a displacement map for the wind effect
        # The displacement is stronger in the direction of the wind
        wind_angle = (self.light_angle + 90) % 360  # Wind perpendicular to light direction
        wind_rad = math.radians(wind_angle)
        wind_x = math.cos(wind_rad) * self.wind_effect * 10  # Scale factor for visible effect
        wind_y = math.sin(wind_rad) * self.wind_effect * 10

        # Create noise for the wind displacement
        wind_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 3, 0.5, 2.0, 2.0)
        )

        # Create the displacement map
        displacement_map = np.zeros((self.size, self.size, 2), dtype=np.float32)
        for y in range(self.size):
            for x in range(self.size):
                # Calculate displacement based on wind direction and noise
                noise_val = wind_noise[y, x] * 2 - 1  # Convert to -1 to 1 range
                displacement_map[y, x, 0] = wind_x * noise_val
                displacement_map[y, x, 1] = wind_y * noise_val

        # Apply the displacement to the cloud texture
        img_array = np.array(self.cloud_texture)
        result_array = np.zeros_like(img_array)

        # Apply displacement to each pixel
        for y in range(self.size):
            for x in range(self.size):
                # Skip if the pixel is fully transparent
                if img_array[y, x, 3] == 0:
                    continue

                # Calculate source coordinates with displacement
                src_x = x + displacement_map[y, x, 0]
                src_y = y + displacement_map[y, x, 1]

                # Ensure source coordinates are within bounds
                src_x = max(0, min(self.size - 1, src_x))
                src_y = max(0, min(self.size - 1, src_y))

                # Get the nearest pixel (simple approach)
                src_x_int = int(src_x)
                src_y_int = int(src_y)

                # Copy the pixel
                result_array[y, x] = img_array[src_y_int, src_x_int]

        # Convert back to PIL Image
        self.cloud_texture = Image.fromarray(result_array)

    def _apply_spherical_distortion(self) -> None:
        """
        Apply spherical distortion to the cloud texture.
        This creates a more realistic curved appearance on the planet.
        """
        # Apply spherical distortion to the clouds for a more realistic curved appearance
        logger.debug(f"Applying spherical distortion to cloud texture (strength: 0.15)", "clouds")
        self.cloud_texture = image_utils.apply_spherical_distortion(self.cloud_texture, strength=0.15)

    def _save_debug_textures(self) -> None:
        """
        Save debug textures for analysis and debugging.
        """
        # Only save debug textures if clouds are enabled
        if not self.enabled:
            return

        # Import here to avoid circular imports
        import config
        from cosmos_generator.utils.directory_utils import ensure_directory_exists

        # Format seed as 8-digit string
        seed_str = str(self.seed).zfill(8)

        # Get the planet type from the logger's generation context
        planet_type = logger.generation_context.get("planet_type", "unknown").lower()

        # Save the cloud mask
        if self.cloud_mask:
            mask_path = config.get_planet_texture_path(planet_type, seed_str, "cloud_mask")
            ensure_directory_exists(os.path.dirname(mask_path))
            self.cloud_mask.save(mask_path)

        # Save the cloud texture
        if self.cloud_texture:
            texture_path = config.get_planet_texture_path(planet_type, seed_str, "cloud_texture")
            ensure_directory_exists(os.path.dirname(texture_path))
            self.cloud_texture.save(texture_path)

        # Log the saved paths
        logger.debug(f"Saved cloud textures for {planet_type} planet with seed {seed_str}", "clouds")

    def set_light_angle(self, angle: float) -> None:
        """
        Set the light angle for cloud illumination.

        Args:
            angle: Light angle in degrees
        """
        self.light_angle = angle
        # Reset the cloud texture so it will be regenerated with the new angle
        self.cloud_texture = None

    def set_coverage(self, coverage: float) -> None:
        """
        Set the cloud coverage.

        Args:
            coverage: Cloud coverage (0.0 to 1.0)
        """
        self.coverage = max(0.0, min(1.0, coverage))
        # Reset the cloud texture so it will be regenerated with the new coverage
        self.cloud_texture = None

    def set_wind_effect(self, strength: float) -> None:
        """
        Set the wind effect strength.

        Args:
            strength: Wind effect strength (0.0 to 1.0)
        """
        self.wind_effect = max(0.0, min(1.0, strength))
        # Reset the cloud texture so it will be regenerated with the new wind effect
        self.cloud_texture = None

    def set_detail_level(self, detail: float) -> None:
        """
        Set the detail level for cloud patterns.

        Args:
            detail: Detail level (0.0 to 2.0)
        """
        self.detail_level = max(0.0, min(2.0, detail))
        # Reset the cloud texture so it will be regenerated with the new detail level
        self.cloud_texture = None
