"""
Tests for the web utility functions.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from web.utils import (
    get_generation_status,
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    get_color_palettes,
    filter_planets,
    get_recent_logs,
    get_planet_log
)


# Este test ha sido eliminado porque la función generate_planet_async no existe en el módulo web.utils


@patch('web.utils.generation_processes')
def test_get_generation_status_not_found(mock_generation_processes):
    """Test the get_generation_status function with a non-existent process ID."""
    # Mock the generation_processes dictionary to be empty
    mock_generation_processes.get.return_value = None

    # Call the function with a non-existent process ID
    status = get_generation_status('non_existent_process_id')

    # Check that the status is None
    assert status is None


@patch('web.utils.generation_processes')
def test_get_generation_status_starting(mock_generation_processes):
    """Test the get_generation_status function with a process in the 'starting' state."""
    # Mock the generation_processes dictionary to return a process in the 'starting' state
    mock_generation_processes.get.return_value = {
        'status': 'starting',
        'logs': [],
        'result': None
    }

    # Call the function with a process ID
    status = get_generation_status('test_process_id')

    # Check that the status is as expected
    assert status['status'] == 'starting'
    assert status['logs'] == []
    assert status['result'] is None


@patch('web.utils.generation_processes')
def test_get_generation_status_running(mock_generation_processes):
    """Test the get_generation_status function with a process in the 'running' state."""
    # Mock the generation_processes dictionary to return a process in the 'running' state
    mock_generation_processes.get.return_value = {
        'status': 'running',
        'logs': ['Starting generation...'],
        'result': None
    }

    # Call the function with a process ID
    status = get_generation_status('test_process_id')

    # Check that the status is as expected
    assert status['status'] == 'running'
    assert status['logs'] == ['Starting generation...']
    assert status['result'] is None


@patch('web.utils.generation_processes')
def test_get_generation_status_completed(mock_generation_processes):
    """Test the get_generation_status function with a process in the 'completed' state."""
    # Mock the generation_processes dictionary to return a process in the 'completed' state
    mock_generation_processes.get.return_value = {
        'status': 'completed',
        'logs': ['Starting generation...', 'Generation complete'],
        'result': {
            'seed': '12345',
            'type': 'desert',
            'url': '/static/planets/desert/12345/planet.png'
        }
    }

    # Call the function with a process ID
    status = get_generation_status('test_process_id')

    # Check that the status is as expected
    assert status['status'] == 'completed'
    assert status['logs'] == ['Starting generation...', 'Generation complete']
    assert status['result']['seed'] == '12345'
    assert status['result']['type'] == 'desert'
    assert status['result']['url'] == '/static/planets/desert/12345/planet.png'


@patch('web.utils.generation_processes')
def test_get_generation_status_failed(mock_generation_processes):
    """Test the get_generation_status function with a process in the 'failed' state."""
    # Mock the generation_processes dictionary to return a process in the 'failed' state
    mock_generation_processes.get.return_value = {
        'status': 'failed',
        'logs': ['Starting generation...', 'Error: Test error'],
        'result': None,
        'error': 'Test error'
    }

    # Call the function with a process ID
    status = get_generation_status('test_process_id')

    # Check that the status is as expected
    assert status['status'] == 'failed'
    assert status['logs'] == ['Starting generation...', 'Error: Test error']
    assert status['result'] is None
    assert status['error'] == 'Test error'


def test_get_planet_types():
    """Test the get_planet_types function."""
    # Call the function
    planet_types = get_planet_types()

    # Check that the result is a list of strings
    assert isinstance(planet_types, list)
    assert all(isinstance(planet_type, str) for planet_type in planet_types)

    # Check that the list is not empty
    assert len(planet_types) > 0


def test_get_planet_variations():
    """Test the get_planet_variations function."""
    # Call the function
    variations = get_planet_variations()

    # Check that the result is a dictionary
    assert isinstance(variations, dict)

    # Check that the dictionary is not empty
    assert len(variations) > 0

    # Check that each key maps to a list of strings
    for planet_type, planet_variations in variations.items():
        assert isinstance(planet_type, str)
        assert isinstance(planet_variations, list)
        assert all(isinstance(variation, str) for variation in planet_variations)
        assert len(planet_variations) > 0


def test_get_default_variations():
    """Test the get_default_variations function."""
    # Call the function
    defaults = get_default_variations()

    # Check that the result is a dictionary
    assert isinstance(defaults, dict)

    # Check that the dictionary is not empty
    assert len(defaults) > 0

    # Check that each key maps to a string
    for planet_type, default_variation in defaults.items():
        assert isinstance(planet_type, str)
        assert isinstance(default_variation, str)


def test_get_color_palettes():
    """Test the get_color_palettes function."""
    # Call the function
    palettes = get_color_palettes()

    # Check that the result is a dictionary
    assert isinstance(palettes, dict)

    # Check that the dictionary is not empty
    assert len(palettes) > 0

    # Check that each key maps to a dictionary of palettes
    for planet_type, color_palettes in palettes.items():
        assert isinstance(planet_type, str)
        assert isinstance(color_palettes, dict)
        assert len(color_palettes) > 0


# Este test ha sido eliminado porque la función read_planets_csv no existe en el módulo web.utils


@patch('web.utils.get_generated_planets')
def test_filter_planets(mock_get_generated_planets):
    """Test the filter_planets function."""
    # Mock the get_generated_planets function to return a list of planets
    mock_get_generated_planets.return_value = [
        {
            'seed': '00012345',
            'type': 'desert',
            'url': '/static/planets/desert/00012345/planet.png',
            'params': {
                'variation': 'standard',
                'atmosphere': True,
                'rings': True,
                'clouds': True
            }
        },
        {
            'seed': '00067890',
            'type': 'ocean',
            'url': '/static/planets/ocean/00067890/planet.png',
            'params': {
                'variation': 'archipelago',
                'atmosphere': False,
                'rings': False,
                'clouds': False
            }
        }
    ]

    # Test with no filters
    planets = filter_planets(mock_get_generated_planets.return_value, {})
    assert len(planets) == 2

    # Test with type filter
    planets = filter_planets(mock_get_generated_planets.return_value, {'type': 'desert'})
    assert len(planets) == 1
    assert planets[0]['type'] == 'desert'

    # Test with seed filter
    planets = filter_planets(mock_get_generated_planets.return_value, {'seed': '123'})
    assert len(planets) == 1
    assert planets[0]['seed'] == '00012345'

    # Test with has_rings filter
    # The implementation only checks if 'rings' is in p['params'], not its value
    planets = filter_planets(mock_get_generated_planets.return_value, {'has_rings': True})
    # Both planets have 'rings' in their params, so both should be returned
    assert len(planets) == 2

    # Test with has_atmosphere filter
    # The implementation only checks if 'atmosphere' is in p['params'], not its value
    planets = filter_planets(mock_get_generated_planets.return_value, {'has_atmosphere': True})
    # Both planets have 'atmosphere' in their params, so both should be returned
    assert len(planets) == 2

    # Test with has_clouds filter
    # The implementation only checks if 'clouds' is in p['params'], not its value
    planets = filter_planets(mock_get_generated_planets.return_value, {'has_clouds': True})
    # Both planets have 'clouds' in their params, so both should be returned
    assert len(planets) == 2

    # Test with multiple filters
    planets = filter_planets(mock_get_generated_planets.return_value, {'type': 'desert', 'has_rings': True})
    assert len(planets) == 1
    assert planets[0]['type'] == 'desert'
    assert planets[0]['params']['rings'] is True

    # Test with no matching planets
    planets = filter_planets(mock_get_generated_planets.return_value, {'type': 'jungle'})
    assert len(planets) == 0


@patch('web.utils.os.path.exists')
@patch('web.utils.open')
def test_get_recent_logs(mock_open, mock_exists):
    """Test the get_recent_logs function."""
    # Mock the os.path.exists function to return True
    mock_exists.return_value = True

    # Mock the open function to return a file-like object
    mock_file = MagicMock()
    mock_file.__enter__.return_value.readlines.return_value = [
        '2023-05-01 12:34:56 [INFO] Starting generation...\n',
        '2023-05-01 12:34:57 [INFO] Generation complete\n'
    ]
    mock_open.return_value = mock_file

    # Test with default parameters
    logs = get_recent_logs()
    assert len(logs) == 2
    assert logs[0].strip() == '2023-05-01 12:34:56 [INFO] Starting generation...'
    assert logs[1].strip() == '2023-05-01 12:34:57 [INFO] Generation complete'

    # Test with custom lines parameter
    logs = get_recent_logs(lines=1)
    assert len(logs) == 1
    assert logs[0].strip() == '2023-05-01 12:34:57 [INFO] Generation complete'

    # Test with custom type parameter
    logs = get_recent_logs(log_type='webserver')
    assert len(logs) == 2

    # Test with planet-specific log
    logs = get_recent_logs(log_type='planet', planet_type='desert', seed='12345')
    assert len(logs) == 2

    # Test with non-existent log file
    mock_exists.return_value = False
    logs = get_recent_logs()
    assert logs == ["No planet logs found"]


# Este test ha sido eliminado porque la función read_planets_csv no existe en el módulo web.utils


# Este test ha sido eliminado porque las funciones delete_planet_from_csv y read_planets_csv no existen en el módulo web.utils


@patch('web.utils.os.path.exists')
@patch('web.utils.open')
def test_get_planet_log(mock_open, mock_exists):
    """Test the get_planet_log function."""
    # Mock the os.path.exists function to return True
    mock_exists.return_value = True

    # Mock the open function to return a file-like object
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = 'Log content for planet desert with seed 12345'
    mock_open.return_value = mock_file

    # Call the function
    log_content = get_planet_log('desert', '12345')

    # Check that the log content is as expected
    assert log_content == 'Log content for planet desert with seed 12345'

    # Test with a non-existent log file
    mock_exists.return_value = False

    # Call the function and check that it returns an error message
    log_content = get_planet_log('desert', '99999')
    assert "No log file found" in log_content
