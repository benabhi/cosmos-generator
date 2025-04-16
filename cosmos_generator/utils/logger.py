"""
Logger module for Cosmos Generator.

Provides a centralized logging system for the application.
"""
import os
import logging
import datetime
from typing import Optional, Dict, Any, List

import config
from cosmos_generator.utils.directory_utils import ensure_directory_exists, ensure_file_directory


class CosmosLogger:
    """
    Logger class for Cosmos Generator.

    Provides methods for logging messages with different levels and formatting.
    """

    # Singleton instance
    _instance = None

    # ANSI color codes for terminal output
    COLORS = {
        'RESET': '\033[0m',
        'BLACK': '\033[30m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
    }

    def __new__(cls, *args, **kwargs):
        """
        Create a singleton instance of the logger.
        """
        if cls._instance is None:
            cls._instance = super(CosmosLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_file: Optional[str] = None, console_level: int = logging.INFO):
        """
        Initialize the logger.

        Args:
            log_file: Path to the log file
            console_level: Logging level for console output
        """
        if self._initialized:
            return

        self._initialized = True

        # Set default log file if not provided
        if log_file is None:
            log_file = config.PLANETS_LOG_FILE

        # Ensure the log directory exists
        ensure_file_directory(log_file)

        # Create logger
        self.logger = logging.getLogger("cosmos_generator")
        self.logger.setLevel(logging.DEBUG)

        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)

        # Create console handler - only show INFO and higher in console by default
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(console_level)

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )

        # Set formatters
        file_handler.setFormatter(file_formatter)
        self.console_handler.setFormatter(console_formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(self.console_handler)

        # Store handlers for later use
        self.file_handler = file_handler

        # Store log file path
        self.log_file = log_file

        # Initialize generation context
        self.generation_context = {}

    def debug(self, message: str, component: str = "general") -> None:
        """
        Log a debug message.

        Args:
            message: Message to log
            component: Component name
        """
        self.logger.debug(f"[{component}] {message}")

    def info(self, message: str, component: str = "general", console: bool = True) -> None:
        """
        Log an info message.

        Args:
            message: Message to log
            component: Component name
            console: Whether to log to console
        """
        formatted_message = f"[{component}] {message}"
        if console:
            self.logger.info(formatted_message)
        else:
            # Log only to file by temporarily changing console handler level
            current_level = self.console_handler.level
            self.console_handler.setLevel(logging.WARNING)  # Higher than INFO
            self.logger.info(formatted_message)
            self.console_handler.setLevel(current_level)

    def warning(self, message: str, component: str = "general") -> None:
        """
        Log a warning message.

        Args:
            message: Message to log
            component: Component name
        """
        self.logger.warning(f"[{component}] {message}")

    def error(self, message: str, component: str = "general", exc_info: bool = False) -> None:
        """
        Log an error message.

        Args:
            message: Message to log
            component: Component name
            exc_info: Whether to include exception info
        """
        self.logger.error(f"[{component}] {message}", exc_info=exc_info)

    def critical(self, message: str, component: str = "general", exc_info: bool = True) -> None:
        """
        Log a critical message.

        Args:
            message: Message to log
            component: Component name
            exc_info: Whether to include exception info
        """
        self.logger.critical(f"[{component}] {message}", exc_info=exc_info)

    def start_generation(self, planet_type: str, seed: int, params: Dict[str, Any]) -> None:
        """
        Log the start of a planet generation process.

        Args:
            planet_type: Type of planet
            seed: Random seed
            params: Generation parameters
        """
        self.generation_context = {
            "planet_type": planet_type,
            "seed": seed,
            "start_time": datetime.datetime.now(),
            "params": params,
            "steps": [],
        }

        # Format parameters for logging
        params_str = "\n".join([f"    {k}: {v}" for k, v in params.items()])

        # Log generation start - only to file, not to console
        self.info(f"Starting generation of {planet_type} planet with seed {seed}", "generator", console=False)
        self.debug(f"Generation parameters:\n{params_str}", "generator")

    def log_step(self, step_name: str, duration_ms: float, details: Optional[str] = None) -> None:
        """
        Log a generation step.

        Args:
            step_name: Name of the step
            duration_ms: Duration in milliseconds
            details: Additional details
        """
        if not self.generation_context:
            return

        # Add step to context
        self.generation_context["steps"].append({
            "name": step_name,
            "duration_ms": duration_ms,
            "details": details,
        })

        # Log step
        if details:
            self.debug(f"Step '{step_name}' completed in {duration_ms:.2f}ms - {details}", "generator")
        else:
            self.debug(f"Step '{step_name}' completed in {duration_ms:.2f}ms", "generator")

    def end_generation(self, success: bool, output_path: Optional[str] = None, error: Optional[str] = None) -> None:
        """
        Log the end of a planet generation process.

        Args:
            success: Whether generation was successful
            output_path: Path to the output file
            error: Error message if generation failed
        """
        if not self.generation_context:
            return

        # Calculate total duration
        end_time = datetime.datetime.now()
        start_time = self.generation_context["start_time"]
        duration = (end_time - start_time).total_seconds() * 1000  # in milliseconds

        # Add end info to context
        self.generation_context["end_time"] = end_time
        self.generation_context["duration_ms"] = duration
        self.generation_context["success"] = success

        if output_path:
            self.generation_context["output_path"] = output_path

        if error:
            self.generation_context["error"] = error

        # Log generation end
        planet_type = self.generation_context["planet_type"]
        seed = self.generation_context["seed"]

        if success:
            # Log to file only, not to console (to avoid redundancy)
            self.info(f"Successfully generated {planet_type} planet with seed {seed} in {duration:.2f}ms", "generator", console=False)
            if output_path:
                self.info(f"Saved to {output_path}", "generator", console=False)
        else:
            self.error(f"Failed to generate {planet_type} planet with seed {seed} after {duration:.2f}ms", "generator")
            if error:
                self.error(f"Error: {error}", "generator")

        # Log step summary
        if self.generation_context["steps"]:
            steps_str = "\n".join([
                f"    {step['name']}: {step['duration_ms']:.2f}ms{' - ' + step['details'] if step['details'] else ''}"
                for step in self.generation_context["steps"]
            ])
            self.debug(f"Generation steps summary:\n{steps_str}", "generator")

        # Clear context
        self.generation_context = {}

    def get_log_file_content(self, lines: Optional[int] = None) -> List[str]:
        """
        Get the content of the log file.

        Args:
            lines: Number of lines to return (None for all)

        Returns:
            List of log lines
        """
        if not os.path.exists(self.log_file):
            # Ensure the log directory exists in case it was deleted
            ensure_file_directory(self.log_file)
            return []

        with open(self.log_file, 'r') as f:
            all_lines = f.readlines()

        # If we're returning all lines, just return them
        if lines is None:
            return all_lines

        # Otherwise, return the last N lines
        return all_lines[-lines:]


# Create a singleton instance
logger = CosmosLogger()
