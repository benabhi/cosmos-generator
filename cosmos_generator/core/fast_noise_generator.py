"""
Noise generation using PyFastNoiseLite for improved performance.
"""
from typing import Tuple, List, Optional, Callable
import random

import numpy as np
from pyfastnoiselite.pyfastnoiselite import FastNoiseLite, NoiseType, FractalType, CellularDistanceFunction, CellularReturnType

class FastNoiseGenerator:
    """
    Implements noise algorithms using PyFastNoiseLite for improved performance.
    Provides the same interface as NoiseGenerator but uses FastNoiseLite internally.
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

        Args:
            x: X coordinate
            y: Y coordinate
            scale: Scale factor for the noise

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

        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of octaves to combine
            persistence: How much each octave contributes to the final result
            lacunarity: How much detail is added at each octave
            scale: Base scale factor for the noise

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

        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of octaves to combine
            persistence: How much each octave contributes to the final result
            lacunarity: How much detail is added at each octave
            scale: Base scale factor for the noise

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

        Args:
            x: X coordinate in range [0, 1]
            y: Y coordinate in range [0, 1]
            cell_count: Number of cells in each dimension
            distance_function: Type of distance function to use ("euclidean", "manhattan", "chebyshev")

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

    def domain_warp(self, x: float, y: float, warp_function: Callable[[float, float], Tuple[float, float]],
                    noise_function: Callable[[float, float], float]) -> float:
        """
        Apply domain warping to create more organic noise patterns.

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

        Args:
            x: X coordinate
            y: Y coordinate
            warp_scale: Scale of the warping noise
            warp_strength: Strength of the warping effect

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

        Args:
            width: Width of the noise map
            height: Height of the noise map
            noise_function: Function that generates noise values

        Returns:
            2D numpy array of noise values
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

        Args:
            noise_map: 2D numpy array of noise values

        Returns:
            Normalized noise map
        """
        min_val = np.min(noise_map)
        max_val = np.max(noise_map)

        if max_val == min_val:
            return np.zeros_like(noise_map)

        return (noise_map - min_val) / (max_val - min_val)

    def combine_noise_maps(self, maps: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Combine multiple noise maps with optional weights.

        Args:
            maps: List of noise maps to combine
            weights: Optional list of weights for each map (defaults to equal weights)

        Returns:
            Combined noise map
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
