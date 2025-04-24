"""
Parameter validation utilities.

This module provides utilities for validating parameters used throughout the application.
It centralizes validation logic to ensure consistency and reduce code duplication.
"""
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import re
from cosmos_generator.core.interfaces import ValidationResult, ValidationError, ParamValue, ParamDict


def validate_numeric_param(
    value: Any,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    allow_none: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Validate a numeric parameter.

    Args:
        value: The value to validate
        min_val: Optional minimum value (inclusive)
        max_val: Optional maximum value (inclusive)
        allow_none: Whether None is an acceptable value

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if None is allowed
    if value is None:
        if allow_none:
            return True, None
        return False, "Value cannot be None"

    # Try to convert to float
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        return False, f"Value must be a number, got {type(value).__name__}"

    # Check min value
    if min_val is not None and float_value < min_val:
        return False, f"Value must be at least {min_val}, got {float_value}"

    # Check max value
    if max_val is not None and float_value > max_val:
        return False, f"Value must be at most {max_val}, got {float_value}"

    return True, None


def validate_string_param(
    value: Any,
    allowed_values: Optional[List[str]] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    allow_none: bool = False,
    case_sensitive: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Validate a string parameter.

    Args:
        value: The value to validate
        allowed_values: Optional list of allowed values
        min_length: Optional minimum length
        max_length: Optional maximum length
        pattern: Optional regex pattern
        allow_none: Whether None is an acceptable value
        case_sensitive: Whether to perform case-sensitive validation for allowed_values

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if None is allowed
    if value is None:
        if allow_none:
            return True, None
        return False, "Value cannot be None"

    # Check type
    if not isinstance(value, str):
        return False, f"Value must be a string, got {type(value).__name__}"

    # Check allowed values
    if allowed_values:
        if case_sensitive:
            if value not in allowed_values:
                return False, f"Value must be one of {allowed_values}, got '{value}'"
        else:
            if value.lower() not in [v.lower() for v in allowed_values]:
                return False, f"Value must be one of {allowed_values} (case insensitive), got '{value}'"

    # Check min length
    if min_length is not None and len(value) < min_length:
        return False, f"Value must be at least {min_length} characters, got {len(value)}"

    # Check max length
    if max_length is not None and len(value) > max_length:
        return False, f"Value must be at most {max_length} characters, got {len(value)}"

    # Check pattern
    if pattern and not re.match(pattern, value):
        return False, f"Value must match pattern '{pattern}', got '{value}'"

    return True, None


def validate_boolean_param(
    value: Any,
    allow_none: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Validate a boolean parameter.

    Args:
        value: The value to validate
        allow_none: Whether None is an acceptable value

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if None is allowed
    if value is None:
        if allow_none:
            return True, None
        return False, "Value cannot be None"

    # Check if it's a boolean
    if not isinstance(value, bool):
        # Check if it's a string representation of a boolean
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ('true', 'false', '1', '0', 'yes', 'no'):
                return True, None
        # Check if it's a numeric representation of a boolean
        elif isinstance(value, (int, float)):
            if value in (0, 1):
                return True, None
        return False, f"Value must be a boolean, got {type(value).__name__}"

    return True, None


def validate_seed(
    value: Any,
    allow_none: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Validate a seed parameter.

    Args:
        value: The value to validate
        allow_none: Whether None is an acceptable value

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if None is allowed
    if value is None:
        if allow_none:
            return True, None
        return False, "Seed cannot be None"

    # If it's a string, check if it's a valid integer
    if isinstance(value, str):
        try:
            int(value)
            return True, None
        except ValueError:
            return False, f"Seed must be a valid integer, got '{value}'"

    # If it's an integer, it's valid
    if isinstance(value, int):
        return True, None

    # If it's a float, check if it's an integer
    if isinstance(value, float):
        if value.is_integer():
            return True, None
        return False, f"Seed must be an integer, got {value}"

    return False, f"Seed must be an integer, got {type(value).__name__}"


def validate_planet_params(params: Dict[str, Any]) -> ValidationResult:
    """
    Validate parameters for planet generation.

    Args:
        params: Dictionary of parameters to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate planet type
    if 'type' in params:
        is_valid, error = validate_string_param(
            params['type'],
            allow_none=False
        )
        if not is_valid:
            errors.append({"type": error})

    # Validate seed
    if 'seed' in params:
        is_valid, error = validate_seed(params['seed'])
        if not is_valid:
            errors.append({"seed": error})

    # Validate variation
    if 'variation' in params:
        is_valid, error = validate_string_param(
            params['variation'],
            allow_none=True
        )
        if not is_valid:
            errors.append({"variation": error})

    # Validate boolean parameters
    for param_name in ['rings', 'atmosphere']:
        if param_name in params:
            is_valid, error = validate_boolean_param(
                params[param_name],
                allow_none=True
            )
            if not is_valid:
                errors.append({param_name: error})

    # Validate clouds parameter (can be boolean or numeric)
    if 'clouds' in params:
        # If it's a boolean, validate as boolean
        if isinstance(params['clouds'], bool):
            is_valid, error = validate_boolean_param(
                params['clouds'],
                allow_none=True
            )
        # If it's not a boolean, validate as numeric (for cloud coverage)
        else:
            is_valid, error = validate_numeric_param(
                params['clouds'],
                min_val=0.0,
                max_val=1.0,
                allow_none=True
            )
        if not is_valid:
            errors.append({"clouds": error})

    # Validate numeric parameters with ranges
    numeric_params = [
        ('atmosphere_glow', 0.0, 1.0),
        ('atmosphere_halo', 0.0, 1.0),
        ('atmosphere_thickness', 1, 10),
        ('atmosphere_blur', 0.0, 1.0),
        ('cloud_coverage', 0.0, 1.0),
        ('light_intensity', 0.1, 2.0),
        ('light_angle', 0, 360),
        ('rotation', 0, 360),
        ('zoom', 0.0, 1.0),
        ('rings_complexity', 1, 5),
        ('rings_tilt', -45, 45)
    ]

    for param_name, min_val, max_val in numeric_params:
        if param_name in params:
            is_valid, error = validate_numeric_param(
                params[param_name],
                min_val=min_val,
                max_val=max_val,
                allow_none=True
            )
            if not is_valid:
                errors.append({param_name: error})

    return len(errors) == 0, errors if errors else None


def convert_param_value(value: Any, param_type: str) -> ParamValue:
    """
    Convert a parameter value to the appropriate type.

    Args:
        value: The value to convert
        param_type: The type to convert to ('numeric', 'boolean', 'string')

    Returns:
        Converted value
    """
    if value is None:
        return None

    if param_type == 'numeric':
        try:
            # Try to convert to int if it's a whole number
            float_value = float(value)
            if float_value.is_integer():
                return int(float_value)
            return float_value
        except (ValueError, TypeError):
            return value  # Return as is if conversion fails

    elif param_type == 'boolean':
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ('true', 'yes', '1'):
                return True
            if lower_value in ('false', 'no', '0'):
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        return value  # Return as is if conversion fails

    elif param_type == 'string':
        return str(value)

    return value  # Return as is for unknown types


def sanitize_planet_params(params: Dict[str, Any]) -> ParamDict:
    """
    Sanitize and convert planet parameters to the appropriate types.

    Args:
        params: Dictionary of parameters to sanitize

    Returns:
        Sanitized parameters
    """
    sanitized = {}

    # String parameters
    string_params = ['type', 'variation', 'color_palette_id']
    for param in string_params:
        if param in params and params[param] is not None:
            sanitized[param] = convert_param_value(params[param], 'string')

    # Boolean parameters
    boolean_params = ['rings', 'atmosphere']
    for param in boolean_params:
        if param in params and params[param] is not None:
            sanitized[param] = convert_param_value(params[param], 'boolean')

    # Handle clouds parameter (can be boolean or numeric)
    if 'clouds' in params and params['clouds'] is not None:
        if isinstance(params['clouds'], bool):
            sanitized['clouds'] = convert_param_value(params['clouds'], 'boolean')
        else:
            sanitized['clouds'] = convert_param_value(params['clouds'], 'numeric')

    # Numeric parameters
    numeric_params = [
        'seed', 'atmosphere_glow', 'atmosphere_halo', 'atmosphere_thickness',
        'atmosphere_blur', 'cloud_coverage', 'light_intensity', 'light_angle',
        'rotation', 'zoom', 'rings_complexity', 'rings_tilt'
    ]
    for param in numeric_params:
        if param in params and params[param] is not None:
            sanitized[param] = convert_param_value(params[param], 'numeric')

    return sanitized
