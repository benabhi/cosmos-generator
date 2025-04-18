"""
Tests for the web interface.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the web module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import create_app
from web.utils import (
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    filter_planets
)


class TestWebInterface(unittest.TestCase):
    """Test the web interface."""

    def setUp(self):
        """Set up the test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_index_route(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PLANET GENERATOR', response.data)

    def test_planets_route(self):
        """Test the planets route."""
        response = self.client.get('/planets')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PLANET EXPLORER', response.data)

    def test_logs_route(self):
        """Test the logs route."""
        response = self.client.get('/logs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SYSTEM LOGS', response.data)

    def test_api_planet_types(self):
        """Test the API endpoint for planet types."""
        response = self.client.get('/api/planet-types')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('types', data)
        self.assertIn('variations', data)
        self.assertIn('defaults', data)

    def test_api_planets(self):
        """Test the API endpoint for planets."""
        response = self.client.get('/api/planets')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('planets', data)
        self.assertIn('count', data)
        self.assertIn('total', data)

    def test_get_planet_types(self):
        """Test the get_planet_types function."""
        types = get_planet_types()
        self.assertIsInstance(types, list)
        self.assertIn('desert', [t.lower() for t in types])
        self.assertIn('ocean', [t.lower() for t in types])

    def test_get_planet_variations(self):
        """Test the get_planet_variations function."""
        variations = get_planet_variations()
        self.assertIsInstance(variations, dict)
        self.assertIn('desert', variations)
        self.assertIn('ocean', variations)
        self.assertIsInstance(variations['desert'], list)
        self.assertIsInstance(variations['ocean'], list)

    def test_get_default_variations(self):
        """Test the get_default_variations function."""
        defaults = get_default_variations()
        self.assertIsInstance(defaults, dict)
        self.assertIn('desert', defaults)
        self.assertIn('ocean', defaults)
        self.assertEqual(defaults['desert'], 'arid')
        self.assertEqual(defaults['ocean'], 'water_world')

    def test_filter_planets(self):
        """Test the filter_planets function."""
        # Create some test planets
        planets = [
            {
                'type': 'Desert',
                'seed': '12345',
                'params': {
                    'rings': True,
                    'atmosphere': True
                }
            },
            {
                'type': 'Ocean',
                'seed': '67890',
                'params': {
                    'clouds': 0.5
                }
            },
            {
                'type': 'Desert',
                'seed': '54321',
                'params': {}
            }
        ]
        
        # Test filtering by type
        filtered = filter_planets(planets, {'type': 'desert'})
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]['type'], 'Desert')
        self.assertEqual(filtered[1]['type'], 'Desert')
        
        # Test filtering by seed
        filtered = filter_planets(planets, {'seed': '123'})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['seed'], '12345')
        
        # Test filtering by features
        filtered = filter_planets(planets, {'has_rings': True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['seed'], '12345')
        
        filtered = filter_planets(planets, {'has_clouds': True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['seed'], '67890')
        
        # Test multiple filters
        filtered = filter_planets(planets, {'type': 'desert', 'has_atmosphere': True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['seed'], '12345')


if __name__ == '__main__':
    unittest.main()
