#!/usr/bin/env python3
"""
Example script to test the random Ocean style selection in the CLI.
"""
import os
import subprocess

def main():
    """
    Generate multiple Ocean planets using the CLI to test random style selection.
    """
    # Create output directory
    output_dir = "output/planets/examples/test_cli_random_ocean"
    os.makedirs(output_dir, exist_ok=True)

    # Generate 5 Ocean planets with different seeds
    for i in range(5):
        seed = 10000 + i
        output_path = os.path.join(output_dir, f"ocean_{seed}.png")

        # Build the command
        cmd = [
            "python", "-m", "cosmos_generator", "planet",
            "--type", "Ocean",
            "--seed", str(seed),
            "--output", output_path,
            "--atmosphere"  # Add atmosphere for better visualization
        ]

        # Run the command
        print(f"Generating Ocean planet with seed {seed}...")
        subprocess.run(cmd, check=True)
        print(f"Saved to {output_path}")
        print()


if __name__ == "__main__":
    main()
