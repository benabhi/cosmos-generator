#!/usr/bin/env python3
"""
Test script to verify the final fixed zoom functionality.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.container import Container
from cosmos_generator.utils.logger import logger


def generate_planet_with_zoom(planet_type="Desert", seed=12345, with_rings=False, zoom_level=None):
    """
    Generate a planet with a specific zoom level.
    
    Args:
        planet_type: Type of planet to generate
        seed: Seed for reproducible generation
        with_rings: Whether to add rings to the planet
        zoom_level: Zoom level (0.0 to 1.0, None for default)
        
    Returns:
        Generated planet image
    """
    # Create a planet generator
    generator = PlanetGenerator()
    
    # Create the planet with all features enabled
    planet = generator.create(planet_type, {
        "size": 512,
        "seed": seed,
        "rings": with_rings,
        "atmosphere": True,
        "clouds": True,
        "cloud_coverage": 1.0,
        "lighting": {
            "intensity": 1.0,
            "angle": 45,
            "falloff": 0.7
        }
    })
    
    # Create a container with the specified zoom level
    container = Container(zoom_level=zoom_level)
    container.set_content(planet)
    
    # Render the planet
    planet_image = container.render()
    
    # Add a label with the zoom level
    draw = ImageDraw.Draw(planet_image)
    try:
        font = ImageFont.truetype("Arial", 30)
    except IOError:
        font = ImageFont.load_default()
    
    zoom_text = f"Zoom: {zoom_level:.1f}" if zoom_level is not None else "Default Zoom"
    draw.text((10, 10), zoom_text, fill=(255, 255, 255), font=font)
    
    return planet_image


def main():
    """
    Generate individual images at different zoom levels.
    """
    # Create output directory
    output_dir = "output/planets/examples/test_zoom_final_fix"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define zoom levels to test
    zoom_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, None]  # None for default
    
    # Test cases
    test_cases = [
        # (planet_type, seed, with_rings)
        ("Desert", 12345, False),  # Desert planet without rings
        ("Desert", 12345, True),   # Desert planet with rings
    ]
    
    # Generate images for each test case and zoom level
    for planet_type, seed, with_rings in test_cases:
        rings_text = "with_rings" if with_rings else "no_rings"
        base_filename = f"{planet_type.lower()}_{rings_text}"
        
        print(f"Generating {planet_type} planet (Rings: {with_rings})...")
        
        for zoom in zoom_levels:
            # Generate the planet with this zoom level
            planet_image = generate_planet_with_zoom(
                planet_type=planet_type,
                seed=seed,
                with_rings=with_rings,
                zoom_level=zoom
            )
            
            # Save the image
            if zoom is None:
                zoom_text = "default"
            else:
                zoom_text = f"{zoom:.1f}"
            
            filename = f"{base_filename}_zoom_{zoom_text}.png"
            output_path = os.path.join(output_dir, filename)
            
            planet_image.save(output_path)
            print(f"  - Saved with zoom {zoom_text} to {output_path}")


if __name__ == "__main__":
    main()
