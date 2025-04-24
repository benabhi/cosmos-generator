"""
Tests for the web interface.
"""
import os
import sys
import unittest
from unittest.mock import patch

# Add the parent directory to the path so we can import the web module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import create_app
from web.utils import (
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    filter_planets,
    get_recent_logs,
    generate_planet_async,
    get_generation_status,
    generation_processes
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
        self.assertIn(b'COSMOS GENERATOR', response.data)

    def test_planets_route(self):
        """Test the planets route."""
        response = self.client.get('/planets')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PLANETS EXPLORER', response.data)

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

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='line1\nline2\nline3\nline4\nline5')
    def test_get_recent_logs_planets(self, mock_open, mock_exists):
        """Test the get_recent_logs function for planet logs."""
        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Get the last 3 lines of the log
        logs = get_recent_logs(3, 'planets')

        # Check that the function returned the expected number of lines
        self.assertEqual(len(logs), 3)

        # Check that the function returned the expected lines
        self.assertEqual(logs, ['line3\n', 'line4\n', 'line5'])

        # Check that the function called open with the correct path
        mock_open.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='line1\nline2\nline3\nline4\nline5')
    def test_get_recent_logs_webserver(self, mock_open, mock_exists):
        """Test the get_recent_logs function for webserver logs."""
        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Get the last 2 lines of the log
        logs = get_recent_logs(2, 'webserver')

        # Check that the function returned the expected number of lines
        self.assertEqual(len(logs), 2)

        # Check that the function returned the expected lines
        self.assertEqual(logs, ['line4\n', 'line5'])

        # Check that the function called open with the correct path
        mock_open.assert_called_once()

    @patch('os.path.exists')
    def test_get_recent_logs_file_not_found(self, mock_exists):
        """Test the get_recent_logs function when the log file doesn't exist."""
        # Mock os.path.exists to return False
        mock_exists.return_value = False

        # Get logs when the file doesn't exist
        logs = get_recent_logs(10, 'planets')

        # Check that the function returned the expected message
        self.assertEqual(logs, ['No planet logs found'])

        # Get webserver logs when the file doesn't exist
        logs = get_recent_logs(10, 'webserver')

        # Check that the function returned the expected message
        self.assertEqual(logs, ['No web logs found'])

    def test_api_generate_valid(self):
        """Test the API endpoint for generating a planet with valid parameters."""
        # Clear any existing processes
        generation_processes.clear()

        # Valid parameters for planet generation
        params = {
            'type': 'desert',
            'seed': '12345',
            'rings': True,
            'atmosphere': True,
            'cloud_coverage': 0.5
        }

        # Make the request
        response = self.client.post('/api/generate', json=params)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('process_id', data)
        self.assertEqual(data['status'], 'started')
        self.assertEqual(data['message'], 'Planet generation started')

        # Check that a process was created
        process_id = data['process_id']
        self.assertIn(process_id, generation_processes)
        # Status can be 'starting' or 'running' depending on timing
        self.assertIn(generation_processes[process_id]['status'], ['starting', 'running'])

        # Check that the parameters are correct, but allow for type conversion
        process_params = generation_processes[process_id]['params']
        self.assertEqual(process_params['type'], params['type'])
        self.assertEqual(process_params['rings'], params['rings'])
        self.assertEqual(process_params['atmosphere'], params['atmosphere'])
        self.assertEqual(process_params['cloud_coverage'], params['cloud_coverage'])
        # The seed might be converted from string to int
        self.assertEqual(str(process_params['seed']), str(params['seed']))

    def test_api_generate_invalid(self):
        """Test the API endpoint for generating a planet with invalid parameters."""
        # Make the request with empty parameters
        response = self.client.post('/api/generate', json={})

        # Check the response
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No parameters provided')

    def test_api_status_valid(self):
        """Test the API endpoint for checking the status of a generation process."""
        # Create a test process
        process_id = '12345'
        generation_processes[process_id] = {
            'status': 'completed',
            'logs': ['Log 1', 'Log 2'],
            'result': {
                'path': '/path/to/planet.png',
                'url': '/static/planets/desert/12345.png'
            }
        }

        # Make the request
        response = self.client.get(f'/api/status/{process_id}')

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['logs'], ['Log 1', 'Log 2'])
        self.assertEqual(data['result']['url'], '/static/planets/desert/12345.png')

    def test_api_status_invalid(self):
        """Test the API endpoint for checking the status of a non-existent process."""
        # Clear any existing processes
        generation_processes.clear()

        # Make the request with a non-existent process ID
        response = self.client.get('/api/status/nonexistent')

        # Check the response
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('Process not found', data['error'])

    @patch('subprocess.Popen')
    @patch('time.time')
    def test_generate_planet_async(self, mock_time, mock_popen):
        """Test the generate_planet_async function."""
        # Clear any existing processes
        generation_processes.clear()

        # Mock time.time to return a fixed value
        mock_time.return_value = 1620000000.0

        # Mock subprocess.Popen
        mock_process = unittest.mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['Log 1', 'Log 2', '']
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Call the function
        params = {
            'type': 'desert',
            'seed': '12345',
            'rings': True
        }
        process_id = generate_planet_async(params)

        # Check that the process was created
        self.assertEqual(process_id, '1620000000000')
        self.assertIn(process_id, generation_processes)
        # Status can be 'starting', 'running', or 'completed' depending on timing
        self.assertIn(generation_processes[process_id]['status'], ['starting', 'running', 'completed'])
        self.assertEqual(generation_processes[process_id]['params'], params)

        # Wait for the thread to complete
        import time
        time.sleep(0.5)

        # Check that the process status was updated
        self.assertEqual(generation_processes[process_id]['status'], 'completed')
        # Check that logs contain our mocked log lines
        logs = generation_processes[process_id]['logs']
        self.assertTrue(any('Log 1' in log for log in logs))
        self.assertTrue(any('Log 2' in log for log in logs))
        self.assertTrue(any('Process completed with return code: 0' in log for log in logs))
        self.assertIn('result', generation_processes[process_id])

    @patch('subprocess.Popen')
    @patch('time.time')
    def test_generate_planet_async_error(self, mock_time, mock_popen):
        """Test the generate_planet_async function with an error."""
        # Clear any existing processes
        generation_processes.clear()

        # Mock time.time to return a fixed value
        mock_time.return_value = 1620000000.0

        # Mock subprocess.Popen to raise an exception
        mock_popen.side_effect = Exception('Test error')

        # Call the function
        params = {
            'type': 'desert',
            'seed': '12345'
        }
        process_id = generate_planet_async(params)

        # Check that the process was created
        self.assertEqual(process_id, '1620000000000')
        self.assertIn(process_id, generation_processes)

        # Wait for the thread to complete
        import time
        time.sleep(0.5)

        # Check that the process status was updated
        self.assertEqual(generation_processes[process_id]['status'], 'failed')
        # The error message might be different depending on the implementation
        self.assertIn('error', generation_processes[process_id])
        self.assertTrue(isinstance(generation_processes[process_id]['error'], str))


if __name__ == '__main__':
    unittest.main()
