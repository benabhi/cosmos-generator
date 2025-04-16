#!/usr/bin/env python3
"""
Example script demonstrating how to ensure directories exist before operations.

This script shows how to use the directory utilities to ensure that
the necessary directories exist before performing file operations.
"""
import os
import sys
import random
from PIL import Image, ImageDraw

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from cosmos_generator.utils.directory_utils import (
    ensure_output_directories,
    get_planet_result_directory,
    get_planet_debug_directory,
    ensure_log_file_directory
)


def create_dummy_image(width=512, height=512, color=(255, 0, 0)):
    """
    Create a dummy image for testing.
    
    Args:
        width: Image width
        height: Image height
        color: Image color
        
    Returns:
        PIL Image
    """
    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # Draw some random circles
    for _ in range(10):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(10, 50)
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=color
        )
    
    return image


def main():
    """
    Demonstrate how to ensure directories exist before operations.
    """
    # Ensure all output directories exist
    print("Ensuring all output directories exist...")
    ensure_output_directories()
    print("Done!")
    
    # Generate a dummy planet image
    seed = random.randint(1000, 9999)
    planet_type = random.choice(config.PLANET_TYPES)
    
    print(f"\nGenerating dummy {planet_type} planet with seed {seed}...")
    
    # Create a dummy image
    image = create_dummy_image(
        color=(0, 0, 100) if planet_type == "ocean" else (200, 150, 100)
    )
    
    # Save the image to the result directory
    result_dir = get_planet_result_directory(planet_type)
    result_path = os.path.join(result_dir, f"{seed}.png")
    image.save(result_path)
    print(f"Saved result image to {result_path}")
    
    # Save a debug texture
    debug_dir = get_planet_debug_directory("terrain")
    debug_path = os.path.join(debug_dir, f"{seed}.png")
    image.save(debug_path)
    print(f"Saved debug texture to {debug_path}")
    
    # Create a cloud texture and mask
    cloud_dir = get_planet_debug_directory("clouds", seed)
    
    # Cloud texture
    cloud_texture = create_dummy_image(color=(255, 255, 255))
    cloud_texture_path = os.path.join(cloud_dir, "texture.png")
    cloud_texture.save(cloud_texture_path)
    print(f"Saved cloud texture to {cloud_texture_path}")
    
    # Cloud mask
    cloud_mask = create_dummy_image(color=(200, 200, 200))
    cloud_mask_path = os.path.join(cloud_dir, "mask.png")
    cloud_mask.save(cloud_mask_path)
    print(f"Saved cloud mask to {cloud_mask_path}")
    
    # Ensure log file directory exists
    ensure_log_file_directory()
    log_path = config.PLANETS_LOG_FILE
    
    # Write a dummy log entry
    with open(log_path, "a") as f:
        f.write(f"[TEST] Generated dummy {planet_type} planet with seed {seed}\n")
    
    print(f"Added log entry to {log_path}")
    
    print("\nAll operations completed successfully!")
    print("The directory structure has been created and populated with example files.")


if __name__ == "__main__":
    main()
