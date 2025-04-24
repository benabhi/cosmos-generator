"""
Lighting and shading utilities.
"""
from typing import Tuple, Optional
import math
import numpy as np
from PIL import Image, ImageDraw


def calculate_normal_map(height_map: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Calculate a normal map from a height map.

    Args:
        height_map: 2D numpy array representing height values
        strength: Strength of the normal map effect

    Returns:
        3D numpy array representing the normal map (RGB)
    """
    # Get dimensions
    height, width = height_map.shape

    # Create an empty normal map
    normal_map = np.zeros((height, width, 3), dtype=np.float32)

    # Calculate gradients
    gradient_x = np.zeros((height, width), dtype=np.float32)
    gradient_y = np.zeros((height, width), dtype=np.float32)

    # X gradient (horizontal)
    gradient_x[:, :-1] = height_map[:, 1:] - height_map[:, :-1]

    # Y gradient (vertical)
    gradient_y[:-1, :] = height_map[1:, :] - height_map[:-1, :]

    # Scale gradients by strength
    gradient_x *= strength
    gradient_y *= strength

    # Calculate normals
    # Normal = normalize((-gradient_x, -gradient_y, 1))
    normal_map[:, :, 0] = -gradient_x
    normal_map[:, :, 1] = -gradient_y
    normal_map[:, :, 2] = 1.0

    # Normalize
    norm = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
    normal_map = normal_map / (norm + 1e-10)

    # Convert to [0, 1] range
    normal_map = (normal_map + 1.0) * 0.5

    return normal_map


def apply_directional_light(image: Image.Image, normal_map: np.ndarray,
                           light_direction: Tuple[float, float, float] = (0.5, 0.5, 1.0),
                           ambient: float = 0.2, diffuse: float = 0.8,
                           specular: float = 0.0, shininess: float = 10.0) -> Image.Image:
    """
    Apply directional lighting to an image using a normal map.

    Args:
        image: Input image
        normal_map: Normal map as a 3D numpy array
        light_direction: Direction of the light source (x, y, z)
        ambient: Ambient light intensity
        diffuse: Diffuse light intensity
        specular: Specular light intensity
        shininess: Shininess factor for specular highlights

    Returns:
        Image with directional lighting applied
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Convert image to numpy array
    img_array = np.array(image)

    # Normalize light direction
    light_dir = np.array(light_direction, dtype=np.float32)
    light_dir = light_dir / np.sqrt(np.sum(light_dir**2))

    # Convert normal map from [0, 1] to [-1, 1] range
    normals = normal_map * 2.0 - 1.0

    # Calculate lighting
    # Dot product between normal and light direction for diffuse lighting
    dot = np.sum(normals * light_dir, axis=2)
    dot = np.clip(dot, 0.0, 1.0)

    # Calculate specular component (if needed)
    specular_map = None
    if specular > 0:
        # Calculate reflection vector
        reflection = 2.0 * np.expand_dims(dot, axis=2) * normals
        reflection = reflection - np.expand_dims(light_dir, axis=(0, 1))

        # View direction (assuming view from above)
        view_dir = np.array([0.0, 0.0, 1.0])

        # Calculate specular term
        spec_dot = np.sum(reflection * view_dir, axis=2)
        spec_dot = np.clip(spec_dot, 0.0, 1.0)
        specular_map = spec_dot ** shininess

    # Apply lighting to the image
    # Create a copy of the array with float32 type for calculations
    result_float = img_array.copy().astype(np.float32)  # Convert to float32 to avoid overflow

    # RGB channels
    for i in range(3):
        # Ambient + diffuse
        result_float[:, :, i] = img_array[:, :, i] * (ambient + diffuse * dot)

        # Add specular (if enabled)
        if specular > 0:
            result_float[:, :, i] += 255 * specular * specular_map

    # Clip values to valid range and convert back to uint8
    result = img_array.copy()  # Keep original array structure with uint8
    result[:, :, :3] = np.clip(result_float[:, :, :3], 0, 255).astype(np.uint8)

    # Create new image from the modified array
    return Image.fromarray(result)


def create_shadow_mask(size: Tuple[int, int], light_angle: float = 45.0,
                       shadow_length: float = 0.5) -> Image.Image:
    """
    Create a shadow mask for a spherical object.

    Args:
        size: Size of the mask (width, height)
        light_angle: Angle of the light source in degrees (0 = right, 90 = top)
        shadow_length: Length of the shadow relative to the object radius

    Returns:
        Shadow mask as PIL Image
    """
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # Calculate light direction
    light_rad = math.radians(light_angle)
    light_x = math.cos(light_rad)
    light_y = -math.sin(light_rad)  # Negative because y increases downward in images

    # Calculate center and radius
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y)

    # Calculate shadow offset
    shadow_dx = -light_x * radius * shadow_length
    shadow_dy = -light_y * radius * shadow_length

    # Draw shadow ellipse
    shadow_x = center_x + shadow_dx
    shadow_y = center_y + shadow_dy

    # Calculate shadow ellipse parameters
    # The shadow is an ellipse that gets more elongated as the light angle gets lower
    shadow_width = radius
    shadow_height = radius * abs(math.sin(light_rad))
    if shadow_height < 0.1 * radius:
        shadow_height = 0.1 * radius

    # Draw the shadow ellipse
    left = shadow_x - shadow_width
    top = shadow_y - shadow_height
    right = shadow_x + shadow_width
    bottom = shadow_y + shadow_height

    draw.ellipse((left, top, right, bottom), fill=128)

    # Blur the shadow
    mask = mask.filter(Image.GaussianBlur(radius // 10))

    return mask


def apply_ambient_occlusion(image: Image.Image, strength: float = 0.5) -> Image.Image:
    """
    Apply ambient occlusion to an image.

    Args:
        image: Input image
        strength: Strength of the ambient occlusion effect

    Returns:
        Image with ambient occlusion applied
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Create a mask for the edges
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    # Draw a filled circle with a gradient from edge to center
    radius = min(width, height) // 2
    center_x, center_y = width // 2, height // 2

    # Create a numpy array for the mask
    mask_array = np.zeros((height, width), dtype=np.uint8)

    # Fill the array with gradient values
    for y in range(height):
        for x in range(width):
            # Calculate distance from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx*dx + dy*dy)

            # Skip if outside the circle
            if distance > radius:
                continue

            # Calculate occlusion value (stronger at edges)
            # 1.0 at the edge, 0.0 at the center
            occlusion = distance / radius

            # Apply strength
            occlusion *= strength

            # Store in the mask array
            mask_array[y, x] = 255 - int(occlusion * 255)

    # Convert array to mask
    mask = Image.fromarray(mask_array)

    # Apply the mask to darken edges
    img_array = np.array(image)
    mask_array = np.array(mask)

    # Apply occlusion to RGB channels
    for i in range(3):
        img_array[:, :, i] = img_array[:, :, i] * mask_array / 255

    # Create new image from the modified array
    return Image.fromarray(img_array)
