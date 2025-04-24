#!/usr/bin/env python3
"""
Command-line interface for Cosmos Generator.
This is the main entry point for the CLI, which dispatches to subcommands.
"""
import argparse
import sys
import os
import importlib.util
import importlib
import pkgutil
from typing import Dict, Callable, List, Optional

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


class CosmosGeneratorCLI:
    """
    Main CLI class for Cosmos Generator.
    Handles subcommand registration and dispatching.
    """

    def __init__(self):
        """Initialize the CLI with a parser and subcommand registry."""
        self.parser = argparse.ArgumentParser(
            description="Generate procedural celestial bodies",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.subparsers = self.parser.add_subparsers(
            title="subcommands",
            dest="subcommand",
            help="Subcommand to execute"
        )
        self.subcommands: Dict[str, Callable] = {}

        # Register all available subcommands
        self._discover_subcommands()

        # Add version information
        self.parser.add_argument(
            "--version", action="store_true",
            help="Show version information and exit"
        )

    def _discover_subcommands(self) -> None:
        """
        Automatically discover and register all available subcommands.
        Looks for modules in the 'subcommands' package and registers
        any that have a 'register_subcommand' function.
        """
        try:
            # Import the subcommands package
            from cosmos_generator import subcommands

            # Get the package path
            package_path = os.path.dirname(subcommands.__file__)

            # Iterate through all modules in the package
            for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
                # Skip __init__.py
                if module_name.startswith('_'):
                    continue

                # Import the module
                module = importlib.import_module(f"cosmos_generator.subcommands.{module_name}")

                # Check if the module has a register_subcommand function
                if hasattr(module, 'register_subcommand'):
                    # Register the subcommand
                    module.register_subcommand(self.subparsers)

                    # Store the main function for this subcommand
                    if hasattr(module, 'main'):
                        self.subcommands[module_name] = module.main

            # Manually register the planet subcommand
            try:
                # Import the module directly
                spec = importlib.util.spec_from_file_location(
                    "planet",
                    os.path.join(package_path, "planet.py")
                )
                planet_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(planet_module)

                if hasattr(planet_module, 'register_subcommand'):
                    planet_module.register_subcommand(self.subparsers)
                    if hasattr(planet_module, 'main'):
                        self.subcommands['planet'] = planet_module.main
            except Exception as e:
                print(f"Error importing planet subcommand: {e}")

            # Manually register the web subcommand
            try:
                # Import the module directly
                spec = importlib.util.spec_from_file_location(
                    "web",
                    os.path.join(package_path, "web.py")
                )
                web_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(web_module)

                if hasattr(web_module, 'register_subcommand'):
                    web_module.register_subcommand(self.subparsers)
                    if hasattr(web_module, 'main'):
                        self.subcommands['web'] = web_module.main
            except Exception as e:
                print(f"Error importing web subcommand: {e}")
        except ImportError:
            # If the subcommands package doesn't exist yet, just continue
            pass

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Parse arguments and dispatch to the appropriate subcommand.

        Args:
            args: Command line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code
        """
        parsed_args = self.parser.parse_args(args)

        # Handle version information
        if hasattr(parsed_args, 'version') and parsed_args.version:
            from cosmos_generator import __version__
            print(f"Cosmos Generator v{__version__}")
            return 0

        # If no subcommand was specified, show help
        if not parsed_args.subcommand:
            self.parser.print_help()
            return 1

        # Dispatch to the appropriate subcommand
        if parsed_args.subcommand in self.subcommands:
            return self.subcommands[parsed_args.subcommand](parsed_args)
        else:
            print(f"Error: Unknown subcommand '{parsed_args.subcommand}'")
            self.parser.print_help()
            return 1


def main() -> int:
    """
    Main entry point for the command-line interface.

    Returns:
        Exit code
    """
    cli = CosmosGeneratorCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())