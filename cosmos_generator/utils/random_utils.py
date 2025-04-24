"""
Seeded random number generation utilities.
"""
from typing import List, Tuple, Optional, TypeVar, Sequence, Any
import random
import math
import numpy as np

T = TypeVar('T')


class RandomGenerator:
    """
    Seeded random number generator for reproducible results.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a random generator with an optional seed.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)
        self.np_rng = np.random.RandomState(self.seed)
        
    def get_seed(self) -> int:
        """
        Get the current seed.

        Returns:
            Current seed
        """
        return self.seed
    
    def set_seed(self, seed: int) -> None:
        """
        Set a new seed.

        Args:
            seed: New random seed
        """
        self.seed = seed
        self.rng = random.Random(self.seed)
        self.np_rng = np.random.RandomState(self.seed)
    
    def random(self) -> float:
        """
        Generate a random float in the range [0.0, 1.0).

        Returns:
            Random float
        """
        return self.rng.random()
    
    def uniform(self, a: float, b: float) -> float:
        """
        Generate a random float in the range [a, b).

        Args:
            a: Lower bound
            b: Upper bound

        Returns:
            Random float
        """
        return self.rng.uniform(a, b)
    
    def randint(self, a: int, b: int) -> int:
        """
        Generate a random integer in the range [a, b].

        Args:
            a: Lower bound
            b: Upper bound

        Returns:
            Random integer
        """
        return self.rng.randint(a, b)
    
    def choice(self, seq: Sequence[T]) -> T:
        """
        Choose a random element from a sequence.

        Args:
            seq: Sequence to choose from

        Returns:
            Random element
        """
        return self.rng.choice(seq)
    
    def choices(self, population: Sequence[T], weights: Optional[Sequence[float]] = None, 
               k: int = 1) -> List[T]:
        """
        Choose k random elements from a population with optional weights.

        Args:
            population: Population to choose from
            weights: Optional weights for each element
            k: Number of elements to choose

        Returns:
            List of random elements
        """
        return self.rng.choices(population, weights=weights, k=k)
    
    def sample(self, population: Sequence[T], k: int) -> List[T]:
        """
        Choose k unique random elements from a population.

        Args:
            population: Population to sample from
            k: Number of elements to choose

        Returns:
            List of unique random elements
        """
        return self.rng.sample(population, k)
    
    def shuffle(self, x: List[Any]) -> None:
        """
        Shuffle a list in-place.

        Args:
            x: List to shuffle
        """
        self.rng.shuffle(x)
    
    def normal(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """
        Generate a random float from a normal distribution.

        Args:
            mu: Mean
            sigma: Standard deviation

        Returns:
            Random float
        """
        return self.rng.normalvariate(mu, sigma)
    
    def lognormal(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """
        Generate a random float from a log-normal distribution.

        Args:
            mu: Mean of the underlying normal distribution
            sigma: Standard deviation of the underlying normal distribution

        Returns:
            Random float
        """
        return self.rng.lognormvariate(mu, sigma)
    
    def exponential(self, lambd: float = 1.0) -> float:
        """
        Generate a random float from an exponential distribution.

        Args:
            lambd: Rate parameter (1/mean)

        Returns:
            Random float
        """
        return self.rng.expovariate(lambd)
    
    def triangular(self, low: float = 0.0, high: float = 1.0, mode: Optional[float] = None) -> float:
        """
        Generate a random float from a triangular distribution.

        Args:
            low: Lower bound
            high: Upper bound
            mode: Mode (peak) of the distribution

        Returns:
            Random float
        """
        return self.rng.triangular(low, high, mode if mode is not None else (low + high) / 2)
    
    def random_point_in_circle(self, radius: float = 1.0) -> Tuple[float, float]:
        """
        Generate a random point inside a circle.

        Args:
            radius: Radius of the circle

        Returns:
            Random point (x, y)
        """
        # Generate random angle and distance from center
        angle = self.uniform(0, 2 * math.pi)
        # Use square root for uniform distribution
        distance = radius * math.sqrt(self.random())
        
        # Convert to Cartesian coordinates
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        
        return (x, y)
    
    def random_point_on_circle(self, radius: float = 1.0) -> Tuple[float, float]:
        """
        Generate a random point on a circle.

        Args:
            radius: Radius of the circle

        Returns:
            Random point (x, y)
        """
        angle = self.uniform(0, 2 * math.pi)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        return (x, y)
    
    def random_point_in_sphere(self, radius: float = 1.0) -> Tuple[float, float, float]:
        """
        Generate a random point inside a sphere.

        Args:
            radius: Radius of the sphere

        Returns:
            Random point (x, y, z)
        """
        # Generate random spherical coordinates
        phi = self.uniform(0, 2 * math.pi)
        theta = math.acos(2 * self.random() - 1)
        # Use cube root for uniform distribution
        r = radius * (self.random() ** (1/3))
        
        # Convert to Cartesian coordinates
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        
        return (x, y, z)
    
    def random_point_on_sphere(self, radius: float = 1.0) -> Tuple[float, float, float]:
        """
        Generate a random point on a sphere.

        Args:
            radius: Radius of the sphere

        Returns:
            Random point (x, y, z)
        """
        # Generate random spherical coordinates
        phi = self.uniform(0, 2 * math.pi)
        theta = math.acos(2 * self.random() - 1)
        
        # Convert to Cartesian coordinates
        x = radius * math.sin(theta) * math.cos(phi)
        y = radius * math.sin(theta) * math.sin(phi)
        z = radius * math.cos(theta)
        
        return (x, y, z)
    
    def random_color(self, include_alpha: bool = False) -> Tuple:
        """
        Generate a random RGB or RGBA color.

        Args:
            include_alpha: Whether to include an alpha channel

        Returns:
            Random color tuple
        """
        if include_alpha:
            return (self.randint(0, 255), self.randint(0, 255), self.randint(0, 255), self.randint(0, 255))
        else:
            return (self.randint(0, 255), self.randint(0, 255), self.randint(0, 255))
    
    def random_pastel_color(self, include_alpha: bool = False) -> Tuple:
        """
        Generate a random pastel RGB or RGBA color.

        Args:
            include_alpha: Whether to include an alpha channel

        Returns:
            Random pastel color tuple
        """
        r = self.randint(150, 255)
        g = self.randint(150, 255)
        b = self.randint(150, 255)
        
        if include_alpha:
            a = self.randint(0, 255)
            return (r, g, b, a)
        else:
            return (r, g, b)
    
    def perturb_value(self, value: float, amount: float) -> float:
        """
        Randomly perturb a value by a certain amount.

        Args:
            value: Original value
            amount: Maximum perturbation amount

        Returns:
            Perturbed value
        """
        return value + self.uniform(-amount, amount)
    
    def perturb_point(self, point: Tuple[float, float], amount: float) -> Tuple[float, float]:
        """
        Randomly perturb a 2D point by a certain amount.

        Args:
            point: Original point (x, y)
            amount: Maximum perturbation amount

        Returns:
            Perturbed point
        """
        return (
            point[0] + self.uniform(-amount, amount),
            point[1] + self.uniform(-amount, amount)
        )
    
    def perturb_point_3d(self, point: Tuple[float, float, float], amount: float) -> Tuple[float, float, float]:
        """
        Randomly perturb a 3D point by a certain amount.

        Args:
            point: Original point (x, y, z)
            amount: Maximum perturbation amount

        Returns:
            Perturbed point
        """
        return (
            point[0] + self.uniform(-amount, amount),
            point[1] + self.uniform(-amount, amount),
            point[2] + self.uniform(-amount, amount)
        )
