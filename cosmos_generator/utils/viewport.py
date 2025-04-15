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

    def __init__(self, width: int = 800, height: int = 600, initial_zoom: float = 1.0):
        """
        Initialize a viewport with the specified dimensions and zoom.

        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
            initial_zoom: Initial zoom factor
        """
        self.width = width
        self.height = height
        self.zoom = initial_zoom
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
            zoom: Zoom factor (>1.0 zooms in, <1.0 zooms out)
        """
        self.zoom = max(0.1, min(10.0, zoom))

    def zoom_in(self, factor: float = 1.2) -> None:
        """
        Zoom in by the specified factor.

        Args:
            factor: Zoom factor
        """
        self.zoom *= factor
        self.zoom = min(10.0, self.zoom)

    def zoom_out(self, factor: float = 1.2) -> None:
        """
        Zoom out by the specified factor.

        Args:
            factor: Zoom factor
        """
        self.zoom /= factor
        self.zoom = max(0.1, self.zoom)

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

        # Apply transformations
        # 1. Check if the content is larger than the viewport
        content_width, content_height = content_image.size

        # Calculate the scale factor needed to fit the content in the viewport
        # with a small margin (5% of the viewport size)
        margin = min(self.width, self.height) * 0.05
        width_scale = (self.width - margin) / content_width if content_width > (self.width - margin) else 1.0
        height_scale = (self.height - margin) / content_height if content_height > (self.height - margin) else 1.0

        # Use the smaller scale factor to maintain aspect ratio
        scale_factor = min(width_scale, height_scale)

        # Scale down the content if necessary
        if scale_factor < 1.0:
            new_width = int(content_width * scale_factor)
            new_height = int(content_height * scale_factor)
            content_image = content_image.resize((new_width, new_height), Image.LANCZOS)
            content_width, content_height = content_image.size

        # 2. Apply zoom after scaling to fit
        if self.zoom != 1.0:
            new_width = int(content_image.width * self.zoom)
            new_height = int(content_image.height * self.zoom)
            content_image = resize_image(content_image, (new_width, new_height))
            content_width, content_height = content_image.size

        # 3. Rotate
        if self.rotation != 0.0:
            content_image = rotate_image(content_image, self.rotation)
            content_width, content_height = content_image.size

        # 4. Create the viewport image
        viewport_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        # Calculate paste position to center the content
        paste_x = (self.width - content_width) // 2 + self.pan_x
        paste_y = (self.height - content_height) // 2 + self.pan_y

        # Paste the content
        viewport_image.paste(content_image, (paste_x, paste_y), content_image if content_image.mode == "RGBA" else None)

        return viewport_image

    def export(self, filename: str) -> None:
        """
        Export the current viewport to an image file.

        Args:
            filename: Output filename
        """
        image = self.render()
        image.save(filename)
