"""
Planet subcommand for the Cosmos Generator CLI.
This is the main entry point for planet-related commands.
"""
import argparse
import os
import sys
import importlib
import pkgutil
from typing import Dict, Callable, Any, Optional, List

# Try to import the required modules
try:
    from cosmos_generator.core.planet_generator import PlanetGenerator
except ImportError:
    # Try with direct imports if the package structure import fails
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    from core.planet_generator import PlanetGenerator


def register_subcommand(subparsers: Any) -> None:
    """
    Register the 'planet' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "planet",
        help="Comandos relacionados con planetas",
        description="Genera y gestiona planetas procedurales",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # List available planet types and variations
    parser.add_argument("--list-types", action="store_true",
                       help="List available planet types")
    parser.add_argument("--list-variations", action="store_true",
                       help="List available variations for each planet type")

    # Create subparsers for planet subcommands
    planet_subparsers = parser.add_subparsers(
        title="subcommands",
        dest="planet_subcommand",
        help="Subcomando de planet a ejecutar"
    )

    # Register all available planet subcommands
    _discover_planet_subcommands(planet_subparsers)


def _discover_planet_subcommands(subparsers: Any) -> Dict[str, Callable]:
    """
    Automatically discover and register all available planet subcommands.
    Looks for modules in the 'subcommands/planet' package and registers
    any that have a 'register_subcommand' function.

    Args:
        subparsers: Subparsers object from argparse

    Returns:
        Dictionary mapping subcommand names to their main functions
    """
    subcommands: Dict[str, Callable] = {}

    try:
        # Get the package path
        package_path = os.path.join(os.path.dirname(__file__), "planet")

        # Iterate through all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
            # Skip __init__.py
            if module_name.startswith('_'):
                continue

            # Import the module
            module = importlib.import_module(f"cosmos_generator.subcommands.planet.{module_name}")

            # Check if the module has a register_subcommand function
            if hasattr(module, 'register_subcommand'):
                # Register the subcommand
                module.register_subcommand(subparsers)

                # Store the main function for this subcommand
                if hasattr(module, 'main'):
                    subcommands[module_name] = module.main
    except ImportError as e:
        # If there's an import error, print it for debugging
        print(f"Error importing planet subcommands: {e}")
        pass

    return subcommands


def main(args: argparse.Namespace) -> int:
    """
    Main function for the 'planet' subcommand.
    Dispatches to the appropriate planet subcommand.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Handle list-types and list-variations at the planet level
    if hasattr(args, 'list_types') and args.list_types:
        # Import here to avoid circular imports
        import config
        from cosmos_generator.core.planet_generator import PlanetGenerator

        # Create planet generator
        generator = PlanetGenerator()

        print("Available planet types:")
        for planet_type in generator.get_celestial_types():
            print(f"  - {planet_type}")
        return 0

    if hasattr(args, 'list_variations') and args.list_variations:
        # Import here to avoid circular imports
        import config

        print("Available variations for each planet type:")
        for planet_type, variations in config.PLANET_VARIATIONS.items():
            default_variation = config.DEFAULT_PLANET_VARIATIONS.get(planet_type, "")
            print(f"  {planet_type.title()}:")
            for variation in variations:
                if variation == default_variation:
                    print(f"    - {variation} (default)")
                else:
                    print(f"    - {variation}")
        return 0

    # If no planet subcommand was specified, show help
    if not hasattr(args, 'planet_subcommand') or not args.planet_subcommand:
        # Try to get the parser from the args
        if hasattr(args, '_parser'):
            args._parser.print_help()
        else:
            print("Error: No planet subcommand specified")
            print("Available subcommands: generate, clean")
        return 1

    # Create a temporary parser to discover subcommands
    temp_parser = argparse.ArgumentParser()
    temp_subparsers = temp_parser.add_subparsers()
    planet_subcommands = _discover_planet_subcommands(temp_subparsers)

    # Dispatch to the appropriate planet subcommand
    if args.planet_subcommand in planet_subcommands:
        return planet_subcommands[args.planet_subcommand](args)
    else:
        print(f"Error: Unknown planet subcommand '{args.planet_subcommand}'")
        print("Available subcommands:", ", ".join(planet_subcommands.keys()))
        return 1
