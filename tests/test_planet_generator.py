#!/usr/bin/env python3
"""
Test script for the Cosmos Generator library.
"""
import os
import sys
import unittest
from PIL import Image

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.viewport import Viewport


class TestPlanetGenerator(unittest.TestCase):
    """
    Test cases for the PlanetGenerator class.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        self.generator = PlanetGenerator(seed=12345)
        
    def test_create_desert_planet(self):
        """
        Test creating a desert planet.
        """
        planet = self.generator.create("Desert", {
            "size": 256,
            "seed": 12345
        })
        
        # Check that the planet was created
        self.assertIsNotNone(planet)
        
        # Check that the planet has the correct type
        self.assertEqual(planet.PLANET_TYPE, "Desert")
        
        # Check that the planet has the correct size
        self.assertEqual(planet.size, 256)
        
        # Check that the planet has the correct seed
        self.assertEqual(planet.seed, 12345)
        
        # Check that the planet can be rendered
        image = planet.render()
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.width, 256)
        self.assertEqual(image.height, 256)
        self.assertEqual(image.mode, "RGBA")
        
    def test_create_planet_with_features(self):
        """
        Test creating a planet with features.
        """
        planet = self.generator.create("Desert", {
            "size": 256,
            "seed": 12345,
            "rings": True,
            "atmosphere": True,
            "atmosphere_intensity": 0.8,
            "light_intensity": 1.2,
            "light_angle": 30.0
        })
        
        # Check that the planet was created
        self.assertIsNotNone(planet)
        
        # Check that the features were set correctly
        self.assertTrue(planet.has_rings)
        self.assertTrue(planet.has_atmosphere)
        self.assertEqual(planet.atmosphere_intensity, 0.8)
        self.assertEqual(planet.light_intensity, 1.2)
        self.assertEqual(planet.light_angle, 30.0)
        
        # Check that the planet can be rendered
        image = planet.render()
        self.assertIsInstance(image, Image.Image)
        
    def test_viewport(self):
        """
        Test the viewport functionality.
        """
        planet = self.generator.create("Desert", {
            "size": 256,
            "seed": 12345
        })
        
        viewport = Viewport(width=400, height=300, initial_zoom=1.0)
        viewport.set_content(planet)
        viewport.zoom_in(1.5)
        viewport.rotate(45)
        viewport.pan(20, -10)
        
        # Check that the viewport has the correct settings
        self.assertEqual(viewport.width, 400)
        self.assertEqual(viewport.height, 300)
        self.assertEqual(viewport.zoom, 1.5)
        self.assertEqual(viewport.rotation, 45.0)
        self.assertEqual(viewport.pan_x, 20)
        self.assertEqual(viewport.pan_y, -10)
        
        # Check that the viewport can be rendered
        image = viewport.render()
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.width, 400)
        self.assertEqual(image.height, 300)
        self.assertEqual(image.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
