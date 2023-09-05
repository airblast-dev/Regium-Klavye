"""Operations related parameter parsing."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..keyboard_profiles.profile_types import AnimationParam, ColorParam


def parse_params(
    params: dict[str, int] | None,
    kb_params: dict[str, AnimationParam | ColorParam],
) -> dict[str, list[int]]:
    """Parse and fill in the missing parameters.

    Args:
        params: Parameters that were passed in from a function or user.
        kb_params: Default parameters for params to be filled in.

    Raises:
        ValueError: Extra parameter was found
    """
    if params is None:
        default_params = {}
        for param in kb_params.keys():
            default_params[param] = kb_params[param]["default"]
        return default_params

    if (param_s := set(params.keys())) != (color_param_s := set(kb_params)):
        extra_param = param_s - color_param_s
        ValueError(
            f"Expected one or more from "
            f"({kb_params.keys()}. Found {sorted(extra_param)})"
        )

    _params: dict[str, list[int]] = {}
    for k, v in params.items():
        if isinstance(v, int):
            _params[k] = [v]
        elif isinstance(v, (list, tuple)):
            _params[k] = v

    new_params = {}
    for param in kb_params.keys():
        is_valid: bool = False
        if param not in _params.keys():
            new_params[param] = kb_params[param]["default"]
            continue

        match kb_params[param]["checks"]:
            case func if isinstance(func, Callable):
                is_valid = func(_params[param])
            case list() | range() | tuple() as in_check:
                is_valid = all([value in in_check for value in _params[param]])
            case _ if not is_valid:
                raise ValueError(f"Invalid value provided for {param}.")

        new_params[param] = _params[param]

    return new_params
