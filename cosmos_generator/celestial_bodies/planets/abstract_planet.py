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
from typing import Optional, Dict, Any
import os
import time
from PIL import Image

from cosmos_generator.utils.logger import logger

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
from cosmos_generator.features.rings import Rings
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.utils import image_utils
from cosmos_generator.core.interfaces import PlanetInterface, NoiseGeneratorInterface, ColorPaletteInterface, TextureGeneratorInterface, AtmosphereInterface, CloudsInterface, RingsInterface


class AbstractPlanet(AbstractCelestialBody, PlanetInterface):
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

    def __init__(self, seed: Optional[int] = None, size: int = 512,
                 noise_gen: Optional[NoiseGeneratorInterface] = None,
                 color_palette: Optional[ColorPaletteInterface] = None,
                 texture_gen: Optional[TextureGeneratorInterface] = None,
                 atmosphere: Optional[AtmosphereInterface] = None,
                 clouds: Optional[CloudsInterface] = None,
                 rings: Optional[RingsInterface] = None,
                 **kwargs):
        """
        Initialize a planet with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            size: Size of the planet image in pixels
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
            texture_gen: Optional texture generator instance (will create one if not provided)
            atmosphere: Optional atmosphere instance (will create one if not provided)
            clouds: Optional clouds instance (will create one if not provided)
            rings: Optional rings instance (will create one if not provided)
            **kwargs: Additional parameters for customization
        """
        # Import here to avoid circular imports
        from cosmos_generator.utils.validation import sanitize_planet_params
        from cosmos_generator.utils.exceptions import ValidationError

        # Store the original requested size for later use
        original_size = size

        # Log the raw parameters for debugging
        logger.debug(f"Parameters from kwargs: {kwargs}", "planet")
        logger.debug(f"Rings parameter: {rings}", "planet")
        logger.debug(f"Atmosphere parameter: {atmosphere}", "planet")
        logger.debug(f"Clouds parameter: {clouds}", "planet")

        # Process feature flags from both kwargs and positional parameters
        feature_flags = self._process_feature_flags(
            atmosphere=atmosphere,
            clouds=clouds,
            rings=rings,
            kwargs=kwargs
        )

        # Extract feature flags
        has_atmosphere = feature_flags['atmosphere']
        has_clouds = feature_flags['clouds']
        has_rings = feature_flags['rings']

        # Log the feature flags for debugging
        logger.debug(f"Feature flags: atmosphere={has_atmosphere}, rings={has_rings}, clouds={has_clouds}", "planet")

        # Sanitize parameters
        sanitized_kwargs = sanitize_planet_params(kwargs)

        # Create a params dictionary to store additional parameters
        self.params = sanitized_kwargs.copy()
        # Add original_size to params
        self.params["original_size"] = original_size

        # No need to adjust size for atmosphere anymore, as we handle it in _apply_atmosphere
        super().__init__(seed=seed, size=size,
                        noise_gen=noise_gen,
                        color_palette=color_palette,
                        texture_gen=texture_gen,
                        **sanitized_kwargs)

        # Default lighting parameters
        self.light_angle = sanitized_kwargs.get("light_angle", 45.0)
        self.light_intensity = sanitized_kwargs.get("light_intensity", 1.0)
        self.light_falloff = sanitized_kwargs.get("light_falloff", 0.6)

        # Feature flags
        self.has_rings = has_rings
        self.has_atmosphere = has_atmosphere
        self.has_clouds = has_clouds

        # Initialize features
        self._initialize_clouds(clouds, has_clouds, sanitized_kwargs)
        self._initialize_atmosphere(atmosphere, has_atmosphere, sanitized_kwargs)
        self._initialize_rings(rings, has_rings, sanitized_kwargs)

    def _process_feature_flags(self, atmosphere, clouds, rings, kwargs):
        """
        Process feature flags from both kwargs and positional parameters.

        Args:
            atmosphere: Atmosphere parameter from constructor
            clouds: Clouds parameter from constructor
            rings: Rings parameter from constructor
            kwargs: Additional parameters

        Returns:
            Dictionary with processed feature flags
        """
        # Extract the feature flags directly from kwargs
        atmosphere_param = kwargs.get("atmosphere", False)
        rings_param = kwargs.get("rings", False)
        clouds_param = kwargs.get("clouds", False)

        # Use the positional parameters if they are provided
        if rings is not None and not isinstance(rings, bool):
            # If rings is an instance of RingsInterface, it means rings are enabled
            rings_param = True
        elif rings is True:
            # If rings is True, it means rings are enabled
            rings_param = True

        if atmosphere is not None and not isinstance(atmosphere, bool):
            # If atmosphere is an instance of AtmosphereInterface, it means atmosphere is enabled
            atmosphere_param = True
        elif atmosphere is True:
            # If atmosphere is True, it means atmosphere is enabled
            atmosphere_param = True

        if clouds is not None and not isinstance(clouds, bool):
            # If clouds is an instance of CloudsInterface, it means clouds are enabled
            clouds_param = True
        elif clouds is True:
            # If clouds is True, it means clouds are enabled
            clouds_param = True

        # Check if cloud_coverage is provided, which implies clouds should be enabled
        if "cloud_coverage" in kwargs and kwargs["cloud_coverage"] is not None:
            clouds_param = True

        # Check if any atmosphere parameters are provided, which implies atmosphere should be enabled
        if any(param in kwargs for param in ["atmosphere_glow", "atmosphere_halo", "atmosphere_thickness", "atmosphere_blur"]):
            atmosphere_param = True

        # Check if any rings parameters are provided, which implies rings should be enabled
        if any(param in kwargs for param in ["rings_complexity", "rings_tilt"]):
            rings_param = True

        # Log the raw parameters for debugging
        logger.debug(
            f"Raw parameters: atmosphere={atmosphere_param} (type: {type(atmosphere_param)}), "
            f"rings={rings_param} (type: {type(rings_param)}), "
            f"clouds={clouds_param} (type: {type(clouds_param)})",
            "planet"
        )

        # Convert to boolean and return
        return {
            'atmosphere': bool(atmosphere_param),
            'rings': bool(rings_param),
            'clouds': bool(clouds_param)
        }

    def _initialize_clouds(self, clouds_param, has_clouds, kwargs):
        """
        Initialize the clouds feature.

        Args:
            clouds_param: Clouds parameter from constructor
            has_clouds: Whether clouds are enabled
            kwargs: Additional parameters
        """
        # Initialize cloud system
        if clouds_param is not None and not isinstance(clouds_param, bool):
            self.clouds = clouds_param
            # Update cloud properties based on kwargs
            if has_clouds:
                self.clouds.enabled = True
                if "cloud_coverage" in kwargs:
                    self.clouds.coverage = kwargs["cloud_coverage"]
            else:
                self.clouds.enabled = False
            # Set the light angle for the clouds to match the planet for consistent illumination
            self.clouds.set_light_angle(self.light_angle)
        else:
            # Create a new clouds instance
            cloud_coverage = kwargs.get("cloud_coverage", 0.5)
            self.clouds = Clouds(
                seed=self.seed,
                coverage=cloud_coverage,
                enabled=has_clouds,
                size=self.size,
                color_palette=self.color_palette,
                planet_type=self.PLANET_TYPE
            )
            # Ensure the clouds are enabled if has_clouds is True
            self.clouds.enabled = has_clouds
            # Set the light angle for the clouds to match the planet for consistent illumination
            self.clouds.set_light_angle(self.light_angle)

    def _initialize_atmosphere(self, atmosphere_param, has_atmosphere, kwargs):
        """
        Initialize the atmosphere feature.

        Args:
            atmosphere_param: Atmosphere parameter from constructor
            has_atmosphere: Whether atmosphere is enabled
            kwargs: Additional parameters
        """
        # Initialize atmosphere system
        if atmosphere_param is not None and not isinstance(atmosphere_param, bool):
            self.atmosphere = atmosphere_param
            # Update atmosphere properties based on kwargs
            if has_atmosphere:
                self.atmosphere.enabled = True
                if "atmosphere_glow" in kwargs:
                    self.atmosphere.glow_intensity = kwargs["atmosphere_glow"]
                if "atmosphere_halo" in kwargs:
                    self.atmosphere.halo_intensity = kwargs["atmosphere_halo"]
                if "atmosphere_thickness" in kwargs:
                    self.atmosphere.halo_thickness = kwargs["atmosphere_thickness"]
                if "atmosphere_blur" in kwargs:
                    self.atmosphere.blur_amount = kwargs["atmosphere_blur"]
            else:
                self.atmosphere.enabled = False
        else:
            # Create a new atmosphere instance
            atmosphere_glow = kwargs.get("atmosphere_glow", 0.5)
            atmosphere_halo = kwargs.get("atmosphere_halo", 0.7)
            atmosphere_thickness = kwargs.get("atmosphere_thickness", 3)
            atmosphere_blur = kwargs.get("atmosphere_blur", 0.5)
            self.atmosphere = Atmosphere(
                seed=self.seed,
                enabled=has_atmosphere,
                glow_intensity=atmosphere_glow,
                halo_intensity=atmosphere_halo,
                halo_thickness=atmosphere_thickness,
                blur_amount=atmosphere_blur
            )
            # Ensure the atmosphere is enabled if has_atmosphere is True
            self.atmosphere.enabled = has_atmosphere

    def _initialize_rings(self, rings_param, has_rings, kwargs):
        """
        Initialize the rings feature.

        Args:
            rings_param: Rings parameter from constructor
            has_rings: Whether rings are enabled
            kwargs: Additional parameters
        """
        # Initialize rings system
        if rings_param is not None and not isinstance(rings_param, bool):
            self.rings_generator = rings_param
            # Ensure the rings are enabled if has_rings is True
            self.rings_generator.enabled = has_rings
        else:
            # Create a new rings instance
            self.rings_generator = Rings(seed=self.seed, enabled=has_rings)

        # Store rings parameters if provided
        if "rings_complexity" in kwargs:
            self.rings_complexity = kwargs["rings_complexity"]
        if "rings_tilt" in kwargs:
            self.rings_tilt = kwargs["rings_tilt"]

    def render(self) -> Image.Image:
        """
        Render the planet with the common generation flow.

        Returns:
            PIL Image of the planet

        Raises:
            PlanetGenerationError: If there is an error during planet generation
            FeatureError: If there is an error applying a feature
            ResourceNotFoundError: If a required resource is not found
        """
        # Import here to avoid circular imports
        from cosmos_generator.utils.exceptions import PlanetGenerationError, FeatureError, ResourceNotFoundError

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
            texture = self._generate_base_texture()

            # Save the base texture
            texture_path = self._save_base_texture(texture)
            logger.debug(f"Saved base texture to {texture_path}", "planet")

            # Apply lighting
            lit_texture = self._apply_lighting_with_logging(texture)

            # Apply features
            result = self.apply_features(lit_texture)

            # Log successful generation
            logger.end_generation(True)

            return result

        except (PlanetGenerationError, FeatureError, ResourceNotFoundError):
            # These are already logged and formatted properly, just re-raise
            logger.end_generation(False)
            raise
        except Exception as e:
            # Unexpected error, wrap in PlanetGenerationError
            error_msg = f"Error rendering planet: {str(e)}"
            logger.error(error_msg, "planet", exc_info=True)
            logger.end_generation(False, error=str(e))
            raise PlanetGenerationError(
                message=error_msg,
                planet_type=self.PLANET_TYPE,
                seed=self.seed
            ) from e

    def _generate_base_texture(self) -> Image.Image:
        """
        Generate the base texture with timing and error handling.

        Returns:
            Base texture image

        Raises:
            PlanetGenerationError: If there is an error generating the texture
        """
        from cosmos_generator.utils.exceptions import PlanetGenerationError

        start_time = time.time()
        try:
            logger.debug(f"Generating texture for {self.PLANET_TYPE} planet (size: {self.size}x{self.size})", "planet")
            texture = self.generate_texture()

            # Apply spherical distortion to the terrain texture
            texture = image_utils.apply_spherical_distortion(texture, strength=0.15)

            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("generate_texture", duration_ms, f"Type: {self.PLANET_TYPE}, Size: {self.size}x{self.size}, Spherical distortion: 15%")
            return texture
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Failed to generate texture: {str(e)}"
            logger.log_step("generate_texture", duration_ms, f"Error: {str(e)}")
            raise PlanetGenerationError(
                message=error_msg,
                planet_type=self.PLANET_TYPE,
                seed=self.seed
            ) from e

    def _save_base_texture(self, texture: Image.Image) -> str:
        """
        Save the base texture to disk.

        Args:
            texture: The texture to save

        Returns:
            Path to the saved texture

        Raises:
            ResourceNotFoundError: If the texture directory cannot be created
        """
        from cosmos_generator.utils.exceptions import ResourceNotFoundError

        try:
            # Import here to avoid circular imports
            import config
            from cosmos_generator.utils.directory_utils import ensure_directory_exists

            # Format seed as 8-digit string
            seed_str = str(self.seed).zfill(8)

            # Save the base texture in the new structure
            texture_path = config.get_planet_texture_path(self.PLANET_TYPE.lower(), seed_str, "terrain")
            ensure_directory_exists(os.path.dirname(texture_path))
            texture.save(texture_path)
            return texture_path
        except Exception as e:
            error_msg = f"Failed to save base texture: {str(e)}"
            logger.error(error_msg, "planet", exc_info=True)
            raise ResourceNotFoundError(
                resource_type="texture directory",
                identifier=os.path.dirname(config.get_planet_texture_path(self.PLANET_TYPE.lower(), str(self.seed).zfill(8), "terrain"))
            ) from e

    def _apply_lighting_with_logging(self, texture: Image.Image) -> Image.Image:
        """
        Apply lighting to the texture with timing and error handling.

        Args:
            texture: The texture to light

        Returns:
            Lit texture

        Raises:
            PlanetGenerationError: If there is an error applying lighting
        """
        from cosmos_generator.utils.exceptions import PlanetGenerationError

        start_time = time.time()
        try:
            logger.debug(f"Applying lighting to {self.PLANET_TYPE} planet (angle: {self.light_angle}°, intensity: {self.light_intensity})", "planet")
            lit_texture = self.apply_lighting(texture)
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_lighting", duration_ms, f"Angle: {self.light_angle}°, Intensity: {self.light_intensity}, Falloff: {self.light_falloff}")
            return lit_texture
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Failed to apply lighting: {str(e)}"
            logger.log_step("apply_lighting", duration_ms, f"Error: {str(e)}")
            raise PlanetGenerationError(
                message=error_msg,
                planet_type=self.PLANET_TYPE,
                seed=self.seed
            ) from e

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

        Raises:
            FeatureError: If there is an error applying a feature
        """
        from cosmos_generator.utils.exceptions import FeatureError

        start_time = time.time()
        try:
            result = base_image
            features_applied = []

            # Log the feature flags for debugging
            logger.debug(f"Applying features with flags: atmosphere={self.has_atmosphere}, rings={self.has_rings}, clouds={self.has_clouds}", "planet")

            # The order of applying features is important:
            # 1. First apply atmosphere if enabled (before anything else)
            if self.has_atmosphere and self.atmosphere.enabled:
                result = self._apply_atmosphere_feature(result)
                features_applied.append("atmosphere")

            # 2. Then apply clouds if enabled
            if self.has_clouds and self.clouds.enabled:
                result = self._apply_clouds_feature(result)
                features_applied.append("clouds")

            # 3. Finally apply rings if enabled
            if self.has_rings and self.rings_generator.enabled:
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
        except FeatureError:
            # Re-raise FeatureError as it's already properly formatted
            duration_ms = (time.time() - start_time) * 1000
            logger.log_step("apply_features", duration_ms, "Error applying features")
            raise
        except Exception as e:
            # Wrap other exceptions in FeatureError
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Error applying features: {str(e)}"
            logger.log_step("apply_features", duration_ms, f"Error: {str(e)}")
            raise FeatureError(message=error_msg, feature="multiple") from e

    def _apply_atmosphere_feature(self, image: Image.Image) -> Image.Image:
        """
        Apply atmosphere feature with error handling.

        Args:
            image: Base planet image

        Returns:
            Planet image with atmosphere

        Raises:
            FeatureError: If there is an error applying atmosphere
        """
        from cosmos_generator.utils.exceptions import FeatureError

        try:
            # Get base and highlight colors for the planet
            try:
                # Try to get colors from the planet's palette
                color_palette_id = getattr(self, 'color_palette_id', None)
                if color_palette_id is not None:
                    base_color = self.color_palette.get_random_color(self.PLANET_TYPE, f"base_{color_palette_id}")
                    highlight_color = self.color_palette.get_random_color(self.PLANET_TYPE, f"highlight_{color_palette_id}")
                    logger.debug(f"Applying atmosphere to {self.PLANET_TYPE} planet with colors from palette {color_palette_id}", "planet")
                else:
                    base_color = None
                    highlight_color = None
                    logger.debug(f"Applying atmosphere to {self.PLANET_TYPE} planet with default colors", "planet")
            except Exception as e:
                # If there's an error, use default colors
                logger.debug(f"Error getting planet colors: {str(e)}, using default colors", "planet")
                base_color = None
                highlight_color = None

            # Apply atmosphere
            return self.atmosphere.apply_to_planet(
                planet_image=image,
                planet_type=self.PLANET_TYPE,
                has_rings=self.has_rings,
                base_color=base_color,
                highlight_color=highlight_color
            )
        except Exception as e:
            error_msg = f"Failed to apply atmosphere: {str(e)}"
            logger.error(error_msg, "planet", exc_info=True)
            raise FeatureError(message=error_msg, feature="atmosphere") from e

    def _apply_clouds_feature(self, image: Image.Image) -> Image.Image:
        """
        Apply clouds feature with error handling.

        Args:
            image: Base planet image

        Returns:
            Planet image with clouds

        Raises:
            FeatureError: If there is an error applying clouds
        """
        from cosmos_generator.utils.exceptions import FeatureError

        try:
            logger.debug(f"Applying clouds to {self.PLANET_TYPE} planet (coverage: {self.clouds.coverage:.2f})", "planet")
            return self.clouds.apply_to_planet(image)
        except Exception as e:
            error_msg = f"Failed to apply clouds: {str(e)}"
            logger.error(error_msg, "planet", exc_info=True)
            raise FeatureError(message=error_msg, feature="clouds") from e


    def _apply_rings(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a Saturn-like ring system with multiple concentric rings of varying widths and opacities.

        Args:
            base_image: Base planet image (may include atmosphere)

        Returns:
            Planet image with Saturn-like rings

        Raises:
            FeatureError: If there is an error applying rings
        """
        from cosmos_generator.utils.exceptions import FeatureError

        start_time = time.time()
        try:
            # Get the ring color for this planet type
            ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)

            # IMPORTANT: Pass the original planet size to the rings generator
            # This ensures rings are based on the actual planet size, not the image with atmosphere
            original_planet_size = self.size

            # Get ring parameters from kwargs if provided
            rings_complexity = getattr(self, 'rings_complexity', None)
            rings_tilt = getattr(self, 'rings_tilt', None)

            # Apply rings using the Rings class
            result = self.rings_generator.apply_rings(
                planet_image=base_image,
                planet_type=self.PLANET_TYPE,
                color=ring_color,
                original_planet_size=original_planet_size,  # Pass the original planet size
                tilt=rings_tilt,  # Pass the tilt parameter if provided
                detail=1.0,  # Default detail level
                ring_complexity=rings_complexity  # Pass the complexity parameter if provided
            )

            # Get ring complexity and count from the rings generator
            ring_complexity = rings_complexity if rings_complexity is not None else self.rng.randint(1, 3)  # Use provided complexity or random
            ring_count = len(self.rings_generator.last_ring_definitions) if hasattr(self.rings_generator, 'last_ring_definitions') else 0
            ring_width_factor = 3.0  # Standard factor used in Rings class

            duration_ms = (time.time() - start_time) * 1000
            # Log details about the rings
            logger.log_step("apply_rings", duration_ms, f"Complexity: {ring_complexity}, Rings: {ring_count}, Factor: {ring_width_factor}")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Failed to apply rings: {str(e)}"
            logger.log_step("apply_rings", duration_ms, f"Error: {str(e)}")
            logger.error(error_msg, "planet", exc_info=True)
            raise FeatureError(message=error_msg, feature="rings") from e