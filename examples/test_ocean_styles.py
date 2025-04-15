#!/usr/bin/env python3
"""
Example script to test the different Ocean planet styles.
"""
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate Ocean planets with different styles.
    """
    # Create output directory
    output_dir = "output/test_ocean_styles"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create generator
    generator = PlanetGenerator()
    
    # Base seed for reproducibility
    base_seed = 12345
    
    # Generate Ocean planet with archipelago style (default)
    ocean_archipelago = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "archipelago",  # This is the default, so it's optional
    })
    
    # Generate Ocean planet with water world style
    ocean_water_world = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "water_world",
    })
    
    # Generate Ocean planet with archipelago style and atmosphere
    ocean_archipelago_atmo = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "archipelago",
        "atmosphere": True,
    })
    
    # Generate Ocean planet with water world style and atmosphere
    ocean_water_world_atmo = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "water_world",
        "atmosphere": True,
    })
    
    # Generate Ocean planet with archipelago style and rings
    ocean_archipelago_rings = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "archipelago",
        "rings": True,
    })
    
    # Generate Ocean planet with water world style and rings
    ocean_water_world_rings = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "water_world",
        "rings": True,
    })
    
    # Generate Ocean planet with archipelago style, atmosphere and rings
    ocean_archipelago_both = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "archipelago",
        "atmosphere": True,
        "rings": True,
    })
    
    # Generate Ocean planet with water world style, atmosphere and rings
    ocean_water_world_both = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "water_world",
        "atmosphere": True,
        "rings": True,
    })
    
    # Save all planets using Container
    container = Container()
    
    # Save archipelago style
    container.set_content(ocean_archipelago)
    archipelago_path = os.path.join(output_dir, "ocean_archipelago.png")
    container.export(archipelago_path)
    print(f"Saved Ocean planet with archipelago style to {archipelago_path}")
    
    # Save water world style
    container.set_content(ocean_water_world)
    water_world_path = os.path.join(output_dir, "ocean_water_world.png")
    container.export(water_world_path)
    print(f"Saved Ocean planet with water world style to {water_world_path}")
    
    # Save archipelago style with atmosphere
    container.set_content(ocean_archipelago_atmo)
    archipelago_atmo_path = os.path.join(output_dir, "ocean_archipelago_atmosphere.png")
    container.export(archipelago_atmo_path)
    print(f"Saved Ocean planet with archipelago style and atmosphere to {archipelago_atmo_path}")
    
    # Save water world style with atmosphere
    container.set_content(ocean_water_world_atmo)
    water_world_atmo_path = os.path.join(output_dir, "ocean_water_world_atmosphere.png")
    container.export(water_world_atmo_path)
    print(f"Saved Ocean planet with water world style and atmosphere to {water_world_atmo_path}")
    
    # Save archipelago style with rings
    container.set_content(ocean_archipelago_rings)
    archipelago_rings_path = os.path.join(output_dir, "ocean_archipelago_rings.png")
    container.export(archipelago_rings_path)
    print(f"Saved Ocean planet with archipelago style and rings to {archipelago_rings_path}")
    
    # Save water world style with rings
    container.set_content(ocean_water_world_rings)
    water_world_rings_path = os.path.join(output_dir, "ocean_water_world_rings.png")
    container.export(water_world_rings_path)
    print(f"Saved Ocean planet with water world style and rings to {water_world_rings_path}")
    
    # Save archipelago style with atmosphere and rings
    container.set_content(ocean_archipelago_both)
    archipelago_both_path = os.path.join(output_dir, "ocean_archipelago_both.png")
    container.export(archipelago_both_path)
    print(f"Saved Ocean planet with archipelago style, atmosphere and rings to {archipelago_both_path}")
    
    # Save water world style with atmosphere and rings
    container.set_content(ocean_water_world_both)
    water_world_both_path = os.path.join(output_dir, "ocean_water_world_both.png")
    container.export(water_world_both_path)
    print(f"Saved Ocean planet with water world style, atmosphere and rings to {water_world_both_path}")


if __name__ == "__main__":
    main()
