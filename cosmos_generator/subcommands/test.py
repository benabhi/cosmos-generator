"""
Test subcommand for the Cosmos Generator CLI.
This is the main entry point for running tests.
"""
import argparse
import os
import sys
import subprocess


def register_subcommand(subparsers):
    """
    Register the 'test' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "test",
        help="Run tests for the Cosmos Generator",
        description="Run unit tests to verify the functionality of the Cosmos Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Add arguments for the test command
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--test-path",
        type=str,
        default="tests",
        help="Path to the test directory or specific test file"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default=None,
        help="Pattern to match test files (e.g., 'test_*.py')"
    )


def main(args):
    """
    Main function for the 'test' subcommand.
    Runs the tests using pytest.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Build the pytest command
    pytest_args = [sys.executable, "-m", "pytest"]
    
    # Add verbose flag if requested
    if args.verbose:
        pytest_args.append("-v")
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(["--cov=cosmos_generator", "--cov-report=term", "--cov-report=html"])
    
    # Add test path
    pytest_args.append(args.test_path)
    
    # Add pattern if provided
    if args.pattern:
        pytest_args.append(args.pattern)
    
    # Print the command being run
    print(f"Running: {' '.join(pytest_args)}")
    
    # Run the tests
    try:
        result = subprocess.run(pytest_args, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1
