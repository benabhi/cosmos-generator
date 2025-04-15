"""
Viewport management for celestial bodies.
"""
from typing import Tuple, Optional, Any, Union
import math
from PIL import Image, ImageDraw

from cosmos_generator.utils.image_utils import rotate_image, resize_image


class Viewport:
    """
    Manages view perspective, zoom, pan, and rotation for celestial bodies.
    """

    def __init__(self, width: int = 512, height: int = 512, initial_zoom: float = 1.0):
        """
        Initialize a viewport with the specified dimensions and zoom.

        Args:
            width: Viewport width in pixels (fixed at 512)
            height: Viewport height in pixels (fixed at 512)
            initial_zoom: Initial zoom factor (between 0.3 and 1.0)
        """
        # Forzar tamaño fijo de 512x512
        self.width = 512
        self.height = 512
        # Limitar zoom entre 0.3 y 1.0
        self.zoom = max(0.3, min(1.0, initial_zoom))
        self.rotation = 0.0
        self.pan_x = 0
        self.pan_y = 0
        self.content = None

    def set_content(self, content: Any) -> None:
        """
        Set the content to be displayed in the viewport.

        Args:
            content: Content to display (must have a render() method)
        """
        self.content = content

    def set_zoom(self, zoom: float) -> None:
        """
        Set the zoom factor.

        Args:
            zoom: Zoom factor (entre 0.3 y 1.0)
        """
        self.zoom = max(0.3, min(1.0, zoom))

    def zoom_in(self, factor: float = 1.2) -> None:
        """
        Zoom in by the specified factor.

        Args:
            factor: Zoom factor
        """
        self.zoom *= factor
        self.zoom = min(1.0, self.zoom)

    def zoom_out(self, factor: float = 1.2) -> None:
        """
        Zoom out by the specified factor.

        Args:
            factor: Zoom factor
        """
        self.zoom /= factor
        self.zoom = max(0.3, self.zoom)

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

    def set_pan(self, x: int, y: int) -> None:
        """
        Set the pan offset.

        Args:
            x: Horizontal pan offset in pixels
            y: Vertical pan offset in pixels
        """
        self.pan_x = x
        self.pan_y = y

    def pan(self, dx: int, dy: int) -> None:
        """
        Pan by the specified offset.

        Args:
            dx: Horizontal pan offset in pixels
            dy: Vertical pan offset in pixels
        """
        self.pan_x += dx
        self.pan_y += dy

    def reset(self) -> None:
        """
        Reset the viewport to its initial state.
        """
        self.zoom = 1.0
        self.rotation = 0.0
        self.pan_x = 0
        self.pan_y = 0

    def render(self) -> Image.Image:
        """
        Render the content with the current viewport settings.

        Genera la imagen completa del planeta y luego recorta un área basada en el zoom.

        Returns:
            Rendered image
        """
        if self.content is None:
            # Create an empty image if no content is set
            image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "No content set", fill=(255, 255, 255))
            return image

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

        # Calcular el tamaño del área a recortar basado en el zoom
        # Zoom 1.0 significa ver una porción más pequeña (más zoom)
        # Zoom 0.3 significa ver más contenido (menos zoom)
        #
        # Para un zoom de 1.0, queremos recortar un área del tamaño del viewport (512x512)
        # Para un zoom de 0.3, queremos recortar un área más grande (aproximadamente 1706x1706)
        # que luego se redimensionará a 512x512
        crop_size = int(self.width / self.zoom)

        # Calcular las coordenadas de recorte, centradas en el planeta pero con desplazamiento por pan
        # El centro del planeta debe estar en el centro del viewport
        crop_left = center_x - crop_size // 2 + self.pan_x
        crop_top = center_y - crop_size // 2 + self.pan_y
        crop_right = crop_left + crop_size
        crop_bottom = crop_top + crop_size

        # Asegurarse de que el área de recorte esté dentro de los límites de la imagen
        # y mantener el tamaño del recorte constante para preservar la relación de aspecto

        # Si el recorte se sale por la izquierda
        if crop_left < 0:
            crop_right = crop_size  # Mantener el ancho constante
            crop_left = 0

        # Si el recorte se sale por arriba
        if crop_top < 0:
            crop_bottom = crop_size  # Mantener el alto constante
            crop_top = 0

        # Si el recorte se sale por la derecha
        if crop_right > content_width:
            crop_left = max(0, content_width - crop_size)  # Mantener el ancho constante
            crop_right = content_width

        # Si el recorte se sale por abajo
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

        # Redimensionar al tamaño del viewport (512x512)
        viewport_image = cropped_image.resize((self.width, self.height), Image.LANCZOS)

        return viewport_image

    def export(self, filename: str) -> None:
        """
        Export the current viewport to an image file.

        Args:
            filename: Output filename
        """
        image = self.render()
        image.save(filename)
