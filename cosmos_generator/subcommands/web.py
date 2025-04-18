"""
Web interface subcommand for Cosmos Generator.
"""
from cosmos_generator.subcommands.web.web_command import setup_parser, run_web_interface


def register_subcommand(subparsers):
    """
    Register the web subcommand.
    
    Args:
        subparsers: Subparsers object from the main parser
    """
    setup_parser(subparsers)


def main(args):
    """
    Main entry point for the web subcommand.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    return run_web_interface(args)
