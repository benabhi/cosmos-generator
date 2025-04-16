"""
Clean subcommand for the Planet CLI.
Handles the deletion of planet-related output directories.
"""
import argparse
import os
import shutil

from typing import Any, List

import config


def register_subcommand(subparsers: Any) -> None:
    """
    Register the 'clean' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "clean",
        help="Limpiar directorios de salida de planetas",
        description="Elimina archivos y directorios de salida generados para planetas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Optional arguments
    parser.add_argument("--debug", action="store_true",
                       help="Eliminar solo archivos de depuración (texturas, etc.)")
    parser.add_argument("--examples", action="store_true",
                       help="Eliminar solo archivos de ejemplos")
    parser.add_argument("--results", action="store_true",
                       help="Eliminar solo archivos de resultados finales")
    parser.add_argument("--all", action="store_true",
                       help="Eliminar todos los archivos (por defecto si no se especifica ninguna opción)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Mostrar qué archivos se eliminarían sin eliminarlos realmente")


def main(args: argparse.Namespace) -> int:
    """
    Main function for the 'clean' subcommand.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Determine which directories to clean
    clean_debug = args.debug or args.all or not (args.debug or args.examples or args.results)
    clean_examples = args.examples or args.all or not (args.debug or args.examples or args.results)
    clean_results = args.results or args.all or not (args.debug or args.examples or args.results)

    # Base output directory is defined in config.py

    # Initialize counters
    files_removed = 0
    dirs_removed = 0

    # List of directories to clean
    dirs_to_clean: List[str] = []

    # List of individual files to clean
    files_to_clean: List[str] = []

    if clean_debug:
        # Add debug directories to clean
        dirs_to_clean.extend([
            config.PLANETS_CLOUDS_TEXTURES_DIR,
            config.PLANETS_TERRAIN_TEXTURES_DIR
        ])

        # Add log file to files to clean
        log_file = config.PLANETS_LOG_FILE
        if os.path.exists(log_file):
            files_to_clean.append(log_file)

    if clean_examples:
        dirs_to_clean.append(config.PLANETS_EXAMPLES_DIR)

    if clean_results:
        # Get all planet type directories in the result directory
        result_dir = config.PLANETS_RESULT_DIR
        if os.path.exists(result_dir):
            planet_types = [d for d in os.listdir(result_dir)
                           if os.path.isdir(os.path.join(result_dir, d))]
            for planet_type in planet_types:
                dirs_to_clean.append(os.path.join(result_dir, planet_type))

    # Clean individual files
    for file_path in files_to_clean:
        if args.dry_run:
            print(f"Se eliminaría el archivo: {file_path}")
        else:
            try:
                os.remove(file_path)
                print(f"Eliminado el archivo: {file_path}")
                files_removed += 1
            except Exception as e:
                print(f"Error al eliminar el archivo: {e}")

    # Clean the directories

    for directory in dirs_to_clean:
        if os.path.exists(directory):
            if args.dry_run:
                print(f"Se eliminaría el directorio: {directory}")
                # List files that would be removed
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        print(f"  Se eliminaría el archivo: {os.path.join(root, file)}")
                    for dir in dirs:
                        print(f"  Se eliminaría el subdirectorio: {os.path.join(root, dir)}")
            else:
                # Count files before removal
                file_count = sum(len(files) for _, _, files in os.walk(directory))
                dir_count = sum(len(dirs) for _, dirs, _ in os.walk(directory))

                # Remove directory contents but keep the directory structure
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

                files_removed += file_count
                dirs_removed += dir_count
                print(f"Limpiado el directorio: {directory}")

    if not args.dry_run:
        if files_removed > 0 or dirs_removed > 0:
            print(f"Eliminados {files_removed} archivos y {dirs_removed} directorios.")
        else:
            print("No se encontraron archivos para eliminar.")
    else:
        print("\nEste fue un dry-run. No se eliminó ningún archivo.")
        print("Ejecute el comando sin --dry-run para eliminar los archivos.")

    return 0
