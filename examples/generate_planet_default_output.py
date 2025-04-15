#!/usr/bin/env python3
"""
Example script to generate a planet with rings using the default output path.
"""
import os
import sys
import subprocess

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    """
    Generate a desert planet with rings using the default output path.
    """
    # Use the CLI to generate a planet with rings
    cmd = [
        "python", "cosmos_generator/cli.py",
        "--type", "desert",  # Case insensitive
        "--rings",
        "--atmosphere", "0.8",
        "--light-angle", "45"
    ]

    print("Executing command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("\nOutput:")
    print(result.stdout)

    if result.stderr:
        print("\nErrors:")
        print(result.stderr)

    print(f"\nExit code: {result.returncode}")

    # Check if the file was created
    if result.returncode == 0:
        # Extract the path from the output
        output_line = [line for line in result.stdout.split('\n') if line.startswith("Saved to")]
        if output_line:
            path = output_line[0].replace("Saved to ", "").replace(" using container", "").strip()
            print(f"\nVerifying file exists: {path}")
            if os.path.exists(path):
                print(f"Success! File was created at: {path}")
            else:
                print(f"Error: File was not created at: {path}")


if __name__ == "__main__":
    main()
