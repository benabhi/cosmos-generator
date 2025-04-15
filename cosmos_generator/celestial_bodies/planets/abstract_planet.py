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

        # Create a larger canvas for the atmosphere (30% larger than the planet)
        atmosphere_padding = int(size * 0.15)  # 15% padding on each side
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
        blur_radius = atmosphere_padding // 3
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
        halo_color = (r, g, b, 255)  # Full opacity for the halo

        # Draw the halo as a thin ring
        halo_draw.ellipse(
            (center - halo_radius, center - halo_radius,
             center + halo_radius, center + halo_radius),
            outline=halo_color, width=2
        )

        # Apply a very small blur to soften the halo slightly
        halo = halo.filter(ImageFilter.GaussianBlur(1))

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