"""
Image manipulation utilities.
"""
from typing import Tuple, Optional, List
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance, ImageOps
import math


def create_transparent_image(size: Tuple[int, int]) -> Image.Image:
    """
    Create a transparent image with the specified size.

    Args:
        size: Image size (width, height)

    Returns:
        Transparent PIL Image
    """
    return Image.new("RGBA", size, (0, 0, 0, 0))


def create_circle_mask(size: int, blur_radius: int = 0) -> Image.Image:
    """
    Create a circular mask image.

    Args:
        size: Size of the mask (width and height)
        blur_radius: Optional blur radius for soft edges

    Returns:
        Circular mask as PIL Image
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size-1, size-1), fill=255)

    if blur_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    return mask


def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    """
    Apply a mask to an image.

    Args:
        image: Source image
        mask: Mask image (grayscale)

    Returns:
        Masked image
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Resize mask if needed
    if mask.size != image.size:
        mask = mask.resize(image.size, Image.LANCZOS)

    # Create a new transparent image
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))

    # Paste the image using the mask
    result.paste(image, (0, 0), mask)

    return result


def overlay_images(base: Image.Image, overlay: Image.Image,
                   position: Tuple[int, int] = (0, 0),
                   blend_mode: str = "normal") -> Image.Image:
    """
    Overlay one image on top of another.

    Args:
        base: Base image
        overlay: Overlay image
        position: Position to place the overlay (x, y)
        blend_mode: Blend mode ("normal", "add", "multiply", "screen")

    Returns:
        Combined image
    """
    # Ensure both images have alpha channels
    if base.mode != "RGBA":
        base = base.convert("RGBA")
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")

    # Create a copy of the base image
    result = base.copy()

    # Apply different blend modes
    if blend_mode == "normal":
        result.paste(overlay, position, overlay)
    elif blend_mode == "add":
        # Create a temporary image for the overlay at the right position
        temp = Image.new("RGBA", base.size, (0, 0, 0, 0))
        temp.paste(overlay, position, overlay)
        # Add the images
        result = ImageChops.add(result, temp)
    elif blend_mode == "multiply":
        # Create a temporary image for the overlay at the right position
        temp = Image.new("RGBA", base.size, (0, 0, 0, 0))
        temp.paste(overlay, position, overlay)
        # Multiply the images
        result = ImageChops.multiply(result, temp)
    elif blend_mode == "screen":
        # Create a temporary image for the overlay at the right position
        temp = Image.new("RGBA", base.size, (0, 0, 0, 0))
        temp.paste(overlay, position, overlay)
        # Screen the images
        result = ImageChops.screen(result, temp)
    else:
        raise ValueError(f"Unknown blend mode: {blend_mode}")

    return result


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust the brightness of an image.

    Args:
        image: Input image
        factor: Brightness factor (>1.0 brightens, <1.0 darkens)

    Returns:
        Brightness-adjusted image
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust the contrast of an image.

    Args:
        image: Input image
        factor: Contrast factor (>1.0 increases contrast, <1.0 decreases contrast)

    Returns:
        Contrast-adjusted image
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def create_gradient(size: Tuple[int, int], start_color: Tuple[int, int, int, int],
                    end_color: Tuple[int, int, int, int], direction: str = "horizontal") -> Image.Image:
    """
    Create a gradient image.

    Args:
        size: Image size (width, height)
        start_color: Starting color (RGBA)
        end_color: Ending color (RGBA)
        direction: Gradient direction ("horizontal", "vertical", "radial")

    Returns:
        Gradient image
    """
    width, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    if direction == "horizontal":
        for x in range(width):
            # Calculate color at this position
            r = int(start_color[0] + (end_color[0] - start_color[0]) * x / width)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * x / width)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * x / width)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * x / width)

            # Draw a line with this color
            draw.line([(x, 0), (x, height)], fill=(r, g, b, a))

    elif direction == "vertical":
        for y in range(height):
            # Calculate color at this position
            r = int(start_color[0] + (end_color[0] - start_color[0]) * y / height)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * y / height)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * y / height)

            # Draw a line with this color
            draw.line([(0, y), (width, y)], fill=(r, g, b, a))

    elif direction == "radial":
        # Calculate the maximum distance from center
        center_x, center_y = width // 2, height // 2
        max_distance = np.sqrt(center_x**2 + center_y**2)

        # Create a numpy array for the image
        img_array = np.zeros((height, width, 4), dtype=np.uint8)

        # Fill the array with gradient colors
        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = distance / max_distance

                # Calculate color at this position
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)

                img_array[y, x] = [r, g, b, a]

        # Convert array back to image
        image = Image.fromarray(img_array, mode="RGBA")

    else:
        raise ValueError(f"Unknown gradient direction: {direction}")

    return image


def resize_image(image: Image.Image, size: Tuple[int, int],
                 resample: int = Image.LANCZOS) -> Image.Image:
    """
    Resize an image to the specified size.

    Args:
        image: Input image
        size: Target size (width, height)
        resample: Resampling filter

    Returns:
        Resized image
    """
    return image.resize(size, resample)


def rotate_image(image: Image.Image, angle: float,
                 expand: bool = True) -> Image.Image:
    """
    Rotate an image by the specified angle.

    Args:
        image: Input image
        angle: Rotation angle in degrees
        expand: Whether to expand the output image to fit the rotated image

    Returns:
        Rotated image
    """
    return image.rotate(angle, expand=expand, resample=Image.BICUBIC)


def apply_spherical_distortion(image: Image.Image, strength: float = 0.2) -> Image.Image:
    """
    Apply a spherical distortion effect to simulate the curvature of a planet.

    This creates a subtle bulging effect that makes flat textures appear more
    spherical, enhancing the 3D appearance of planets.

    Args:
        image: Input image (should be square for best results)
        strength: Distortion strength (0.0 to 1.0, where 0.0 is no distortion
                 and 1.0 is maximum distortion)
                 Recommended values: 0.1-0.3 for subtle effect

    Returns:
        Distorted image with same dimensions as input
    """
    # Ensure strength is in valid range
    strength = max(0.0, min(1.0, strength))

    # Get image dimensions
    width, height = image.width, image.height

    # Create output image (same size as input)
    output = Image.new(image.mode, (width, height))

    # Calculate center of the image
    center_x, center_y = width // 2, height // 2

    # Calculate maximum distance from center (radius)
    max_distance = min(center_x, center_y)

    # Create numpy arrays for faster processing
    img_array = np.array(image)
    output_array = np.zeros_like(img_array)

    # Apply the distortion
    for y in range(height):
        for x in range(width):
            # Calculate distance from center (normalized 0-1)
            dx = (x - center_x) / max_distance
            dy = (y - center_y) / max_distance
            distance = math.sqrt(dx*dx + dy*dy)

            # Skip pixels outside the circle
            if distance > 1.0:
                continue

            # Calculate the distortion factor
            # This creates a subtle bulging effect toward the center
            # The formula creates a non-linear distortion that's stronger near the edges
            distortion = 1.0 - strength * (1.0 - math.cos(distance * math.pi / 2))

            # Calculate source coordinates
            source_x = center_x + (dx * distortion * max_distance)
            source_y = center_y + (dy * distortion * max_distance)

            # Ensure source coordinates are within bounds
            if 0 <= source_x < width and 0 <= source_y < height:
                # Get the nearest pixel (simple approach)
                src_x_int = int(source_x)
                src_y_int = int(source_y)

                # Copy the pixel
                output_array[y, x] = img_array[src_y_int, src_x_int]

    # Convert array back to image
    output = Image.fromarray(output_array)

    return output
