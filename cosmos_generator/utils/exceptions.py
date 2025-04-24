"""
Custom exceptions for the Cosmos Generator.

This module defines custom exceptions used throughout the application to provide
more specific error information and improve error handling.
"""
from typing import Optional, Dict, Any, List


class CosmosGeneratorError(Exception):
    """Base exception for all Cosmos Generator errors."""
    pass


class ValidationError(CosmosGeneratorError):
    """Exception raised for parameter validation errors."""

    def __init__(self, message: str, errors: Optional[List[Dict[str, str]]] = None):
        """
        Initialize a ValidationError.

        Args:
            message: Error message
            errors: Optional list of validation errors
        """
        self.errors = errors or []
        super().__init__(message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if not self.errors:
            return super().__str__()
        
        error_str = super().__str__() + "\n"
        for error in self.errors:
            for key, value in error.items():
                error_str += f"- {key}: {value}\n"
        return error_str


class PlanetGenerationError(CosmosGeneratorError):
    """Exception raised for errors during planet generation."""

    def __init__(self, message: str, planet_type: Optional[str] = None, seed: Optional[int] = None):
        """
        Initialize a PlanetGenerationError.

        Args:
            message: Error message
            planet_type: Optional planet type
            seed: Optional seed
        """
        self.planet_type = planet_type
        self.seed = seed
        
        # Add context to the message if available
        context = []
        if planet_type:
            context.append(f"type={planet_type}")
        if seed is not None:
            context.append(f"seed={seed}")
            
        if context:
            message = f"{message} ({', '.join(context)})"
            
        super().__init__(message)


class FeatureError(CosmosGeneratorError):
    """Exception raised for errors related to planet features."""

    def __init__(self, message: str, feature: str):
        """
        Initialize a FeatureError.

        Args:
            message: Error message
            feature: Feature name (e.g., 'atmosphere', 'rings', 'clouds')
        """
        self.feature = feature
        super().__init__(f"{feature.capitalize()} error: {message}")


class ResourceNotFoundError(CosmosGeneratorError):
    """Exception raised when a required resource is not found."""

    def __init__(self, resource_type: str, identifier: Any):
        """
        Initialize a ResourceNotFoundError.

        Args:
            resource_type: Type of resource (e.g., 'planet', 'texture')
            identifier: Identifier of the resource (e.g., seed, path)
        """
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type.capitalize()} not found: {identifier}")


class ConfigurationError(CosmosGeneratorError):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize a ConfigurationError.

        Args:
            message: Error message
            config_key: Optional configuration key
        """
        self.config_key = config_key
        
        if config_key:
            message = f"Configuration error for '{config_key}': {message}"
        else:
            message = f"Configuration error: {message}"
            
        super().__init__(message)


class WebInterfaceError(CosmosGeneratorError):
    """Exception raised for errors in the web interface."""

    def __init__(self, message: str, endpoint: Optional[str] = None, status_code: int = 500):
        """
        Initialize a WebInterfaceError.

        Args:
            message: Error message
            endpoint: Optional API endpoint
            status_code: HTTP status code
        """
        self.endpoint = endpoint
        self.status_code = status_code
        
        if endpoint:
            message = f"Web interface error at '{endpoint}': {message}"
        else:
            message = f"Web interface error: {message}"
            
        super().__init__(message)
