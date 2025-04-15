"""
Container management for celestial bodies.
"""
from typing import Any
from PIL import Image, ImageDraw

from cosmos_generator.utils.image_utils import rotate_image


class Container:
    """
    Manages view perspective and rotation for celestial bodies.
    Proporciona una vista fija para cada tipo de planeta.
    """

    def __init__(self, width: int = 512, height: int = 512):
        """
        Initialize a container with fixed dimensions.

        Args:
            width: Container width in pixels (fixed at 512)
            height: Container height in pixels (fixed at 512)
        """
        # Forzar tamaño fijo de 512x512
        self.width = 512
        self.height = 512
        self.rotation = 0.0
        self.content = None

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

    def rotate(self, angle: float) -> None:
        """
        Rotate by the specified angle.

        Args:
            angle: Rotation angle in degrees
        """
        self.rotation = (self.rotation + angle) % 360

    def reset(self) -> None:
        """
        Reset the container to its initial state.
        """
        self.rotation = 0.0

    def render(self) -> Image.Image:
        """
        Render the content with the current container settings.

        Genera la imagen del planeta con una vista fija según el tipo:
        - Planetas con anillos: Vista equivalente a zoom 0.75 en el viewport anterior
        - Planetas sin anillos: Vista completa

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
            content_image = rotate_image(content_image, self.rotation)

        # Obtener el tamaño de la imagen del contenido
        content_width, content_height = content_image.size

        # Calcular el centro de la imagen
        center_x = content_width // 2
        center_y = content_height // 2

        # Determinar el tipo de contenido y aplicar la vista fija adecuada
        if has_rings:
            # Para planetas con anillos, usamos un zoom fijo de 0.75
            # para acercar un poco más y mostrar mejor los anillos
            fixed_zoom = 0.75

            # Para planetas con anillos, queremos un recorte que muestre una buena parte de los anillos
            # pero que también permita ver el planeta con suficiente detalle
            #
            # Un zoom de 0.75 significa que queremos ver el 75% del tamaño total
            # Esto nos da un buen equilibrio entre mostrar los anillos y ver el planeta con detalle
            crop_size = int(min(content_width, content_height) * fixed_zoom)
        else:
            # Para planetas sin anillos, mostramos la vista completa
            # pero asegurándonos de que sea un recorte cuadrado
            crop_size = min(content_width, content_height)

        # Calcular las coordenadas de recorte, centradas en el planeta
        crop_left = center_x - crop_size // 2
        crop_top = center_y - crop_size // 2
        crop_right = crop_left + crop_size
        crop_bottom = crop_top + crop_size

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

        # Recortar la imagen
        cropped_image = content_image.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Redimensionar al tamaño del container (512x512)
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
