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
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from cosmos_generator.celestial_bodies.base import AbstractCelestialBody
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

    def render(self) -> Image.Image:
        """
        Render the planet with the common generation flow.

        Returns:
            PIL Image of the planet
        """
        # Generate base texture
        texture = self.generate_texture()

        # Save the base texture for debugging
        debug_dir = os.path.join("output", "debug", "textures", "terrain")
        os.makedirs(debug_dir, exist_ok=True)
        texture.save(os.path.join(debug_dir, f"{self.seed}.png"))

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

        # The order of applying features is important:
        # 1. First apply atmosphere if enabled (before anything else)
        if self.has_atmosphere:
            result = self._apply_atmosphere(result)

        # 2. Then apply clouds if enabled
        if self.has_clouds:
            result = self._apply_clouds(result)

        # 3. Finally apply rings if enabled
        if self.has_rings:
            result = self._apply_rings(result)

        return result

    def _apply_atmosphere(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a simple atmospheric glow to the planet with a fine light line around the edge.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with atmosphere
        """
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
            atmosphere_padding = int(size * 0.15)  # 15% padding for planets with rings
        else:
            atmosphere_padding = int(size * 0.02)  # 2% padding for planets without rings (drastically reduced)
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
            halo_width = 2  # Normal width for planets without rings

        # Draw the halo as a thin ring
        halo_draw.ellipse(
            (center - halo_radius, center - halo_radius,
             center + halo_radius, center + halo_radius),
            outline=halo_color, width=halo_width
        )

        # Apply a very small blur to soften the halo slightly
        # For planets with rings, use less blur to keep the halo more defined
        blur_amount = 0.5 if self.has_rings else 1
        halo = halo.filter(ImageFilter.GaussianBlur(blur_amount))

        # Composite the halo onto the result
        result = Image.alpha_composite(result, halo)

        return result

    def _apply_clouds(self, base_image: Image.Image) -> Image.Image:
        """
        Apply cloud layer to the planet.

        Args:
            base_image: Base planet image

        Returns:
            Planet image with clouds
        """
        # Get the size of the planet image (may include atmosphere)
        size = base_image.width

        # COMPLETELY REDESIGNED CLOUD GENERATION FOR MORE REALISTIC CLOUDS
        # Base cloud layer - large, fluffy formations with very low frequency
        base_cloud_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.2, 0.3),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 4, 0.7, 2.0, 1.8)  # Lower frequency (1.8) for larger, fluffier clouds
            )
        )

        # Detail layer - adds fine texture and fluffiness with higher frequency
        detail_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.4, 0.5),
                lambda dx, dy: self.noise_gen.fractal_simplex(dx, dy, 6, 0.6, 2.2, 6.0)  # Higher frequency (6.0) for fine details
            )
        )

        # Wispy edges layer - creates soft, wispy cloud edges
        wispy_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.domain_warp(
                x, y,
                lambda dx, dy: self.noise_gen.simplex_warp(dx, dy, 0.3, 0.4),
                lambda dx, dy: self.noise_gen.ridged_simplex(dx, dy, 5, 0.5, 2.0, 4.0)  # Ridge noise for wispy edges
            )
        )

        # Puffy layer - adds puffy, cumulus-like structures using ridged noise
        puffy_noise = self.noise_gen.generate_noise_map(
            self.size, self.size,
            lambda x, y: self.noise_gen.ridged_simplex(x, y, 3, 0.8, 2.0, 3.0)  # Ridged noise for puffy structures
        )

        # Combine the noise layers to create realistic cloud formations
        # Create a new array for the combined noise
        combined_noise = np.zeros((self.size, self.size), dtype=np.float32)

        for y in range(self.size):
            for x in range(self.size):
                # Base shape (40%) - large cloud formations
                base = base_cloud_noise[y, x]
                # Add detail (20%) - fine texture
                detail = detail_noise[y, x]
                # Add wispy edges (20%) - soft, natural cloud edges
                wispy = wispy_noise[y, x]
                # Add puffy structure (20%) - puffy, cumulus-like appearance
                puffy = puffy_noise[y, x]

                # Combine with weights for a more realistic cloud appearance
                combined = base * 0.4 + detail * 0.2 + wispy * 0.2 + puffy * 0.2

                # Apply a subtle curve to enhance cloud definition
                if combined > 0.4 and combined < 0.6:
                    # Enhance the mid-range to create more defined edges
                    factor = (combined - 0.4) / 0.2  # 0 to 1 in the 0.4-0.6 range
                    combined = 0.4 + factor * 0.25  # Steeper transition

                # Store the result
                combined_noise[y, x] = combined

        # Use the combined noise for cloud generation
        cloud_noise = combined_noise

        # Create the cloud mask
        cloud_mask = Image.new("L", (self.size, self.size), 0)
        cloud_data = cloud_mask.load()

        # Adjust threshold to increase cloud coverage
        # Lower threshold = more clouds
        cloud_threshold = 0.45 - (self.cloud_coverage * 0.35)  # More aggressive adjustment

        # Fill the cloud mask with a sophisticated approach for realistic, fluffy clouds
        for y in range(self.size):
            for x in range(self.size):
                # Use a softer threshold approach for more natural cloud edges
                value = cloud_noise[y, x]

                # Instead of a hard threshold, use a smooth transition
                # This creates more natural, feathered cloud edges
                if value > cloud_threshold - 0.1:  # Start transition 0.1 below threshold
                    if value < cloud_threshold:  # Soft edge zone
                        # Gradual transition from 0 to 50 opacity in the edge zone
                        edge_factor = (value - (cloud_threshold - 0.1)) / 0.1  # 0 to 1
                        alpha = int(50 * edge_factor)  # 0 to 50 opacity for very soft edges
                    else:  # Main cloud zone
                        # Calculate normalized distance from threshold
                        normalized = (value - cloud_threshold) / (1.0 - cloud_threshold)

                        # Apply a sophisticated curve for natural cloud density
                        # This creates very fluffy, natural-looking clouds
                        if normalized < 0.3:  # Outer cloud area
                            # Gradual increase from edge to main cloud
                            curved = 0.2 + (normalized * 2.0)  # Steeper increase for more defined edges
                        elif normalized < 0.7:  # Mid-cloud area
                            # Moderate density for most of the cloud
                            curved = 0.8 + (normalized - 0.3) * 0.5  # Slower increase in the middle
                        else:  # Dense cloud centers
                            # High density for cloud centers
                            curved = 1.0 + (normalized - 0.7) * 0.5  # Boost for dense centers

                        # Convert to alpha value with a minimum of 50 for visibility
                        alpha = int(255 * curved)

                    # Apply the calculated alpha
                    cloud_data[x, y] = min(255, alpha)

        # Apply circular mask to the clouds
        circle_mask = image_utils.create_circle_mask(self.size)
        cloud_mask = ImageChops.multiply(cloud_mask, circle_mask)

        # Create slightly off-white clouds for more natural appearance
        # Pure white can look too harsh - a very slight cream tint looks more natural
        cloud_color = (255, 252, 248, 255)  # Slightly off-white with maximum opacity

        # Create the cloud layer
        clouds = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(clouds)
        draw.ellipse((0, 0, self.size-1, self.size-1), fill=cloud_color)

        # Apply the cloud mask
        clouds.putalpha(cloud_mask)

        # Save both cloud mask and enhanced cloud texture in the same location
        clouds_dir = os.path.join("output", "debug", "textures", "clouds")
        os.makedirs(clouds_dir, exist_ok=True)

        # Save the original cloud mask
        cloud_mask.save(os.path.join(clouds_dir, f"mask_{self.seed}.png"))

        # Save a copy of the cloud mask with better visibility for reference
        enhanced_mask = cloud_mask.copy()
        # Enhance contrast for better visibility when viewed directly
        for y in range(self.size):
            for x in range(self.size):
                pixel = enhanced_mask.getpixel((x, y))
                if pixel > 0:  # If there's any cloud at all
                    # Boost low values for better visibility
                    enhanced_mask.putpixel((x, y), min(255, pixel + 50))
        enhanced_mask.save(os.path.join(clouds_dir, f"cloud_{self.seed}.png"))

        # Create a normal map from the cloud noise for 3D lighting effect
        # Use the original cloud_noise directly since it's already in the right format
        # We don't need to create a separate height map

        # Enhanced lighting for more realistic cloud appearance
        lit_clouds = lighting_utils.apply_directional_light(
            clouds,
            lighting_utils.calculate_normal_map(cloud_noise, 3.0),  # Use cloud_noise directly for height map
            light_direction=(
                -math.cos(math.radians(self.light_angle)),
                -math.sin(math.radians(self.light_angle)),
                1.0
            ),
            ambient=0.6,  # Balanced ambient light
            diffuse=0.9,  # Strong diffuse for good cloud definition
            specular=0.3   # Moderate specular for highlights on cloud tops
        )

        # Add a very subtle blur to soften the edges slightly
        # This creates a more natural, fluffy appearance
        lit_clouds = lit_clouds.filter(ImageFilter.GaussianBlur(0.8))

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

        return result

    def _apply_rings(self, base_image: Image.Image) -> Image.Image:
        """
        Apply a Saturn-like ring system with multiple concentric rings of varying widths and opacities.

        Args:
            base_image: Base planet image (may include atmosphere)

        Returns:
            Planet image with Saturn-like rings
        """
        # Asegurarse de que la imagen tiene canal alfa
        if base_image.mode != "RGBA":
            base_image = base_image.convert("RGBA")

        # Obtener el color base para los anillos
        base_ring_color = self.color_palette.get_ring_color(self.PLANET_TYPE)

        # IMPORTANTE: Usar el tamaño original del planeta, no el tamaño de la imagen con atmósfera
        # Esto asegura que los anillos se basen en el diámetro del planeta, no en la atmósfera
        original_planet_size = self.size
        planet_radius = original_planet_size // 2

        # Obtener el tamaño actual de la imagen (puede incluir atmósfera)
        current_image_size = base_image.width

        # Crear un canvas más grande para los anillos (3.0 veces el tamaño del planeta original)
        ring_width_factor = 3.0
        canvas_size = int(original_planet_size * ring_width_factor)
        result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

        # Posición central del canvas
        center_x, center_y = canvas_size // 2, canvas_size // 2

        # Calcular el offset para centrar la imagen actual (con atmósfera) en el canvas
        planet_offset = (canvas_size - current_image_size) // 2

        # Factor de compresión vertical para los anillos
        vertical_factor = 0.3  # Más pronunciado para mejor efecto visual

        # Determinar complejidad del sistema de anillos (1-3)
        ring_complexity = self.rng.randint(1, 3)

        # Crear capa para el planeta (para máscaras)
        planet_layer = Image.new("1", (canvas_size, canvas_size), 0)
        draw_planet = ImageDraw.Draw(planet_layer)
        draw_planet.ellipse(
            [center_x - planet_radius, center_y - planet_radius,
            center_x + planet_radius, center_y + planet_radius],
            fill=1
        )

        # Crear máscara para la mitad frontal
        front_mask = Image.new("L", (canvas_size, canvas_size), 0)
        draw_front = ImageDraw.Draw(front_mask)
        draw_front.rectangle([0, center_y, canvas_size, canvas_size], fill=255)

        # Definiciones de anillos según la complejidad
        ring_definitions = []

        if ring_complexity == 1:
            # Sistema simple (3-4 anillos)
            ring_definitions = [
                (1.2, 1.35, 0.95, 0.8),  # Anillo interno
                (1.4, 1.6, 1.0, 0.95),   # Anillo medio brillante
                (1.65, 1.8, 0.9, 0.85),  # Anillo externo
            ]
            # Quizás añadir un anillo más
            if self.rng.random() > 0.5:
                ring_definitions.append((1.9, 2.0, 0.8, 0.7))

        elif ring_complexity == 2:
            # Sistema intermedio (5-7 anillos)
            ring_definitions = [
                (1.2, 1.3, 0.9, 0.75),    # Anillo interno (C)
                (1.35, 1.45, 0.95, 0.9),  # Anillo B interno
                (1.5, 1.65, 1.0, 0.95),   # Anillo B medio (brillante)
                (1.7, 1.85, 0.9, 0.85),   # Anillo A interno
                (1.9, 2.05, 0.85, 0.8),   # Anillo A externo
            ]
            # Quizás añadir anillos adicionales
            if self.rng.random() > 0.4:
                ring_definitions.append((2.1, 2.15, 0.75, 0.7))

        else:
            # Sistema complejo (tipo Saturno, 8+ anillos)
            ring_definitions = [
                (1.2, 1.25, 0.8, 0.7),    # Anillo D (muy fino)
                (1.28, 1.38, 0.9, 0.75),  # Anillo C
                (1.4, 1.48, 0.95, 0.9),   # Anillo B interno
                (1.5, 1.6, 1.0, 0.95),    # Anillo B medio (brillante)
                (1.63, 1.68, 0.9, 0.85),  # Anillo B externo
                (1.7, 1.72, 0.7, 0.6),    # División Cassini
                (1.74, 1.85, 0.95, 0.9),  # Anillo A interno
                (1.86, 1.88, 0.7, 0.65),  # Hueco de Encke
                (1.9, 2.0, 0.9, 0.85),    # Anillo A externo
                (2.1, 2.12, 0.75, 0.7)    # Anillo F (fino, aislado)
            ]

        # Añadir anillos finos aleatorios para variedad
        num_extra_rings = 0
        if ring_complexity == 1:
            num_extra_rings = self.rng.randint(0, 1)
        elif ring_complexity == 2:
            num_extra_rings = self.rng.randint(1, 2)
        else:
            num_extra_rings = self.rng.randint(2, 4)

        for _ in range(num_extra_rings):
            pos = 1.25 + 0.8 * self.rng.random()
            thickness = 0.005 + 0.01 * self.rng.random()
            opacity = 0.7 + 0.3 * self.rng.random()
            brightness = 0.7 + 0.3 * self.rng.random()
            ring_definitions.append((pos, pos + thickness, opacity, brightness))

        # Ordenar los anillos por radio interno
        ring_definitions.sort(key=lambda x: x[0])

        # Procesar cada anillo - PRIMERO LOS ARCOS TRASEROS
        for inner_factor, outer_factor, opacity, brightness in ring_definitions:
            # Calcular dimensiones
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)

            # Variar ligeramente el color
            r, g, b, a = base_ring_color
            color_var = 0.1

            # Color con brillo, opacidad y variación
            ring_color = (
                max(0, min(255, int(r * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(g * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(b * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(a * opacity)))
            )

            # Crear capa para el anillo
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Dibujar elipse externa
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry,
                center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Dibujar elipse interna (agujero)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry,
                center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # Arcos externos: diferencia entre anillo y planeta
            ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

            # Color más oscuro para los arcos (detrás del planeta)
            shadow_factor = 0.6
            arcs_color = (
                int(ring_color[0] * shadow_factor),
                int(ring_color[1] * shadow_factor),
                int(ring_color[2] * shadow_factor),
                ring_color[3]
            )

            # Crear arcos coloreados
            ring_arcs_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_arcs_colored.paste(arcs_color, mask=ring_arcs)

            # Añadir arcos (detrás del planeta)
            result.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)

        # Añadir el planeta sobre los anillos traseros
        result.paste(base_image, (planet_offset, planet_offset), base_image)

        # AHORA AÑADIR BANDAS FRONTALES
        for inner_factor, outer_factor, opacity, brightness in ring_definitions:
            # Calcular dimensiones
            outer_rx = int(planet_radius * outer_factor)
            outer_ry = int(outer_rx * vertical_factor)

            inner_rx = int(planet_radius * inner_factor)
            inner_ry = int(inner_rx * vertical_factor)

            # Variar ligeramente el color
            r, g, b, a = base_ring_color
            color_var = 0.1

            # Color con brillo, opacidad y variación
            ring_color = (
                max(0, min(255, int(r * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(g * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(b * brightness * (1 + (self.rng.random() - 0.5) * color_var)))),
                max(0, min(255, int(a * opacity)))
            )

            # Crear capa para el anillo
            ring_layer = Image.new("1", (canvas_size, canvas_size), 0)
            draw_ring = ImageDraw.Draw(ring_layer)

            # Dibujar elipse externa
            draw_ring.ellipse(
                [center_x - outer_rx, center_y - outer_ry,
                center_x + outer_rx, center_y + outer_ry],
                fill=1
            )

            # Dibujar elipse interna (agujero)
            draw_ring.ellipse(
                [center_x - inner_rx, center_y - inner_ry,
                center_x + inner_rx, center_y + inner_ry],
                fill=0
            )

            # Intersección entre anillo y planeta
            ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

            # La banda frontal es solo la mitad frontal de la intersección
            ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

            # Crear banda frontal coloreada
            ring_front_colored = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            ring_front_colored.paste(ring_color, mask=ring_front)

            # Añadir la banda frontal sobre el planeta
            result.paste(ring_front_colored, (0, 0), ring_front_colored)

        # IMPORTANTE: NO redimensionar el resultado, devolver imagen completa con anillos
        return result