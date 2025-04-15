"""
Noise generation algorithms for texture creation.
"""
from typing import Tuple, List, Dict, Any, Optional, Callable
import random
import math
import numpy as np
from opensimplex import OpenSimplex

class NoiseGenerator:
    """
    Implements and combines noise algorithms (Perlin, Simplex, Worley) for texture generation.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a noise generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible noise generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)
        self.simplex = OpenSimplex(seed=self.seed)
        
        # For Worley noise
        self.worley_points: Dict[int, List[Tuple[float, float]]] = {}
        
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
        return self.simplex.noise2(x * scale, y * scale)
    
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
        total = 0
        frequency = scale
        amplitude = 1.0
        max_value = 0
        
        for _ in range(octaves):
            total += self.simplex_noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
            
        return total / max_value
    
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
        total = 0
        frequency = scale
        amplitude = 1.0
        max_value = 0
        
        for _ in range(octaves):
            # Get absolute value of noise and invert it
            value = 1.0 - abs(self.simplex_noise(x * frequency, y * frequency))
            # Square the value to increase the ridges
            value *= value
            total += value * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
            
        return total / max_value
    
    def _get_worley_points(self, cell_count: int) -> List[Tuple[float, float]]:
        """
        Get or generate Worley noise points for a specific cell count.

        Args:
            cell_count: Number of cells in each dimension

        Returns:
            List of point coordinates
        """
        if cell_count not in self.worley_points:
            points = []
            for i in range(cell_count):
                for j in range(cell_count):
                    # Add a random point within each cell
                    x = (i + self.rng.random()) / cell_count
                    y = (j + self.rng.random()) / cell_count
                    points.append((x, y))
            self.worley_points[cell_count] = points
        return self.worley_points[cell_count]
    
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
        points = self._get_worley_points(cell_count)
        
        # Calculate distances to all points
        distances = []
        for px, py in points:
            if distance_function == "euclidean":
                dist = math.sqrt((x - px)**2 + (y - py)**2)
            elif distance_function == "manhattan":
                dist = abs(x - px) + abs(y - py)
            elif distance_function == "chebyshev":
                dist = max(abs(x - px), abs(y - py))
            else:
                raise ValueError(f"Unknown distance function: {distance_function}")
            distances.append(dist)
        
        # Sort distances and return the distance to the closest point
        distances.sort()
        # Normalize to [0, 1] range (approximately)
        return min(1.0, distances[0] * cell_count * 2)
    
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
        warp_x = x + self.simplex_noise(x * warp_scale, y * warp_scale) * warp_strength
        warp_y = y + self.simplex_noise(y * warp_scale, x * warp_scale) * warp_strength
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
