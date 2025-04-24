"""
Noise generation using PyFastNoiseLite for improved performance.

This module provides a high-performance implementation of various noise algorithms
using the PyFastNoiseLite library. It replaces the previous custom noise implementation
with optimized C++ implementations for better performance while maintaining the same interface.

The FastNoiseGenerator class implements the same interface as the previous NoiseGenerator,
allowing for a seamless transition to the faster implementation.
"""
from typing import Tuple, List, Optional, Callable
import random

import numpy as np
from pyfastnoiselite.pyfastnoiselite import FastNoiseLite, NoiseType, FractalType, CellularDistanceFunction, CellularReturnType

from cosmos_generator.core.interfaces import NoiseGeneratorInterface

class FastNoiseGenerator(NoiseGeneratorInterface):
    """
    Implements noise algorithms using PyFastNoiseLite for improved performance.

    This class provides a high-performance implementation of various noise algorithms
    using the PyFastNoiseLite library. It maintains the same interface as the previous
    NoiseGenerator class but uses optimized C++ implementations internally for better performance.

    The class supports various noise types including Simplex noise, fractal noise,
    ridged noise, and cellular (Worley) noise, as well as domain warping techniques
    for creating more organic patterns.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a noise generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible noise generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

        # Ensure the seed is within the acceptable range for FastNoiseLite
        # FastNoiseLite expects a 32-bit signed integer
        # We'll use modulo to ensure it's within the range of a 32-bit signed integer
        safe_seed = self.seed % (2**31 - 1)

        # Create FastNoiseLite instances for different noise types
        self.simplex = FastNoiseLite(seed=safe_seed)
        self.simplex.noise_type = NoiseType.NoiseType_OpenSimplex2

        self.fractal = FastNoiseLite(seed=safe_seed)
        self.fractal.noise_type = NoiseType.NoiseType_OpenSimplex2
        self.fractal.fractal_type = FractalType.FractalType_FBm

        self.ridged = FastNoiseLite(seed=safe_seed)
        self.ridged.noise_type = NoiseType.NoiseType_OpenSimplex2
        self.ridged.fractal_type = FractalType.FractalType_Ridged

        self.cellular = FastNoiseLite(seed=safe_seed)
        self.cellular.noise_type = NoiseType.NoiseType_Cellular
        self.cellular.cellular_return_type = CellularReturnType.CellularReturnType_Distance

        # For domain warping
        self.warp = FastNoiseLite(seed=safe_seed)
        self.warp.noise_type = NoiseType.NoiseType_OpenSimplex2

    def simplex_noise(self, x: float, y: float, scale: float = 1.0) -> float:
        """
        Generate 2D Simplex noise at the given coordinates.

        This method uses the OpenSimplex2 algorithm from PyFastNoiseLite to generate
        high-quality, smooth noise values.

        Args:
            x: X coordinate
            y: Y coordinate
            scale: Scale factor for the noise (higher values = more detail)

        Returns:
            Noise value in range [-1, 1]
        """
        self.simplex.frequency = scale
        return self.simplex.get_noise(x, y)

    def fractal_simplex(self, x: float, y: float, octaves: int = 6,
                        persistence: float = 0.5, lacunarity: float = 2.0,
                        scale: float = 1.0) -> float:
        """
        Generate fractal Simplex noise by combining multiple octaves.

        This method uses Fractal Brownian Motion (FBm) to combine multiple octaves of
        Simplex noise, creating more complex and natural-looking patterns. Each octave
        adds finer detail to the noise.

        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of octaves to combine (higher = more detail but slower)
            persistence: How much each octave contributes to the final result (0.0-1.0)
            lacunarity: How much detail is added at each octave (typically 2.0)
            scale: Base scale factor for the noise (higher values = more detail)

        Returns:
            Noise value in range [-1, 1]
        """
        self.fractal.frequency = scale
        self.fractal.fractal_octaves = octaves
        self.fractal.fractal_gain = persistence
        self.fractal.fractal_lacunarity = lacunarity
        return self.fractal.get_noise(x, y)

    def ridged_simplex(self, x: float, y: float, octaves: int = 6,
                       persistence: float = 0.5, lacunarity: float = 2.0,
                       scale: float = 1.0) -> float:
        """
        Generate ridged fractal Simplex noise for terrain-like features.

        This method uses a ridged multi-fractal algorithm that creates noise patterns
        with sharp ridges and valleys, ideal for terrain generation. The algorithm
        inverts and modifies the noise values to create ridge-like structures.

        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of octaves to combine (higher = more detail but slower)
            persistence: How much each octave contributes to the final result (0.0-1.0)
            lacunarity: How much detail is added at each octave (typically 2.0)
            scale: Base scale factor for the noise (higher values = more detail)

        Returns:
            Noise value in range [0, 1]
        """
        self.ridged.frequency = scale
        self.ridged.fractal_octaves = octaves
        self.ridged.fractal_gain = persistence
        self.ridged.fractal_lacunarity = lacunarity
        # FastNoiseLite's ridged multi returns values in [-1, 1], so we normalize to [0, 1]
        return (self.ridged.get_noise(x, y) + 1.0) * 0.5

    def worley_noise(self, x: float, y: float, cell_count: int = 10,
                     distance_function: str = "euclidean") -> float:
        """
        Generate Worley (cellular) noise at the given coordinates.

        This method creates cellular noise patterns based on the distance to randomly
        distributed feature points. It's excellent for creating textures that look like
        cells, scales, or cobblestones. Different distance functions create different
        visual effects.

        Args:
            x: X coordinate in range [0, 1]
            y: Y coordinate in range [0, 1]
            cell_count: Number of cells in each dimension (higher = smaller cells)
            distance_function: Type of distance function to use:
                - "euclidean": Standard distance (circular cells)
                - "manhattan": Sum of absolute differences (diamond-shaped cells)
                - "chebyshev": Maximum of absolute differences (square cells)

        Returns:
            Noise value in range [0, 1]
        """
        # Set up cellular noise parameters
        self.cellular.frequency = cell_count

        # Set distance function
        if distance_function == "euclidean":
            self.cellular.cellular_distance_function = CellularDistanceFunction.CellularDistanceFunction_Euclidean
        elif distance_function == "manhattan":
            self.cellular.cellular_distance_function = CellularDistanceFunction.CellularDistanceFunction_Manhattan
        elif distance_function == "chebyshev":
            self.cellular.cellular_distance_function = CellularDistanceFunction.CellularDistanceFunction_Hybrid
        else:
            raise ValueError(f"Unknown distance function: {distance_function}")

        # FastNoiseLite's cellular noise returns values in [-1, 1], so we normalize to [0, 1]
        return (self.cellular.get_noise(x * cell_count, y * cell_count) + 1.0) * 0.5

    def cellular_noise(self, x: float, y: float, scale: float = 1.0) -> float:
        """
        Generate cellular (Worley) noise at the given coordinates.

        This is an alias for worley_noise with simplified parameters, provided for
        compatibility with the reef texture generation.

        Args:
            x: X coordinate in range [0, 1]
            y: Y coordinate in range [0, 1]
            scale: Scale factor for the noise (higher values = more detail)

        Returns:
            Noise value in range [0, 1]
        """
        # Convert scale to an appropriate cell count (higher scale = more cells)
        cell_count = int(10 * scale)
        if cell_count < 1:
            cell_count = 1

        return self.worley_noise(x, y, cell_count, "euclidean")

    def domain_warp(self, x: float, y: float, warp_function: Callable[[float, float], Tuple[float, float]],
                    noise_function: Callable[[float, float], float]) -> float:
        """
        Apply domain warping to create more organic noise patterns.

        Domain warping is a powerful technique that distorts the input coordinates before
        applying the noise function. This creates more natural, organic patterns by breaking
        up the regularity of the noise. It's especially useful for creating realistic
        terrain, clouds, and other natural phenomena.

        Args:
            x: X coordinate
            y: Y coordinate
            warp_function: Function that warps the input coordinates
            noise_function: Function that generates noise from the warped coordinates

        Returns:
            Warped noise value
        """
        warped_x, warped_y = warp_function(x, y)
        return noise_function(warped_x, warped_y)

    def simplex_warp(self, x: float, y: float, warp_scale: float = 0.1,
                     warp_strength: float = 0.5) -> Tuple[float, float]:
        """
        Warp coordinates using Simplex noise.

        This method uses Simplex noise to distort the input coordinates, creating a
        smooth, flowing warping effect. It's commonly used with domain_warp() to create
        natural-looking patterns like flowing water, clouds, or marble textures.

        Args:
            x: X coordinate
            y: Y coordinate
            warp_scale: Scale of the warping noise (lower = smoother distortion)
            warp_strength: Strength of the warping effect (higher = more distortion)

        Returns:
            Warped coordinates (x, y)
        """
        self.warp.frequency = warp_scale
        warp_x = x + self.warp.get_noise(x, y) * warp_strength
        warp_y = y + self.warp.get_noise(y, x) * warp_strength
        return warp_x, warp_y

    def generate_noise_map(self, width: int, height: int,
                           noise_function: Callable[[float, float], float]) -> np.ndarray:
        """
        Generate a 2D noise map using the specified noise function.

        This method creates a 2D array of noise values by sampling the provided noise
        function at regular intervals. The coordinates are normalized to the range [0, 1]
        to ensure consistent scaling regardless of the map dimensions.

        Args:
            width: Width of the noise map in pixels
            height: Height of the noise map in pixels
            noise_function: Function that generates noise values from (x, y) coordinates

        Returns:
            2D numpy array of noise values with shape (height, width)
        """
        noise_map = np.zeros((height, width), dtype=np.float32)

        for y in range(height):
            for x in range(width):
                # Normalize coordinates to [0, 1] range
                nx = x / width
                ny = y / height
                noise_map[y, x] = noise_function(nx, ny)

        return noise_map

    def normalize_noise_map(self, noise_map: np.ndarray) -> np.ndarray:
        """
        Normalize a noise map to the range [0, 1].

        This method linearly rescales all values in the noise map to fit within the
        range [0, 1], where the minimum value becomes 0 and the maximum value becomes 1.
        This is useful for ensuring consistent value ranges across different noise
        generation methods or for preparing noise maps for visualization.

        Args:
            noise_map: 2D numpy array of noise values with any range

        Returns:
            Normalized noise map with values in range [0, 1]
        """
        min_val = np.min(noise_map)
        max_val = np.max(noise_map)

        if max_val == min_val:
            return np.zeros_like(noise_map)

        return (noise_map - min_val) / (max_val - min_val)

    def combine_noise_maps(self, maps: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Combine multiple noise maps with optional weights.

        This method blends multiple noise maps together, optionally weighting their
        contributions. This is useful for creating complex textures by combining different
        noise types or frequencies. The result is normalized to ensure values remain in
        the range [0, 1].

        Args:
            maps: List of noise maps to combine (must all have the same shape)
            weights: Optional list of weights for each map (defaults to equal weights)
                     The weights do not need to sum to 1, as the result is normalized.

        Returns:
            Combined and normalized noise map with values in range [0, 1]
        """
        if not maps:
            raise ValueError("No maps provided")

        if weights is None:
            weights = [1.0 / len(maps)] * len(maps)

        if len(maps) != len(weights):
            raise ValueError("Number of maps and weights must match")

        # Ensure all maps have the same shape
        shape = maps[0].shape
        for m in maps:
            if m.shape != shape:
                raise ValueError("All maps must have the same shape")

        # Combine maps
        result = np.zeros(shape, dtype=np.float32)
        for i, m in enumerate(maps):
            result += m * weights[i]

        return self.normalize_noise_map(result)
