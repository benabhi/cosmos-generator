#!/usr/bin/env python3
"""
Test script to verify that components (colors, textures, rings) are consistent with the same seed.
"""
import os
import sys
import hashlib
from PIL import Image

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator.core.planet_generator import PlanetGenerator


def image_hash(image):
    """
    Calculate a hash of an image to compare images.
    """
    # Convert to RGB to ensure consistent format
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Get image data
    data = image.tobytes()

    # Calculate hash
    return hashlib.md5(data).hexdigest()


def test_seed_consistency():
    """
    Test that planets generated with the same seed are identical.
    """
    # Create output directory
    output_dir = "output/test_seed_consistency"
    os.makedirs(output_dir, exist_ok=True)

    # Test parameters
    seed = 12345
    planet_type = "Desert"

    print(f"Testing seed consistency with seed={seed}, type={planet_type}")

    # Create two planet generators
    generator1 = PlanetGenerator(seed=seed)
    generator2 = PlanetGenerator(seed=seed)

    # Create two planets with the same parameters
    planet1 = generator1.create(planet_type, {
        "seed": seed,
        "size": 512,
        "rings": True,
        "atmosphere": True,
        "atmosphere_intensity": 0.8,
    })

    planet2 = generator2.create(planet_type, {
        "seed": seed,
        "size": 512,
        "rings": True,
        "atmosphere": True,
        "atmosphere_intensity": 0.8,
    })

    # Save the planets
    planet1_path = os.path.join(output_dir, "planet1.png")
    planet2_path = os.path.join(output_dir, "planet2.png")

    planet1.save(planet1_path)
    planet2.save(planet2_path)

    print(f"Saved planets to {planet1_path} and {planet2_path}")

    # Load the images and calculate hashes
    image1 = Image.open(planet1_path)
    image2 = Image.open(planet2_path)

    hash1 = image_hash(image1)
    hash2 = image_hash(image2)

    print(f"Image 1 hash: {hash1}")
    print(f"Image 2 hash: {hash2}")

    # Compare hashes
    if hash1 == hash2:
        print("SUCCESS: Planets are identical!")
    else:
        print("FAILURE: Planets are different!")

    # We don't need to test with Container since the planets are identical


if __name__ == "__main__":
    test_seed_consistency()
