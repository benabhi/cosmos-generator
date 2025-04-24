#!/usr/bin/env python3
"""
Test script for the CLI functionality.
"""
import os
import sys
import pytest
from unittest.mock import patch
from PIL import Image

import config
from cosmos_generator.cli import CosmosGeneratorCLI
from cosmos_generator.subcommands.planet.generate import main as generate_main
from cosmos_generator.subcommands.planet.clean import main as clean_main
from cosmos_generator.subcommands.planet.logs import main as logs_main


class TestCLI:
    """
    Test cases for the CLI.
    """

    def test_cli_initialization(self):
        """
        Test CLI initialization.
        """
        # Create a CLI instance
        cli = CosmosGeneratorCLI()

        # Check that the CLI was initialized
        assert cli is not None
        assert cli.parser is not None
        assert cli.subparsers is not None
        assert cli.subcommands is not None

    @patch('sys.argv', ['cosmos_generator', '--version'])
    def test_cli_version(self, capsys):
        """
        Test CLI version command.
        """
        # Create a CLI instance
        cli = CosmosGeneratorCLI()

        # Run the CLI with the version flag
        result = cli.run(['--version'])

        # Check that the exit code is 0 (success)
        assert result == 0

        # Check that the version was printed
        captured = capsys.readouterr()
        assert "Cosmos Generator" in captured.out

    @patch('sys.argv', ['cosmos_generator'])
    def test_cli_help(self, capsys):
        """
        Test CLI help command.
        """
        # Create a CLI instance
        cli = CosmosGeneratorCLI()

        # Run the CLI with no arguments (should show help)
        result = cli.run([])

        # Check that the exit code is 1 (error, no subcommand specified)
        assert result == 1

        # Check that the help was printed
        captured = capsys.readouterr()
        assert "usage:" in captured.out
        assert "subcommands:" in captured.out


class TestPlanetGenerateCommand:
    """
    Test cases for the 'planet generate' command.
    """

    def test_generate_command_basic(self, temp_output_dir):
        """
        Test basic planet generation command.
        """
        # Clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': None,
            'rings': False,
            'rings_complexity': None,
            'rings_tilt': None,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created in the new directory structure
        seed_str = '00012345'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planet image exists
        planet_image_path = os.path.join(planet_dir, 'planet.png')
        assert os.path.exists(planet_image_path), f"Planet image {planet_image_path} not found"

        # Check that the terrain texture exists
        terrain_texture_path = os.path.join(planet_dir, 'terrain_texture.png')
        assert os.path.exists(terrain_texture_path), f"Terrain texture {terrain_texture_path} not found"

        # Check that the planets.csv file exists
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV {config.PLANETS_CSV} not found"

        # Check that the planet is in the planets.csv file
        with open(config.PLANETS_CSV, 'r') as f:
            csv_content = f.read()
            assert seed_str in csv_content, f"Seed {seed_str} not found in planets.csv"

        # Check that the planet.log file exists
        planet_log_path = os.path.join(planet_dir, 'planet.log')
        assert os.path.exists(planet_log_path), f"Planet log {planet_log_path} not found"

        # Open and check the image
        image = Image.open(planet_image_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_generate_command_with_features(self, temp_output_dir):
        """
        Test planet generation command with features.
        """
        # Clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 54321,
            'output': None,
            'rings': True,
            'rings_complexity': None,  # Permitir que se elija aleatoriamente
            'rings_tilt': None,  # Permitir que se elija aleatoriamente
            'atmosphere': True,
            'atmosphere_glow': 0.7,
            'atmosphere_halo': 0.8,
            'atmosphere_thickness': 4,
            'atmosphere_blur': 0.6,
            'clouds': True,
            'clouds_coverage': 0.7,
            'light_intensity': 1.2,
            'light_angle': 30.0,
            'zoom': 0.5,
            'rotation': 45.0,
            'variation': None,
            'color_palette_id': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created in the new directory structure
        seed_str = '00054321'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planet image exists
        planet_image_path = os.path.join(planet_dir, 'planet.png')
        assert os.path.exists(planet_image_path), f"Planet image {planet_image_path} not found"

        # Check that the terrain texture exists
        terrain_texture_path = os.path.join(planet_dir, 'terrain_texture.png')
        assert os.path.exists(terrain_texture_path), f"Terrain texture {terrain_texture_path} not found"

        # Check that the planets.csv file exists
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV {config.PLANETS_CSV} not found"

        # Check that the planet is in the planets.csv file
        with open(config.PLANETS_CSV, 'r') as f:
            csv_content = f.read()
            assert seed_str in csv_content, f"Seed {seed_str} not found in planets.csv"

        # Check that the planet.log file exists
        planet_log_path = os.path.join(planet_dir, 'planet.log')
        assert os.path.exists(planet_log_path), f"Planet log {planet_log_path} not found"

        # Open and check the image
        image = Image.open(planet_image_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_generate_command_with_color_palette_id(self, temp_output_dir):
        """
        Test planet generation command with color palette ID.
        """
        # Clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 67890,
            'output': None,
            'rings': False,
            'rings_complexity': None,
            'rings_tilt': None,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': 2  # Specify color palette ID
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created in the new directory structure
        seed_str = '00067890'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planet image exists
        planet_image_path = os.path.join(planet_dir, 'planet.png')
        assert os.path.exists(planet_image_path), f"Planet image {planet_image_path} not found"

        # Check that the terrain texture exists
        terrain_texture_path = os.path.join(planet_dir, 'terrain_texture.png')
        assert os.path.exists(terrain_texture_path), f"Terrain texture {terrain_texture_path} not found"

        # Check that the planets.csv file exists
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV {config.PLANETS_CSV} not found"

        # Check that the planet is in the planets.csv file
        with open(config.PLANETS_CSV, 'r') as f:
            csv_content = f.read()
            assert seed_str in csv_content, f"Seed {seed_str} not found in planets.csv"

        # Check that the planet.log file exists
        planet_log_path = os.path.join(planet_dir, 'planet.log')
        assert os.path.exists(planet_log_path), f"Planet log {planet_log_path} not found"

        # Open and check the image
        image = Image.open(planet_image_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_generate_command_with_rings_parameters(self, temp_output_dir):
        """
        Test planet generation command with specific rings parameters.
        """
        # Clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 78901,
            'output': None,
            'rings': True,  # Enable rings
            'rings_complexity': 3,  # Full complexity
            'rings_tilt': 45.0,  # 45 degree tilt
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created in the new directory structure
        seed_str = '00078901'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planet image exists
        planet_image_path = os.path.join(planet_dir, 'planet.png')
        assert os.path.exists(planet_image_path), f"Planet image {planet_image_path} not found"

        # Check that the terrain texture exists
        terrain_texture_path = os.path.join(planet_dir, 'terrain_texture.png')
        assert os.path.exists(terrain_texture_path), f"Terrain texture {terrain_texture_path} not found"

        # Check that the planets.csv file exists
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV {config.PLANETS_CSV} not found"

        # Check that the planet is in the planets.csv file
        with open(config.PLANETS_CSV, 'r') as f:
            csv_content = f.read()
            assert seed_str in csv_content, f"Seed {seed_str} not found in planets.csv"

        # Check that the planet.log file exists
        planet_log_path = os.path.join(planet_dir, 'planet.log')
        assert os.path.exists(planet_log_path), f"Planet log {planet_log_path} not found"

        # Open and check the image
        image = Image.open(planet_image_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_generate_command_with_custom_output(self, temp_output_dir):
        """
        Test planet generation command with custom output path.
        """
        # Create a custom output path
        custom_output = os.path.join(temp_output_dir, 'custom_output.png')

        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': custom_output,
            'rings': False,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created
        assert os.path.exists(custom_output)

        # Check that the output file is a valid image
        image = Image.open(custom_output)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"


class TestPlanetCommand:
    """
    Test cases for the 'planet' command with direct options.
    """

    def test_list_types_command(self, capsys):
        """
        Test 'planet --list-types' command.
        """
        # Use the CLI directly
        from cosmos_generator.cli import CosmosGeneratorCLI
        cli = CosmosGeneratorCLI()

        # Run the CLI with the list-types flag
        result = cli.run(['planet', '--list-types'])

        # Check that the command was successful
        assert result == 0

        # Check that the types were printed
        captured = capsys.readouterr()
        assert "Available planet types:" in captured.out
        assert "Desert" in captured.out
        assert "Ocean" in captured.out

    def test_list_variations_command(self, capsys):
        """
        Test 'planet --list-variations' command.
        """
        # Use the CLI directly
        from cosmos_generator.cli import CosmosGeneratorCLI
        cli = CosmosGeneratorCLI()

        # Run the CLI with the list-variations flag
        result = cli.run(['planet', '--list-variations'])

        # Check that the command was successful
        assert result == 0

        # Check that the variations were printed
        captured = capsys.readouterr()
        assert "Available variations for each planet type:" in captured.out
        assert "Desert:" in captured.out
        assert "Ocean:" in captured.out
        assert "default" in captured.out


class TestPlanetCleanCommand:
    """
    Test cases for the 'planet clean' command.
    """

    def test_clean_all_command(self, temp_output_dir):
        """
        Test 'planet clean --all' command.
        """
        # First, clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)

        # Then generate a new planet
        generate_args = type('Args', (), {
            'type': 'Desert',
            'seed': 54321,
            'output': None,
            'rings': False,
            'rings_complexity': None,
            'rings_tilt': None,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': None
        })

        # Run the generate command
        generate_main(generate_args)

        # Check that the output file was created in the new directory structure
        seed_str = '00054321'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planet image exists
        planet_image_path = os.path.join(planet_dir, 'planet.png')
        assert os.path.exists(planet_image_path), f"Planet image {planet_image_path} not found"

        # Check that the planets.csv file exists
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV file {config.PLANETS_CSV} not found"

        # Create arguments for the clean command
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })

        # Run the clean command
        result = clean_main(clean_args)

        # Check that the command was successful
        assert result == 0

        # Check that the planet directory was deleted
        assert not os.path.exists(planet_dir), f"Planet directory {planet_dir} was not deleted"

        # Check that the planets.csv file still exists but is empty (only header)
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV file {config.PLANETS_CSV} was deleted"
        with open(config.PLANETS_CSV, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1, f"Planets CSV file should only contain the header, but contains {len(lines)} lines"
            assert 'seed,planet_type,variation,atmosphere,rings,clouds' in lines[0], f"Planets CSV file header is incorrect"

    def test_clean_seeds_command(self, temp_output_dir):
        """
        Test 'planet clean --seeds' command.
        """
        # First, clean all existing planets
        clean_args = type('Args', (), {
            'all': True,
            'seeds': None
        })
        clean_main(clean_args)

        # Generate two planets
        for seed, planet_type in [(12345, 'Desert'), (67890, 'Ocean')]:
            generate_args = type('Args', (), {
                'type': planet_type,
                'seed': seed,
                'output': None,
                'rings': False,
                'rings_complexity': None,
                'rings_tilt': None,
                'atmosphere': False,
                'atmosphere_glow': 0.5,
                'atmosphere_halo': 0.7,
                'atmosphere_thickness': 3,
                'atmosphere_blur': 0.5,
                'clouds': False,
                'clouds_coverage': 0.5,
                'light_intensity': 1.0,
                'light_angle': 45.0,
                'zoom': None,
                'rotation': 0.0,
                'variation': None,
                'color_palette_id': None
            })

            # Run the generate command
            generate_main(generate_args)

        # Check that both planet directories exist
        desert_dir = os.path.join(config.PLANETS_DIR, 'desert', '00012345')
        ocean_dir = os.path.join(config.PLANETS_DIR, 'ocean', '00067890')
        assert os.path.exists(desert_dir), f"Desert planet directory {desert_dir} not found"
        assert os.path.exists(ocean_dir), f"Ocean planet directory {ocean_dir} not found"

        # Check that the planets.csv file exists and contains both planets
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV file {config.PLANETS_CSV} not found"
        with open(config.PLANETS_CSV, 'r') as f:
            content = f.read()
            assert '00012345' in content, f"Desert planet seed not found in planets.csv"
            assert '00067890' in content, f"Ocean planet seed not found in planets.csv"

        # Create arguments for the clean command to remove only the desert planet
        clean_args = type('Args', (), {
            'all': False,
            'seeds': '12345'
        })

        # Run the clean command
        result = clean_main(clean_args)

        # Check that the command was successful
        assert result == 0

        # Check that the desert planet directory was deleted
        assert not os.path.exists(desert_dir), f"Desert planet directory {desert_dir} was not deleted"

        # Check that the ocean planet directory still exists
        assert os.path.exists(ocean_dir), f"Ocean planet directory {ocean_dir} was unexpectedly deleted"

        # Check that the planets.csv file still exists and contains only the ocean planet
        assert os.path.exists(config.PLANETS_CSV), f"Planets CSV file {config.PLANETS_CSV} was deleted"
        with open(config.PLANETS_CSV, 'r') as f:
            content = f.read()
            assert '00012345' not in content, f"Desert planet seed still found in planets.csv"
            assert '00067890' in content, f"Ocean planet seed not found in planets.csv"


class TestPlanetLogsCommand:
    """
    Test cases for the 'planet logs' command.
    """

    def test_logs_command(self, temp_output_dir, capsys):
        """
        Test logs command.
        """
        # First, generate a planet to create some logs
        generate_args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': None,
            'rings': False,
            'rings_complexity': None,
            'rings_tilt': None,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': None,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None,
            'color_palette_id': None
        })

        # Ensure the log directory exists
        from cosmos_generator.utils.directory_utils import ensure_directory_exists
        ensure_directory_exists(os.path.dirname(config.PLANETS_LOG_FILE))

        # Create a log file manually
        with open(config.PLANETS_LOG_FILE, 'w') as f:
            f.write("2025-04-17 18:00:00 [INFO] cosmos_generator: [cli] Test log entry\n")

        # Run the generate command
        generate_main(generate_args)

        # Check that the log file exists
        assert os.path.exists(config.PLANETS_LOG_FILE)

        # Create arguments for the logs command
        logs_args = type('Args', (), {
            'tail': 10,
            'head': None,
            'grep': None,
            'path': False,
            'level': None,
            'lines': None
        })

        # Run the logs command
        result = logs_main(logs_args)

        # Check that the command was successful
        assert result == 0

        # Check that logs were printed
        captured = capsys.readouterr()
        assert captured.out  # Output should not be empty
