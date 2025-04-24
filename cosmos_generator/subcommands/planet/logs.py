"""
Logs subcommand for the Planet CLI.
Handles the display of planet generation logs.
"""
import argparse
from typing import Any

from cosmos_generator.utils.logger import logger


def register_subcommand(subparsers: Any) -> None:
    """
    Register the 'logs' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "logs",
        help="Show planet generation logs",
        description="Display the planet generation logs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Optional arguments
    parser.add_argument("--lines", type=int, default=None,
                       help="Number of lines to show (default: all)")
    parser.add_argument("--tail", type=int, default=None,
                       help="Show the last N lines")
    # Removed --summary argument as the summary is now automatically included in the log
    parser.add_argument("--path", action="store_true",
                       help="Show the log file path")
    parser.add_argument("--level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       default=None, help="Filter logs by minimum level")


def main(args: argparse.Namespace) -> int:
    """
    Main function for the 'logs' subcommand.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # If path flag is set, just show the log file path
    if args.path:
        print(f"Log file: {logger.log_file}")
        return 0

    # Summary is now automatically included in the log file after each generation

    # Determine number of lines to show
    lines = None
    if args.tail is not None:
        lines = args.tail
    elif args.lines is not None:
        lines = args.lines

    # Get log content
    log_lines = logger.get_log_file_content(lines)

    if not log_lines:
        print("No logs available or log file does not exist.")
        print(f"Log file: {logger.log_file}")
        return 0

    # Filter by level if specified
    if args.level:
        filtered_lines = []
        level_hierarchy = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        requested_level = level_hierarchy.get(args.level, 0)

        for line in log_lines:
            # Check each level to see if it's in the line
            for level, value in level_hierarchy.items():
                if f"[{level}]" in line and value >= requested_level:
                    filtered_lines.append(line)
                    break

        log_lines = filtered_lines

        if not log_lines:
            print(f"No logs with level {args.level} or higher.")
            return 0

    # Print log content
    for line in log_lines:
        print(line.rstrip())

    return 0
