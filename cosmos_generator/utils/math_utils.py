"""
Common mathematical operations.
"""
from typing import Tuple, List, Optional
import math
import numpy as np


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.

    Args:
        a: First value
        b: Second value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def smoothstep(a: float, b: float, t: float) -> float:
    """
    Smooth interpolation between two values.

    Args:
        a: First value
        b: Second value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Smoothly interpolated value
    """
    t = max(0.0, min(1.0, (t - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between a minimum and maximum.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Distance between the points
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def manhattan_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Manhattan distance between two points.

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Manhattan distance between the points
    """
    return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])


def chebyshev_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Chebyshev distance between two points.

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Chebyshev distance between the points
    """
    return max(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))


def normalize(v: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normalize a 2D vector to unit length.

    Args:
        v: Vector (x, y)

    Returns:
        Normalized vector
    """
    length = math.sqrt(v[0]**2 + v[1]**2)
    if length < 1e-10:
        return (0.0, 0.0)
    return (v[0] / length, v[1] / length)


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to the range [0.0, 1.0].

    Args:
        value: Value to normalize
        min_val: Minimum value of the range
        max_val: Maximum value of the range

    Returns:
        Normalized value in the range [0.0, 1.0]
    """
    if max_val - min_val < 1e-10:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def normalize_3d(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Normalize a 3D vector to unit length.

    Args:
        v: Vector (x, y, z)

    Returns:
        Normalized vector
    """
    length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if length < 1e-10:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def dot_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """
    Calculate dot product of two 2D vectors.

    Args:
        v1: First vector (x, y)
        v2: Second vector (x, y)

    Returns:
        Dot product
    """
    return v1[0] * v2[0] + v1[1] * v2[1]


def dot_product_3d(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    """
    Calculate dot product of two 3D vectors.

    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)

    Returns:
        Dot product
    """
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def cross_product_3d(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate cross product of two 3D vectors.

    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)

    Returns:
        Cross product vector
    """
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )


def rotate_point(point: Tuple[float, float], center: Tuple[float, float], angle_deg: float) -> Tuple[float, float]:
    """
    Rotate a point around a center by a given angle.

    Args:
        point: Point to rotate (x, y)
        center: Center of rotation (x, y)
        angle_deg: Rotation angle in degrees

    Returns:
        Rotated point
    """
    angle_rad = math.radians(angle_deg)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)

    # Translate point to origin
    translated_x = point[0] - center[0]
    translated_y = point[1] - center[1]

    # Rotate
    rotated_x = translated_x * cos_angle - translated_y * sin_angle
    rotated_y = translated_x * sin_angle + translated_y * cos_angle

    # Translate back
    return (rotated_x + center[0], rotated_y + center[1])


def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
    """
    Convert Cartesian coordinates to polar coordinates.

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        Polar coordinates (radius, angle in radians)
    """
    radius = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x)
    return (radius, angle)


def polar_to_cartesian(radius: float, angle: float) -> Tuple[float, float]:
    """
    Convert polar coordinates to Cartesian coordinates.

    Args:
        radius: Radius
        angle: Angle in radians

    Returns:
        Cartesian coordinates (x, y)
    """
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)


def spherical_to_cartesian(radius: float, theta: float, phi: float) -> Tuple[float, float, float]:
    """
    Convert spherical coordinates to Cartesian coordinates.

    Args:
        radius: Radius
        theta: Polar angle in radians (0 to π)
        phi: Azimuthal angle in radians (0 to 2π)

    Returns:
        Cartesian coordinates (x, y, z)
    """
    x = radius * math.sin(theta) * math.cos(phi)
    y = radius * math.sin(theta) * math.sin(phi)
    z = radius * math.cos(theta)
    return (x, y, z)


def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Convert Cartesian coordinates to spherical coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate

    Returns:
        Spherical coordinates (radius, theta, phi)
    """
    radius = math.sqrt(x*x + y*y + z*z)
    if radius < 1e-10:
        return (0.0, 0.0, 0.0)

    theta = math.acos(z / radius)
    phi = math.atan2(y, x)
    return (radius, theta, phi)


def ellipse_point(center: Tuple[float, float], a: float, b: float,
                 angle: float, rotation: float = 0.0) -> Tuple[float, float]:
    """
    Calculate a point on an ellipse.

    Args:
        center: Center of the ellipse (x, y)
        a: Semi-major axis
        b: Semi-minor axis
        angle: Parameter angle in radians (0 to 2π)
        rotation: Rotation of the ellipse in radians

    Returns:
        Point on the ellipse
    """
    # Calculate point on unrotated ellipse
    x = a * math.cos(angle)
    y = b * math.sin(angle)

    # Rotate the point
    cos_rot = math.cos(rotation)
    sin_rot = math.sin(rotation)
    x_rot = x * cos_rot - y * sin_rot
    y_rot = x * sin_rot + y * cos_rot

    # Translate to center
    return (center[0] + x_rot, center[1] + y_rot)
