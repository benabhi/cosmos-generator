"""
Container management for celestial bodies.

Esta clase proporciona un contenedor para mostrar cuerpos celestes con un tamaño fijo de 512x512 píxeles.
Maneja de forma diferente los planetas con anillos y sin anillos, asegurando que se muestren correctamente
y con las proporciones adecuadas.
"""
from typing import Any, Optional
from PIL import Image, ImageDraw

import config
from cosmos_generator.utils.image_utils import rotate_image
from cosmos_generator.utils.logger import logger
from cosmos_generator.core.interfaces import ContainerInterface


class Container(ContainerInterface):
    """
    Manages view perspective, zoom and rotation for celestial bodies.

    Esta clase proporciona un contenedor de tamaño fijo (512x512 píxeles) para mostrar
    cuerpos celestes. Aplica una vista adaptada para cada tipo de planeta:
    - Planetas con anillos: Zoom por defecto de 0.5 para mostrar más de los anillos
    - Planetas sin anillos: Zoom por defecto de 1.1 para mostrar el planeta con más detalle

    Permite personalizar el nivel de zoom en un rango de 0.0 (muy lejos) a 1.0 (muy cerca).
    También permite rotar el contenido, lo que es útil para visualizar diferentes ángulos.
    """

    def __init__(self, zoom_level=None):
        """
        Initialize a container with fixed dimensions (defined in config.PLANET_SIZE).

        Args:
            zoom_level: Optional custom zoom level (0.0 to 1.0)
                        0.0 = far away (planeta pequeño)
                        1.0 = very close (planeta grande, ocupa todo el contenedor)
                        0.9 = default for planets without rings (grande con algo de padding)
                        0.7 = default for planets with rings
                        None = use default based on planet type
        """
        # Tamaño fijo definido en la configuración
        self.width = config.PLANET_SIZE
        self.height = config.PLANET_SIZE
        self.rotation = 0.0
        self.content = None

        # Ensure zoom_level is a float if provided
        if zoom_level is not None:
            try:
                zoom_value = float(zoom_level)
                # Ensure zoom level is within valid range
                self.zoom_level = max(config.CONTAINER_DEFAULT_SETTINGS["zoom_min"],
                                     min(config.CONTAINER_DEFAULT_SETTINGS["zoom_max"], zoom_value))
                logger.info(f"Container initialized with zoom level: {self.zoom_level}", "container")
            except (ValueError, TypeError) as e:
                logger.error(f"Error setting zoom level: {e}", "container")
                self.zoom_level = None
        else:
            self.zoom_level = None
            logger.info("Container initialized with default zoom level", "container")

    def set_content(self, content: Any) -> None:
        """
        Set the content to be displayed in the container.

        Args:
            content: Content to display (must have a render() method)
        """
        self.content = content

    def set_rotation(self, angle: float) -> None:
        """
        Set the rotation angle.

        Args:
            angle: Rotation angle in degrees
        """
        self.rotation = angle % 360
        logger.info(f"Rotation set to: {self.rotation} degrees", "container")

    def rotate(self, angle: float) -> None:
        """
        Rotate by the specified angle.

        Args:
            angle: Rotation angle in degrees
        """
        self.rotation = (self.rotation + angle) % 360
        logger.info(f"Rotated by {angle} degrees, new rotation: {self.rotation} degrees", "container")

    def set_zoom(self, zoom_level: float) -> None:
        """
        Set the zoom level.

        Args:
            zoom_level: Zoom level (0.0 to 1.0)
                        0.0 = far away (planeta pequeño)
                        1.0 = very close (planeta grande, ocupa todo el contenedor)
                        0.9 = default for planets without rings (grande con algo de padding)
                        0.7 = default for planets with rings

        Note:
            El zoom no afecta la generación del planeta ni la relación entre sus componentes.
            Solo determina cuánto de la imagen completa se muestra en el contenedor.
            Un valor más bajo hace que el planeta se vea más pequeño (más lejos).
            Un valor más alto hace que el planeta se vea más grande (más cerca).
        """
        try:
            # Convert to float if not already
            zoom_level = float(zoom_level)
            # Ensure zoom level is within valid range
            self.zoom_level = max(config.CONTAINER_DEFAULT_SETTINGS["zoom_min"],
                                 min(config.CONTAINER_DEFAULT_SETTINGS["zoom_max"], zoom_level))
            logger.info(f"Zoom level set to: {self.zoom_level}", "container")
        except (ValueError, TypeError) as e:
            logger.error(f"Error setting zoom level: {e}", "container")
            # Keep current zoom level


    def render(self) -> Image.Image:
        """
        Render the content with the current container settings.

        Genera la imagen del planeta con un nivel de zoom adaptado:
        - Si se especifica un nivel de zoom personalizado (0.0 a 2.0), se usa ese valor
        - Si no, se usa el zoom por defecto según el tipo de planeta:
          - Planetas con anillos: Zoom de 0.5 para mostrar más de los anillos
          - Planetas sin anillos: Zoom de 1.1 para mostrar el planeta con más detalle

        El proceso consiste en:
        1. Obtener la imagen del contenido
        2. Aplicar rotación si es necesario
        3. Calcular el factor de zoom y recortar un área cuadrada
        4. Redimensionar el recorte a 512x512 píxeles

        La imagen final siempre será de 512x512 píxeles.

        Returns:
            Rendered image (512x512 pixels)
        """
        if self.content is None:
            # Create an empty image if no content is set
            image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "No content set", fill=(255, 255, 255))
            return image

        # Detectar si el contenido es un planeta con anillos
        has_rings = False
        if hasattr(self.content, "has_rings"):
            has_rings = self.content.has_rings

        # Get the content image
        if hasattr(self.content, "render"):
            content_image = self.content.render()
        elif hasattr(self.content, "image"):
            content_image = self.content.image
        elif isinstance(self.content, Image.Image):
            content_image = self.content
        else:
            raise ValueError("Content must have a render() method, an image attribute, or be a PIL Image")

        # Aplicar rotación si es necesario
        if self.rotation != 0.0:
            logger.info(f"Applying rotation of {self.rotation} degrees during rendering", "container")
            content_image = rotate_image(content_image, self.rotation)

        # Obtener el tamaño de la imagen del contenido
        content_width, content_height = content_image.size

        # Log para depuración - tamaño de la imagen original
        logger.info(f"Original image size: {content_width}x{content_height}", "container")

        # Solo para planetas sin anillos, necesitamos crear un canvas más grande para permitir zoom out
        # Para planetas con anillos, la imagen original ya tiene suficiente espacio alrededor
        # EXCEPTO cuando el zoom es 1.0 para planetas sin anillos, donde queremos que el planeta ocupe todo el canvas
        if not has_rings and (self.zoom_level is None or self.zoom_level != 1.0):
            # Usamos un canvas 4 veces más grande que la imagen original
            # Esto nos dará suficiente espacio para todos los niveles de zoom
            # y evitará que el planeta choque contra los bordes en zoom = 0.9
            canvas_multiplier = 4.0
            canvas_size = int(max(content_width, content_height) * canvas_multiplier)

            # Aseguramos que el canvas sea al menos del tamaño de la imagen original
            canvas_size = max(canvas_size, max(content_width, content_height))

            # Creamos el canvas grande con fondo transparente
            large_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

            # Calculamos la posición para centrar la imagen original en el canvas grande
            paste_x = (canvas_size - content_width) // 2
            paste_y = (canvas_size - content_height) // 2

            # Pegamos la imagen original en el centro del canvas grande
            large_canvas.paste(content_image, (paste_x, paste_y),
                              content_image if content_image.mode == "RGBA" else None)

            # Reemplazamos la imagen original con el canvas grande
            content_image = large_canvas
            content_width, content_height = content_image.size
            logger.info(f"Created larger canvas: {content_width}x{content_height} (multiplier: {canvas_multiplier:.2f})", "container")

        # Calcular el centro de la imagen
        center_x = content_width // 2
        center_y = content_height // 2

        # IMPORTANTE: El zoom se aplica después de generar todos los componentes del planeta
        # para asegurar que las proporciones entre ellos (anillos, atmósfera, etc.) se mantengan constantes.
        # El zoom solo determina cuánto de la imagen completa se muestra, no afecta la generación.

        # Nota: Ya no usamos los factores de recorte de la configuración
        # Ahora calculamos el tamaño del recorte basado en el tamaño del planeta y el factor de escala

        # Determinar el nivel de zoom a aplicar
        if self.zoom_level is not None:
            # Si hay un nivel de zoom personalizado, lo usamos
            zoom_level = self.zoom_level
            logger.info(f"Applying custom zoom level: {zoom_level}", "container")
        else:
            # Si no hay zoom personalizado, usamos los valores por defecto según el tipo de planeta
            if has_rings:
                # Para planetas con anillos, usamos un zoom menor para mostrar más de los anillos
                zoom_level = config.CONTAINER_DEFAULT_SETTINGS["default_zoom_with_rings"]
                logger.debug(f"Using default zoom for planet with rings: {zoom_level}", "container")
            else:
                # Para planetas sin anillos, usamos un zoom mayor para mostrar el planeta con más detalle
                zoom_level = config.CONTAINER_DEFAULT_SETTINGS["default_zoom_without_rings"]
                logger.debug(f"Using default zoom for planet without rings: {zoom_level}", "container")

        # ENFOQUE COMPLETAMENTE NUEVO PARA EL ZOOM

        # Determinamos el tamaño del planeta (aproximadamente)
        if not has_rings:
            # Para planetas sin anillos
            if self.zoom_level is not None and self.zoom_level == 1.0:
                # Para zoom = 1.0, usamos el tamaño exacto de la imagen original
                planet_size = min(content_width, content_height)
                logger.info(f"Using exact image size for zoom 1.0: {planet_size}", "container")
            else:
                # Para otros niveles de zoom, asumimos que el planeta ocupa aproximadamente el 95% de la imagen original
                planet_size = int(min(532, 532) * 0.95)  # Usamos el tamaño original conocido (532x532)
        else:
            # Para planetas con anillos
            # El planeta real (sin anillos) ocupa aproximadamente el 30% del tamaño de la imagen
            # Los anillos ocupan el resto (aproximadamente hasta el 90% del tamaño de la imagen)
            planet_only_size = int(min(content_width, content_height) * 0.3)  # Solo el planeta
            planet_with_rings_size = int(min(content_width, content_height) * 0.9)  # Planeta con anillos

            logger.info(f"Planet only size: {planet_only_size}, Planet with rings: {planet_with_rings_size}", "container")

            # Usamos el tamaño del planeta sin anillos como referencia
            planet_size = planet_only_size

        # Definimos los límites de tamaño de recorte
        # - Para zoom = 0.0 (muy lejos): recorte muy grande (3 veces el tamaño del planeta)
        # - Para zoom = 0.9 (cerca): recorte ligeramente mayor que el tamaño del planeta (1.1x)
        # - Para zoom = 1.0 (muy cerca): recorte exactamente del tamaño del planeta

        # Definimos los límites de tamaño de recorte según el tipo de planeta
        if not has_rings:
            # Para planetas sin anillos
            if self.zoom_level == 1.0:
                # Para zoom = 1.0, usamos un tamaño ligeramente menor que la imagen original
                # para asegurarnos de que el planeta esté completamente visible
                min_crop_size = int(planet_size * 0.98)  # 98% del tamaño de la imagen original
                logger.info(f"Using slightly smaller crop size for zoom 1.0: {min_crop_size}", "container")
            else:
                # Para otros niveles de zoom, usamos el tamaño del planeta
                min_crop_size = planet_size

            # Para zoom = 0.0, el recorte es del tamaño máximo disponible
            max_crop_size = min(content_width, content_height)
        else:
            # Para planetas con anillos
            # Para zoom = 1.0, queremos mostrar solo el planeta (sin anillos)
            if self.zoom_level is not None and self.zoom_level == 1.0:
                # Usamos un tamaño ligeramente mayor que el planeta para evitar recortar los bordes
                min_crop_size = int(planet_only_size * 1.2)  # 20% más grande que el planeta
                logger.info(f"Zoom 1.0 for planet with rings: showing only the planet with padding (crop size: {min_crop_size})", "container")
            else:
                # Para zoom = 0.0, queremos mostrar el planeta completo con anillos
                # Para valores intermedios, interpolamos entre el tamaño del planeta con anillos y sin anillos
                min_crop_size = planet_only_size

            # Para zoom = 0.0, el recorte muestra todo el planeta con anillos
            max_crop_size = planet_with_rings_size

            logger.info(f"Crop size limits for planet with rings: min={min_crop_size}, max={max_crop_size}", "container")

        # Calculamos el tamaño del recorte basado en el nivel de zoom
        if self.zoom_level is not None:
            # Si hay un nivel de zoom personalizado, lo usamos
            zoom_level = self.zoom_level
        else:
            # Si no hay zoom personalizado, usamos los valores por defecto según el tipo de planeta
            if has_rings:
                zoom_level = config.CONTAINER_DEFAULT_SETTINGS["default_zoom_with_rings"]
            else:
                zoom_level = config.CONTAINER_DEFAULT_SETTINGS["default_zoom_without_rings"]

        # Interpolación lineal entre max_crop_size y min_crop_size basada en zoom_level
        # - zoom_level = 0.0 -> crop_size = max_crop_size (planeta pequeño/lejos)
        # - zoom_level = 1.0 -> crop_size = min_crop_size (planeta grande/cerca)
        crop_range = max_crop_size - min_crop_size
        crop_size = max_crop_size - int(zoom_level * crop_range)

        logger.info(f"Calculated crop size for zoom {zoom_level}: {crop_size}", "container")

        # Aseguramos que el tamaño del recorte esté dentro de los límites
        crop_size = max(min_crop_size, min(crop_size, max_crop_size))

        # Log para depuración
        logger.info(f"Zoom: {zoom_level}, Planet size: {planet_size}, Crop size: {crop_size}, "
                   f"Min crop: {min_crop_size}, Max crop: {max_crop_size}", "container")

        # Calcular las coordenadas de recorte, centradas en el planeta
        crop_left = center_x - crop_size // 2
        crop_top = center_y - crop_size // 2
        crop_right = crop_left + crop_size
        crop_bottom = crop_top + crop_size

        # Log para depuración - coordenadas de recorte
        logger.info(f"Crop coordinates: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}", "container")
        logger.info(f"Center coordinates: x={center_x}, y={center_y}", "container")

        # Asegurarse de que el área de recorte esté dentro de los límites de la imagen
        # y mantener el tamaño del recorte constante para preservar la relación de aspecto
        if crop_left < 0:
            crop_right = crop_size  # Mantener el ancho constante
            crop_left = 0

        if crop_top < 0:
            crop_bottom = crop_size  # Mantener el alto constante
            crop_top = 0

        if crop_right > content_width:
            crop_left = max(0, content_width - crop_size)  # Mantener el ancho constante
            crop_right = content_width

        if crop_bottom > content_height:
            crop_top = max(0, content_height - crop_size)  # Mantener el alto constante
            crop_bottom = content_height

        # Verificar si el tamaño del recorte es menor que el esperado (puede ocurrir si la imagen es pequeña)
        actual_width = crop_right - crop_left
        actual_height = crop_bottom - crop_top

        if actual_width < crop_size or actual_height < crop_size:
            # Si la imagen es más pequeña que el tamaño de recorte deseado,
            # usar la imagen completa y dejar que el redimensionamiento se encargue
            crop_left = 0
            crop_top = 0
            crop_right = content_width
            crop_bottom = content_height

        # Recortar la imagen usando las coordenadas calculadas
        # Esto nos da un recorte cuadrado centrado en el planeta
        cropped_image = content_image.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Redimensionar al tamaño fijo del container (512x512)
        # Usamos el algoritmo LANCZOS para obtener la mejor calidad de imagen
        container_image = cropped_image.resize((self.width, self.height), Image.LANCZOS)

        return container_image

    def export(self, filename: str) -> None:
        """
        Export the current container to an image file.

        Args:
            filename: Output filename
        """
        image = self.render()
        image.save(filename)
