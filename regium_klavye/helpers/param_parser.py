"""Operations related parameter parsing."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..keyboard_profiles.profile_types import AnimationParam, ColorParam


def parse_params(
    params: dict[str, Sequence[int]] | None,
    base_params: dict[str, AnimationParam | ColorParam],
) -> dict[str, list[int]]:
    """Parse and fill in the missing parameters.

    Args:
        params: Parameters that were passed in from a function or user.
        base_params: Default parameters for params to be filled in.

    Raises:
        ValueError: Extra parameter was found.
    """
    if params is None:
        default_params = {}
        for param in base_params.keys():
            default_params[param] = base_params[param]["default"]
        return default_params

    if (param_s := set(params)) != (base_params_s := set(base_params)):
        extra_params = param_s - base_params_s
        ValueError(
            f"Expected one or more from "
            f"({base_params.keys()}. Found {sorted(extra_params)})"
        )

    _params: dict[str, Sequence[int]] = {}

    new_params = {}
    for param in base_params:
        is_valid = False
        if param not in params:
            new_params[param] = base_params[param]["default"]
            continue

        param_val = params[param]
        base_param_val = base_params[param]["default"]
        
        if isinstance(param_val, Sequence) \
        and len(param_val) == len(base_param_val)\
        and all([isinstance(val, int) for val in param_val]):
            _params[param] = list(param_val)
        else:
            raise ValueError(f"Invalid value provided for {param}.")

        match base_params[param]["checks"]:
            case list() | range() | tuple() as in_check if len(_params[param]) == len(
                base_params[param]["default"]
            ):
                is_valid = all([value in in_check for value in _params[param]])
            case func if callable(func):
                is_valid = func(_params[param])

        if is_valid is not True:
            raise ValueError(f"Invalid value provided for {param}.")

        new_params[param] = params[param]

    return new_params
