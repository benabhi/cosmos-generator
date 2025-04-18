"""
Cloud generation for celestial bodies.
"""
from typing import Tuple, Optional, Dict, Any
import math
import os
import time
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.utils import image_utils, lighting_utils
from cosmos_generator.utils.logger import logger


class Clouds:
    """
    Generates cloud layers with varying patterns and opacity.

    This class handles all cloud-related functionality including:
    - Cloud texture generation with various patterns and styles
    - Cloud mask creation with customizable coverage
    - Lighting effects based on planet illumination
    - Wind and other visual effects
    - Spherical distortion for realistic planet curvature
    """

    def __init__(self, seed: Optional[int] = None, coverage: float = 0.5,
                 enabled: bool = False, size: int = 512):
        """
        Initialize a cloud generator with customizable properties.

        Args:
            seed: Random seed for reproducible generation
            coverage: Cloud coverage (0.0 to 1.0, where 1.0 is maximum coverage)
            enabled: Whether clouds are enabled
            size: Size of the cloud textures in pixels
        """
        self.seed = seed
        self.rng = random.Random(seed)
        self.noise_gen = FastNoiseGenerator(seed=seed)

        # Cloud properties
        self.enabled = enabled
        self.coverage = coverage
        self.size = size

        # Default cloud appearance settings
        self.density = 0.8  # Cloud density/opacity (0.0 to 1.0)
        self.detail_level = 1.0  # Level of detail in cloud patterns (0.0 to 2.0)
        self.wind_effect = 0.0  # Wind effect strength (0.0 to 1.0)
        self.cloud_color = (245, 242, 240, 255)  # Slightly off-white for more natural clouds

        # Lighting settings
        self.light_angle = 45.0
        self.ambient_light = 0.75  # Ambient light level (0.0 to 1.0)
        self.diffuse_light = 0.7  # Diffuse light level (0.0 to 1.0)
        self.specular_light = 0.02  # Specular light level (0.0 to 1.0)

        # Generated textures (will be populated during generation)
        self.cloud_noise = None
        self.cloud_mask = None
        self.cloud_texture = None

    def generate_cloud_texture(self) -> Image.Image:
        """
        Generate a cloud texture based on the current cloud properties.
        This is the main method that creates the cloud texture with all effects applied.

        Returns:
            Cloud texture as PIL Image with all effects applied
        """
        start_time = time.time()
        try:
            # Generate the base cloud noise
            self._generate_cloud_noise()

            # Create the cloud mask from the noise
            self._create_cloud_mask()

            # Create the initial cloud texture
            self._create_initial_cloud_texture()

            # Apply lighting effects
            self._apply_lighting_to_clouds()

            # Apply wind effect if enabled
            if self.wind_effect > 0:
                self._apply_wind_effect()

            # Apply spherical distortion for realistic planet curvature
            self._apply_spherical_distortion()

            # Save debug textures
            self._save_debug_textures()

            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("generate_cloud_texture", duration_ms,
                          f"Coverage: {self.coverage:.2f}, Density: {self.density:.2f}, " +
                          f"Detail: {self.detail_level:.2f}, Wind: {self.wind_effect:.2f}, " +
                          f"Lighting: ambient={self.ambient_light:.2f}, diffuse={self.diffuse_light:.2f}, " +
                          f"Spherical distortion: 15%")

            return self.cloud_texture
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("generate_cloud_texture", duration_ms, f"Error: {str(e)}")
            raise

    def _generate_cloud_noise(self) -> None:
        """
        Generate the base cloud noise patterns using various noise algorithms.
        This creates the foundation for the cloud shapes and distribution.
        """
        # VOLUMETRIC CLOUD GENERATION
        # Base cloud layer - larger, more distributed cloud formations with better definition
        base_cloud_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                # Lower frequency for more spread-out distribution but with better definition
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.08, 0.2),
                # Fewer octaves but higher persistence for more natural cloud shapes
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.7, 2.0, 1.8 * self.detail_level)
            )
        )

        # Add a cellular noise component to create more varied cloud patterns and better clustering
        cellular_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: 1.0 - self.noise_gen.worley_noise(x, y, 6, "euclidean")
        )

        # Detail layer - enhanced texture for better cloud volume and definition
        detail_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            # Use 4 octaves for more detailed texture
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 4, 0.6, 2.0, 2.2 * self.detail_level)
        )

        # Edge definition layer - more defined edges for better cloud formations
        edge_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            # Use a stronger ridge function for better edge definition
            lambda x, y: self.noise_gen.ridged_simplex(x, y, 3, 0.6, 2.0, 2.8)
        )

        # Large-scale organization layer - helps create more realistic cloud systems
        organization_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.fractal_simplex(x, y, 2, 0.5, 2.0, 1.0)
        )

        # Combine the noise layers to create balanced cloud formations
        combined_noise = np.zeros((self.size, self.size), dtype=np.float32)

        for y in range(self.size):
            for x in range(self.size):
                # Base shape (40%) - dominant cloud formations
                base = base_cloud_noise[y, x]
                # Cellular component (25%) - helps with distribution and breaking up uniformity
                cellular = cellular_noise[y, x]
                # Detail (15%) - adds texture for volume
                detail = detail_noise[y, x]
                # Edge definition (15%) - natural cloud boundaries
                edge = edge_noise[y, x]
                # Organization (5%) - large-scale structure
                organization = organization_noise[y, x]

                # Combine with weights for more natural, volumetric appearance
                combined = base * 0.4 + cellular * 0.25 + detail * 0.15 + edge * 0.15 + organization * 0.05

                # Apply a stronger non-linear curve to create more defined cloud shapes
                if combined > 0.35 and combined < 0.75:
                    # Create a more pronounced bulge in the middle range for better definition
                    factor = (combined - 0.35) / 0.4  # 0 to 1 in the 0.35-0.75 range
                    # Use a non-linear curve (sine) for more natural cloud shapes
                    curve_factor = math.sin(factor * math.pi / 2)  # 0 to 1, non-linear
                    # Apply a stronger curve for better definition
                    curve_factor = math.pow(curve_factor, 0.8)  # Adjust the power for better definition
                    combined = 0.35 + curve_factor * 0.4  # More natural transition with better contrast

                # Add slight variation for natural appearance but maintain cloud structure
                variation = (self.rng.random() - 0.5) * 0.02  # Smaller random variation for better coherence
                combined = max(0.0, min(1.0, combined + variation))  # Keep within 0-1 range

                # Store the result
                combined_noise[y, x] = combined

        # Store the cloud noise for later use
        self.cloud_noise = combined_noise

    def _create_cloud_mask(self) -> None:
        """
        Create a cloud mask from the generated noise.
        This determines where clouds appear and their opacity.
        """
        # Create the cloud mask
        cloud_mask = Image.new("L", (self.size, self.size), 0)
        cloud_data = cloud_mask.load()

        # Adjust threshold for cloud coverage with a better curve for more defined clouds
        # Lower threshold = more clouds
        # Even at maximum coverage, we want significant areas without clouds
        base_threshold = 0.55  # Higher base threshold for better definition
        # Use a non-linear coverage factor to ensure better distribution at all coverage levels
        coverage_factor = math.pow(self.coverage, 1.2) * 0.4  # Non-linear scaling for better control
        cloud_threshold = base_threshold - coverage_factor

        # Create a secondary noise layer for cloud clustering and gaps
        # This helps create more realistic cloud formations with clear gaps
        cluster_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.05, 0.1),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 3, 0.6, 2.0, 1.5)
            )
        )

        # Fill the cloud mask with a more realistic approach for cloud-like appearance
        for y in range(self.size):
            for x in range(self.size):
                # Get the noise value at this pixel
                value = self.cloud_noise[y, x]

                # Apply the cluster noise to create more realistic cloud formations
                # This ensures that clouds form in natural clusters with clear gaps
                cluster_value = cluster_noise[y, x]

                # Calculate a dynamic threshold based on the cluster value
                # This creates more natural cloud formations with varying density
                local_threshold = cloud_threshold

                # If cluster value is low, increase the threshold to create gaps
                # This ensures that even at maximum coverage, there are clear gaps
                if cluster_value < 0.4:
                    # Scale the threshold increase based on coverage
                    # Higher coverage = larger threshold increase for more defined gaps
                    threshold_increase = (0.4 - cluster_value) * (0.3 + self.coverage * 0.3)
                    local_threshold += threshold_increase

                    # If the threshold is too high, skip this pixel entirely
                    # This creates very clear gaps between cloud formations
                    if local_threshold > 0.85:
                        continue

                # Use a narrower transition zone for more defined cloud edges
                if value > local_threshold - 0.15:  # Narrower transition zone (0.15) for more defined edges
                    if value < local_threshold:  # Edge zone
                        # Sharper transition for more defined cloud edges
                        edge_factor = (value - (local_threshold - 0.15)) / 0.15  # 0 to 1 over narrower range
                        # Use a steeper non-linear curve for more defined edge falloff
                        edge_factor = math.pow(edge_factor, 1.3)  # Steeper falloff for better definition
                        # Higher minimum opacity for more visible cloud edges
                        alpha = int(80 * edge_factor)  # 0 to 80 opacity for edges
                    else:  # Main cloud zone
                        # Calculate normalized distance from threshold
                        normalized = (value - local_threshold) / (1.0 - local_threshold)

                        # Three-zone curve for more volumetric appearance with better definition
                        if normalized < 0.3:  # Outer cloud zone
                            # Steeper transition in the outer zone for better definition
                            alpha = int(80 + normalized * 240)  # 80-150 range for outer zone
                        elif normalized < 0.65:  # Mid-cloud zone - the bulk of the cloud
                            # Middle zone has higher opacity for better visibility
                            alpha = int(150 + (normalized - 0.3) * 200)  # 150-220 range for mid zone
                        else:  # Dense cloud center
                            # Higher maximum opacity for better visibility
                            alpha = int(220 + (normalized - 0.65) * 110)  # 220-255 range for centers

                        # Apply cluster-based variation to create more natural cloud density
                        # Higher cluster values = denser clouds
                        density_factor = 0.8 + cluster_value * 0.4  # 0.8 to 1.2 range
                        alpha = int(alpha * density_factor)

                    # Apply a small random variation for natural texture
                    # Just enough to avoid perfectly smooth areas
                    variation = int((self.rng.random() - 0.5) * 10)  # Small variation (-5 to +5)
                    alpha = max(0, min(255, alpha + variation))  # Keep within 0-255 range
                    cloud_data[x, y] = alpha

        # Apply circular mask to the clouds
        circle_mask = image_utils.create_circle_mask(self.size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)

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
        Create the initial cloud texture using the cloud mask.
        This creates a base cloud image before lighting and effects are applied.
        """
        # Create the cloud layer
        clouds = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, self.size-1, self.size-1), fill=self.cloud_color)

        # Apply the cloud mask
        clouds.putalpha(self.cloud_mask)

        # Store the initial cloud texture
        self.cloud_texture = clouds

    def _create_light_based_opacity_mask(self) -> Image.Image:
        """
        Create an opacity adjustment mask based on light direction to make clouds
        more visible in illuminated areas and create a more realistic 3D appearance.
        """
        # Calculate light direction vector
        light_direction = (
            -math.cos(math.radians(self.light_angle)),
            -math.sin(math.radians(self.light_angle)),
            1.0
        )

        # Extract light direction components
        light_x, light_y = light_direction[0], light_direction[1]

        # Create a completely new illumination gradient with better lighting model
        gradient = Image.new('L', (self.size, self.size), 0)
        gradient_draw = ImageDraw.Draw(gradient)

        # The center of the gradient is offset in the direction opposite to the light
        # Use a stronger offset for more dramatic lighting effect
        center = self.size // 2
        light_center_x = int(center - light_x * center * 0.8)  # Increased from 0.7 to 0.8
        light_center_y = int(center - light_y * center * 0.8)  # Increased from 0.7 to 0.8

        # Draw concentric circles with decreasing brightness from the light center
        # Use a non-linear brightness curve for more dramatic lighting
        max_radius = int(self.size * 0.85)  # Increased from 0.8 to 0.85
        for r in range(max_radius, 0, -1):
            # Calculate brightness with a non-linear curve for more dramatic lighting
            # This creates a sharper transition between light and shadow
            normalized_radius = r / max_radius
            brightness_factor = 1.0 - normalized_radius
            # Apply a power curve to create a more dramatic falloff
            brightness_factor = math.pow(brightness_factor, 0.85)  # Less than 1.0 for more gradual falloff
            brightness = int(255 * brightness_factor)

            gradient_draw.ellipse(
                (light_center_x - r, light_center_y - r, light_center_x + r, light_center_y + r),
                fill=brightness
            )

        # Apply a circular mask to the gradient to match the planet shape
        circle_mask = image_utils.create_circle_mask(self.size)
        gradient = ImageChops.multiply(gradient, circle_mask)

        # Apply a blur to smooth the gradient, but use a smaller blur for more definition
        gradient = gradient.filter(ImageFilter.GaussianBlur(self.size // 25))  # Reduced from 20 to 25

        # Create the final adjusted mask by combining the original mask with the gradient
        mask_array = np.array(self.cloud_mask)
        gradient_array = np.array(gradient)
        adjusted_array = np.zeros_like(mask_array)

        # Apply the gradient to the mask with a more dramatic effect
        for y in range(self.size):
            for x in range(self.size):
                if mask_array[y, x] > 0:  # Only process cloud pixels
                    # Get the illumination factor from the gradient (0-255)
                    illumination = gradient_array[y, x] / 255.0

                    # Apply a stronger curve to enhance the effect in illuminated areas
                    # This makes clouds much more visible in illuminated areas
                    if illumination > 0.6:  # Brighter part of the planet
                        # Much stronger boost in well-lit areas for better visibility
                        opacity_boost = 1.0 + (illumination - 0.6) * 1.8  # Up to 72% boost in fully lit areas
                    elif illumination > 0.3:  # Mid-lit areas
                        # Moderate boost in partially lit areas
                        opacity_boost = 1.0 + (illumination - 0.3) * 0.8  # Up to 24% boost in mid-lit areas
                    else:  # Darker part of the planet
                        # Reduce opacity in shadowed areas for better contrast
                        opacity_boost = 0.8 + illumination * 0.7  # 80% to 101% in shadowed areas

                    # Apply the boost to the original opacity
                    new_opacity = min(255, int(mask_array[y, x] * opacity_boost))
                    adjusted_array[y, x] = new_opacity

        # Return the adjusted mask
        return Image.fromarray(adjusted_array)

    def _enhance_cloud_contrast(self, cloud_image: Image.Image, light_direction: tuple) -> Image.Image:
        """
        Enhance the contrast of clouds, particularly in illuminated areas.
        This creates more defined cloud formations with better visibility.

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
        result_array = img_array.copy()

        # Process each pixel with a more aggressive contrast enhancement
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
                    if illumination > 0.6:  # More illuminated side
                        # Calculate contrast factor - much stronger in more illuminated areas
                        # This creates more defined cloud formations in well-lit areas
                        contrast_factor = 1.0 + (illumination - 0.6) * 1.5  # Up to 60% increase

                        # Apply contrast enhancement to RGB channels
                        for i in range(3):
                            # Formula: new_value = 128 + (old_value - 128) * contrast_factor
                            pixel_value = float(img_array[y, x, i])
                            adjusted_value = 128 + (pixel_value - 128) * contrast_factor
                            result_array[y, x, i] = np.clip(adjusted_value, 0, 255).astype(np.uint8)

                    # Also apply a slight contrast enhancement to mid-lit areas
                    # This helps maintain some definition in partially lit areas
                    elif illumination > 0.3 and img_array[y, x, 3] > 100:  # Only enhance more opaque cloud areas
                        # Gentler contrast enhancement for mid-lit areas
                        contrast_factor = 1.0 + (illumination - 0.3) * 0.5  # Up to 15% increase

                        # Apply contrast enhancement to RGB channels
                        for i in range(3):
                            pixel_value = float(img_array[y, x, i])
                            adjusted_value = 128 + (pixel_value - 128) * contrast_factor
                            result_array[y, x, i] = np.clip(adjusted_value, 0, 255).astype(np.uint8)

                    # Slightly darken the shadowed areas for better contrast
                    elif img_array[y, x, 3] > 150:  # Only darken more opaque cloud areas
                        # Subtle darkening for shadowed areas
                        darkening_factor = 0.9 - (0.3 - illumination) * 0.2  # 0.9 to 0.7 range

                        # Apply darkening to RGB channels
                        for i in range(3):
                            pixel_value = float(img_array[y, x, i])
                            adjusted_value = pixel_value * darkening_factor
                            result_array[y, x, i] = np.clip(adjusted_value, 0, 255).astype(np.uint8)

        # Convert back to PIL Image
        enhanced_image = Image.fromarray(result_array)

        # Apply a subtle sharpening to enhance cloud definition
        enhancer = ImageEnhance.Sharpness(enhanced_image)
        enhanced_image = enhancer.enhance(1.2)  # Subtle sharpening for better definition

        return enhanced_image

    def _apply_lighting_to_clouds(self) -> None:
        """
        Apply lighting effects to the cloud texture.
        This creates a more realistic 3D appearance with proper illumination.
        """
        # Calculate light direction vector
        light_direction = (
            -math.cos(math.radians(self.light_angle)),
            -math.sin(math.radians(self.light_angle)),
            1.0
        )

        # Create an opacity adjustment mask based on light direction
        opacity_adjustment_mask = self._create_light_based_opacity_mask()

        # Apply the opacity adjustment to the clouds
        clouds_adjusted = self.cloud_texture.copy()
        clouds_adjusted.putalpha(opacity_adjustment_mask)

        # Calculate a normal map with more height variation for better volume and definition
        # Higher strength value creates more pronounced 3D effect
        cloud_normal_map = lighting_utils.calculate_normal_map(self.cloud_noise, 2.5)  # Increased from 2.2 to 2.5

        # Apply directional lighting with adjusted parameters for better cloud definition
        lit_clouds = lighting_utils.apply_directional_light(
            clouds_adjusted,
            cloud_normal_map,
            light_direction=light_direction,
            ambient=self.ambient_light * 0.9,  # Slightly reduced ambient for more contrast
            diffuse=self.diffuse_light * 1.2,  # Increased diffuse for more pronounced lighting
            specular=self.specular_light * 1.5  # Increased specular for better highlights
        )

        # Apply a very light blur for more natural cloud appearance while preserving detail
        lit_clouds = lit_clouds.filter(ImageFilter.GaussianBlur(0.5))  # Reduced from 0.6 to 0.5

        # Apply a stronger unsharp mask to enhance the cloud texture definition
        enhancer = ImageEnhance.Sharpness(lit_clouds)
        lit_clouds = enhancer.enhance(1.3)  # Increased from 1.25 to 1.3

        # Enhance contrast to make clouds more defined
        contrast_enhancer = ImageEnhance.Contrast(lit_clouds)
        lit_clouds = contrast_enhancer.enhance(1.1)  # Add 10% more contrast

        # Apply post-processing to enhance contrast in illuminated areas
        lit_clouds = self._enhance_cloud_contrast(lit_clouds, light_direction)

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
        # Import here to avoid circular imports
        import config
        from cosmos_generator.utils.directory_utils import ensure_directory_exists

        # Create a seed-specific directory for cloud textures
        seed_clouds_dir = os.path.join(config.PLANETS_CLOUDS_TEXTURES_DIR, str(self.seed))
        ensure_directory_exists(seed_clouds_dir)

        # Save the cloud mask
        if self.cloud_mask:
            self.cloud_mask.save(os.path.join(seed_clouds_dir, "mask.png"))

        # Save the cloud texture
        if self.cloud_texture:
            self.cloud_texture.save(os.path.join(seed_clouds_dir, "texture.png"))

        # Log the saved paths
        logger.debug(f"Saved cloud debug textures to {seed_clouds_dir}", "clouds")

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
