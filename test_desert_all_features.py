#!/usr/bin/env python3
"""
Test script to generate Desert planets with all features at specific zoom levels.
"""
import os
import sys
from PIL import Image, ImageDraw

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


class CustomContainer(Container):
    """
    Extended Container class that allows custom zoom levels.
    """
    
    def render(self, custom_zoom=None) -> Image.Image:
        """
        Render the content with a custom zoom level.
        
        Args:
            custom_zoom: Custom zoom level (0.1 to 1.0)
            
        Returns:
            Rendered image (512x512 pixels)
        """
        if self.content is None:
            # Create an empty image if no content is set
            image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "No content set", fill=(255, 255, 255))
            return image

        # Detectar si el contenido es un planeta con anillos
        has_rings = False
        if hasattr(self.content, "has_rings"):
            has_rings = self.content.has_rings

        # Get the content image
        if hasattr(self.content, "render"):
            content_image = self.content.render()
        elif hasattr(self.content, "image"):
            content_image = self.content.image
        elif isinstance(self.content, Image.Image):
            content_image = self.content
        else:
            raise ValueError("Content must have a render() method, an image attribute, or be a PIL Image")

        # Aplicar rotación si es necesario
        if self.rotation != 0.0:
            from cosmos_generator.utils.image_utils import rotate_image
            content_image = rotate_image(content_image, self.rotation)

        # Obtener el tamaño de la imagen del contenido
        content_width, content_height = content_image.size

        # Calcular el centro de la imagen
        center_x = content_width // 2
        center_y = content_height // 2

        # Determinar el tipo de contenido y aplicar la vista fija adecuada
        if custom_zoom is not None:
            # Use the custom zoom level
            fixed_zoom = custom_zoom
        elif has_rings:
            # Para planetas con anillos, usamos un factor fijo de 0.75
            fixed_zoom = 0.75
        else:
            # Para planetas sin anillos, mostramos la vista completa del planeta
            fixed_zoom = 1.0

        # Calculate crop size based on zoom level
        crop_size = int(min(content_width, content_height) * fixed_zoom)

        # Calculate crop coordinates
        crop_left = center_x - crop_size // 2
        crop_top = center_y - crop_size // 2
        crop_right = crop_left + crop_size
        crop_bottom = crop_top + crop_size

        # Recortar la imagen usando las coordenadas calculadas
        cropped_image = content_image.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Redimensionar al tamaño fijo del container (512x512)
        container_image = cropped_image.resize((self.width, self.height), Image.LANCZOS)

        return container_image


def generate_desert_planet(seed=12345, with_rings=False, zoom_level=0.75):
    """
    Generate a Desert planet with all features (atmosphere and clouds) at a specific zoom level.
    
    Args:
        seed: Seed for reproducible generation
        with_rings: Whether to add rings to the planet
        zoom_level: Zoom level (0.1 to 1.0)
        
    Returns:
        Generated planet image
    """
    # Create a planet generator
    generator = PlanetGenerator()
    
    # Create the planet with all features enabled
    planet = generator.create("Desert", {
        "size": 512,
        "seed": seed,
        "rings": with_rings,
        "atmosphere": True,  # Always enable atmosphere
        "clouds": True,      # Always enable clouds
        "cloud_coverage": 1.0,  # Maximum cloud coverage
        "lighting": {
            "intensity": 1.0,
            "angle": 45,
            "falloff": 0.7
        }
    })
    
    # Create a custom container with the specified zoom level
    container = CustomContainer()
    container.set_content(planet)
    
    # Render the planet with the custom zoom level
    return container.render(custom_zoom=zoom_level)


def main():
    """
    Generate Desert planets with all features at specific zoom levels.
    """
    # Create output directory
    output_dir = "output/planets/examples/test_desert_all_features"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define zoom levels to test
    zoom_levels = [0.5, 1.0]
    
    # Define seeds to use
    seeds = [12345, 54321, 98765]
    
    # Generate planets with and without rings
    for seed in seeds:
        for with_rings in [False, True]:
            ring_text = "with_rings" if with_rings else "no_rings"
            
            print(f"Generating Desert planet (Seed: {seed}, Rings: {with_rings})...")
            
            for zoom in zoom_levels:
                # Generate the planet with this zoom level
                planet_image = generate_desert_planet(
                    seed=seed,
                    with_rings=with_rings,
                    zoom_level=zoom
                )
                
                # Save the image with descriptive filename
                filename = f"desert_seed{seed}_{ring_text}_zoom{zoom:.1f}.png"
                output_path = os.path.join(output_dir, filename)
                
                planet_image.save(output_path)
                print(f"  - Saved with zoom {zoom:.1f} to {output_path}")


if __name__ == "__main__":
    main()
