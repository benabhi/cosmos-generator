"""
Main entry point for the Cosmos Generator package.
This allows the package to be run as a module: python -m cosmos_generator
"""
import sys
from cosmos_generator.cli import main

if __name__ == "__main__":
    sys.exit(main())
