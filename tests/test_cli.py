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
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': None,
            'rings': False,
            'atmosphere': False,
            'clouds': False,
            'cloud_coverage': 0.5,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created
        output_path = os.path.join(config.PLANETS_RESULT_DIR, 'desert', '12345.png')
        assert os.path.exists(output_path)

        # Check that the output file is a valid image
        image = Image.open(output_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_generate_command_with_features(self, temp_output_dir):
        """
        Test planet generation command with features.
        """
        # Create arguments for the generate command
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 54321,
            'output': None,
            'rings': True,
            'atmosphere': True,
            'atmosphere_glow': 0.7,
            'atmosphere_halo': 0.8,
            'atmosphere_thickness': 4,
            'atmosphere_blur': 0.6,
            'clouds': True,
            'cloud_coverage': 0.7,
            'light_intensity': 1.2,
            'light_angle': 30.0,
            'zoom': 0.5,
            'rotation': 45.0,
            'variation': None
        })

        # Run the generate command
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created
        output_path = os.path.join(config.PLANETS_RESULT_DIR, 'desert', '54321.png')
        assert os.path.exists(output_path)

        # Check that the output file is a valid image
        image = Image.open(output_path)
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
            'cloud_coverage': 0.5,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None
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

    def test_clean_command(self, temp_output_dir):
        """
        Test clean command.
        """
        # First, generate a planet to create some files
        generate_args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': None,
            'rings': False,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'cloud_coverage': 0.5,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None
        })

        # Run the generate command
        generate_main(generate_args)

        # Check that files were created
        assert os.path.exists(os.path.join(config.PLANETS_RESULT_DIR, 'desert', '12345.png'))

        # Create arguments for the clean command
        clean_args = type('Args', (), {
            'all': False,
            'debug': False,
            'examples': False,
            'results': True,
            'dry_run': False
        })

        # Run the clean command
        result = clean_main(clean_args)

        # Check that the command was successful
        assert result == 0

        # Check that the result files were deleted
        assert not os.path.exists(os.path.join(config.PLANETS_RESULT_DIR, 'desert', '12345.png'))

        # Check that the debug files still exist
        assert os.path.exists(config.PLANETS_DEBUG_DIR)


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
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'cloud_coverage': 0.5,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': None
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
