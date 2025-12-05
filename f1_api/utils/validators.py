"""Utilities for validating request data and query parameters."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from werkzeug.datastructures import ImmutableMultiDict

from .exceptions import APIError


Validator = Callable[[Any], bool]
Transformer = Callable[[Any], Any]


class QueryParamSpec(dict):
    """Type alias for query parameter specification.

    Expected keys:
        - type: callable used to coerce the incoming string (e.g. ``str``).
        - required: whether the parameter must be present.
        - validator: optional predicate to run after coercion.
        - message: error message when ``validator`` fails.
        - transform: optional callable to normalize the coerced value.
        - default: value to use when param is absent (and not required).
    """


def validate_query_params(
    args: ImmutableMultiDict[str, str] | Mapping[str, str],
    allowed: Mapping[str, QueryParamSpec],
) -> dict[str, Any]:
    """Validate and normalize query parameters.

    - Rejects any unexpected parameters.
    - Coerces known params to the desired type.
    - Applies optional validators and transformations.

    Returns a dict of parsed parameters. Raises :class:`APIError` with
    status code 400 when validation fails.
    """

    parsed: dict[str, Any] = {}
    errors: dict[str, Any] = {}

    allowed_keys = set(allowed.keys())
    received_keys = set(args.keys())

    unexpected = sorted(received_keys - allowed_keys)
    if unexpected:
        errors["unexpected"] = unexpected

    for name, spec in allowed.items():
        is_required = spec.get("required", False)

        if name not in args:
            if is_required:
                errors[name] = "Missing required parameter"
            elif "default" in spec:
                parsed[name] = spec["default"]
            continue

        raw_value = args.get(name)
        value: Any = raw_value

        converter = spec.get("type")
        if converter:
            try:
                value = converter(raw_value)
            except (TypeError, ValueError):
                errors[name] = spec.get("invalid_type_message") or (
                    f"Invalid value for '{name}'"
                )
                continue

        validator: Validator | None = spec.get("validator")
        if validator and not validator(value):
            errors[name] = spec.get("message") or f"Invalid value for '{name}'"
            continue

        transform: Transformer | None = spec.get("transform")
        if transform:
            value = transform(value)

        parsed[name] = value

    if errors:
        raise APIError(
            "Invalid query parameters",
            status_code=400,
            code="invalid_query_params",
            details=errors,
        )

    return parsed
