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


def apply_edge_antialiasing(image: Image.Image, edge_width: int = 2) -> Image.Image:
    """
    Apply antialiasing to the edge of a circular planet texture.

    This function smooths the edge of a circular planet texture to reduce pixelation
    and jagged edges, creating a more natural-looking planet silhouette.

    Args:
        image: Input image (should be a circular planet texture)
        edge_width: Width of the edge smoothing effect in pixels (1-5 recommended)

    Returns:
        Image with antialiased edges
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Get image dimensions
    width, height = image.size

    # Create a completely new image with a perfect circle
    # This is the most reliable way to ensure a perfect circular edge

    # Calculate the center of the image
    center_x, center_y = width // 2, height // 2

    # Extract the RGB channels from the original image
    r, g, b, alpha = image.split()

    # Create a new alpha channel with a perfect circle
    # First, create a new blank alpha channel
    new_alpha = Image.new('L', (width, height), 0)
    alpha_draw = ImageDraw.Draw(new_alpha)

    # Determine the radius of the planet
    # We'll sample multiple points around the circle to get a more accurate radius
    alpha_data = np.array(alpha)

    # Sample points at 0, 90, 180, and 270 degrees
    sample_points = [
        (center_x + 1, center_y),  # Right (0°)
        (center_x, center_y - 1),  # Top (90°)
        (center_x - 1, center_y),  # Left (180°)
        (center_x, center_y + 1)   # Bottom (270°)
    ]

    # Find the radius by moving outward from each sample point
    radii = []
    for start_x, start_y in sample_points:
        # Determine direction to move
        dx = start_x - center_x
        dy = start_y - center_y

        # Normalize direction
        length = max(1, (dx**2 + dy**2)**0.5)
        dx, dy = dx / length, dy / length

        # Move outward until we find the edge
        x, y = start_x, start_y
        steps = 0
        max_steps = max(width, height)

        while 0 <= int(x) < width and 0 <= int(y) < height and steps < max_steps:
            if alpha_data[int(y), int(x)] < 128:  # Found the edge
                # Calculate distance from center
                distance = ((int(x) - center_x)**2 + (int(y) - center_y)**2)**0.5
                radii.append(distance)
                break

            # Move outward
            x += dx
            y += dy
            steps += 1

    # Use the average radius if we found any edges
    if radii:
        radius = sum(radii) / len(radii)
    else:
        # Fallback: use 45% of the image width
        radius = int(width * 0.45)

    # Draw a filled circle for the planet body
    alpha_draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=255
    )

    # Apply a slight gaussian blur to the alpha channel for antialiasing
    # This creates a smooth edge transition
    new_alpha = new_alpha.filter(ImageFilter.GaussianBlur(0.7))

    # Create a mask for the transition area (the edge of the circle)
    # First, create a slightly smaller circle
    inner_mask = Image.new('L', (width, height), 0)
    inner_draw = ImageDraw.Draw(inner_mask)
    inner_draw.ellipse(
        (center_x - (radius - edge_width), center_y - (radius - edge_width),
         center_x + (radius - edge_width), center_y + (radius - edge_width)),
        fill=255
    )

    # The edge mask is the difference between the alpha and inner mask
    edge_mask = ImageChops.difference(new_alpha, inner_mask)

    # Apply a gaussian blur to the edge mask for smooth transitions
    edge_mask = edge_mask.filter(ImageFilter.GaussianBlur(edge_width / 2))

    # Create a blurred version of the image for the edges
    blurred = image.filter(ImageFilter.GaussianBlur(edge_width / 2))

    # Convert to numpy arrays for faster processing
    img_array = np.array(image)
    blurred_array = np.array(blurred)
    edge_array = np.array(edge_mask)

    # Reshape the edge array to match the image dimensions
    edge_weights = edge_array.reshape(edge_array.shape[0], edge_array.shape[1], 1) / 255.0

    # Blend the original and blurred images based on the edge weights
    result_array = img_array * (1 - edge_weights) + blurred_array * edge_weights

    # Convert back to PIL image
    result = Image.fromarray(result_array.astype(np.uint8))

    # Combine the RGB channels with the new alpha channel
    r, g, b, _ = result.split()  # We don't use the result's alpha channel
    result = Image.merge('RGBA', (r, g, b, new_alpha))

    return result


def apply_subtle_edge_smoothing(image: Image.Image) -> Image.Image:
    """
    Apply a very subtle smoothing only to the extreme edges of the planet.
    This function only affects a few pixels at the very edge to make the planet
    appear more round without changing its overall appearance or affecting rings.

    Args:
        image: Input image (should be a circular planet texture)

    Returns:
        Image with slightly smoothed edges
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Get the alpha channel
    r, g, b, alpha = image.split()

    # Apply a very slight blur only to the alpha channel
    # This is much more subtle than replacing the alpha channel entirely
    smoothed_alpha = alpha.filter(ImageFilter.GaussianBlur(0.5))

    # Create a mask that only affects the very edge pixels
    # First, erode the alpha channel slightly to find the edge
    kernel_size = 3
    eroded = alpha.filter(ImageFilter.MinFilter(kernel_size))

    # The edge is the difference between the original and eroded alpha
    edge = ImageChops.difference(alpha, eroded)

    # Further refine the edge to only include the outermost pixels
    # Convert to numpy for more precise control
    edge_array = np.array(edge)
    alpha_array = np.array(alpha)

    # Create a mask that only includes pixels where:
    # 1. They are part of the detected edge
    # 2. The alpha value is between 1 and 254 (partial transparency)
    edge_mask = np.logical_and(
        edge_array > 0,
        np.logical_and(alpha_array > 0, alpha_array < 255)
    )

    # Convert back to PIL image
    edge_mask_img = Image.fromarray(edge_mask.astype(np.uint8) * 255)

    # Blur the edge mask slightly to create a smooth transition
    edge_mask_img = edge_mask_img.filter(ImageFilter.GaussianBlur(0.7))

    # Use the edge mask to blend between the original and smoothed alpha
    # Convert to numpy arrays for faster processing
    mask_array = np.array(edge_mask_img) / 255.0
    orig_alpha_array = np.array(alpha)
    smooth_alpha_array = np.array(smoothed_alpha)

    # Blend only at the edges
    final_alpha_array = orig_alpha_array * (1 - mask_array) + smooth_alpha_array * mask_array
    final_alpha = Image.fromarray(final_alpha_array.astype(np.uint8))

    # Combine the RGB channels with the subtly smoothed alpha
    result = Image.merge('RGBA', (r, g, b, final_alpha))

    return result


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

    # Pre-calculate a distance map and distortion factors for optimization
    distance_map = np.zeros((height, width))
    distortion_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            # Calculate distance from center (normalized 0-1)
            dx = (x - center_x) / max_distance
            dy = (y - center_y) / max_distance
            distance = math.sqrt(dx*dx + dy*dy)

            # Store the distance
            distance_map[y, x] = distance

            # Calculate distortion factor with a smoother function
            if distance <= 1.0:
                # Use a smoothstep-like function for more natural falloff
                # This creates smoother transitions at the edges
                t = distance
                t = t * t * (3 - 2 * t)  # Smoothstep function
                distortion = 1.0 - strength * (1.0 - math.cos(t * math.pi / 2))
                distortion_map[y, x] = distortion

    # Apply the distortion with improved interpolation
    for y in range(height):
        for x in range(width):
            distance = distance_map[y, x]

            # Skip pixels outside the circle
            if distance > 1.0:
                continue

            # Get the pre-calculated distortion
            distortion = distortion_map[y, x]

            # Calculate normalized vector from center
            dx = (x - center_x) / max_distance
            dy = (y - center_y) / max_distance

            # Calculate source coordinates
            source_x = center_x + (dx * distortion * max_distance)
            source_y = center_y + (dy * distortion * max_distance)

            # Ensure source coordinates are within bounds
            if 0 <= source_x < width - 1 and 0 <= source_y < height - 1:
                # Use bilinear interpolation for smoother results
                x0, y0 = int(source_x), int(source_y)
                x1, y1 = x0 + 1, y0 + 1

                # Calculate interpolation weights
                wx = source_x - x0
                wy = source_y - y0

                # Get the four surrounding pixels
                p00 = img_array[y0, x0]
                p01 = img_array[y0, x1]
                p10 = img_array[y1, x0]
                p11 = img_array[y1, x1]

                # Interpolate in x direction
                p0 = p00 * (1 - wx) + p01 * wx
                p1 = p10 * (1 - wx) + p11 * wx

                # Interpolate in y direction
                pixel = p0 * (1 - wy) + p1 * wy

                # Set the interpolated pixel
                output_array[y, x] = pixel.astype(np.uint8)

    # Convert array back to image
    output = Image.fromarray(output_array)

    # Apply a very subtle smoothing to the edges to improve roundness
    # This only affects the alpha channel at the very edge
    if image.mode == 'RGBA':
        # Extract channels
        r, g, b, alpha = output.split()

        # Apply a very slight blur to the alpha channel
        # This is extremely subtle and won't affect rings
        smoothed_alpha = alpha.filter(ImageFilter.GaussianBlur(0.5))

        # Create a mask that only affects the very edge
        # We'll use a simple threshold to find partially transparent pixels
        alpha_array = np.array(alpha)
        edge_mask = np.logical_and(alpha_array > 0, alpha_array < 255)

        # Convert to PIL image
        edge_mask_img = Image.fromarray(edge_mask.astype(np.uint8) * 255)

        # Blur the mask slightly to create a smooth transition
        edge_mask_img = edge_mask_img.filter(ImageFilter.GaussianBlur(0.5))

        # Use the mask to blend between original and smoothed alpha
        mask_array = np.array(edge_mask_img) / 255.0
        orig_alpha_array = np.array(alpha)
        smooth_alpha_array = np.array(smoothed_alpha)

        # Only blend at the very edges
        final_alpha_array = orig_alpha_array * (1 - mask_array) + smooth_alpha_array * mask_array
        final_alpha = Image.fromarray(final_alpha_array.astype(np.uint8))

        # Combine the RGB channels with the subtly smoothed alpha
        output = Image.merge('RGBA', (r, g, b, final_alpha))

    return output
