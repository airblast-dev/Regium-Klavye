from keyboard_profiles.profile_types import AnimationParam, ColorParam


def parse_params(
    params: dict[str, int] | None,
    kb_params: dict[str, AnimationParam | ColorParam],
) -> dict[str, list[int]]:
    """Parse parameters and fill in the missing parameters in options with defaults defined in kb_option."""

    if params is None:
        default_params = {}
        for param in kb_params.keys():
            default_params[param] = kb_params[param]["default"]
        return default_params

    if (param_s := set(params.keys())) != (color_param_s := set(kb_params)):
        extra_param = param_s - color_param_s
        ValueError(
            f"Expected one or more from ({kb_params.keys()}. Found {sorted(extra_param)})"
        )

    _params = {}
    for k, v in params.items():
        if type(v) is int:
            _params[k] = [v]
        elif isinstance(v, (list, tuple)):
            _params[k] = v

    new_params = {}
    for param in kb_params.keys():
        print(kb_params.keys())
        is_valid: bool = False
        if param not in _params.keys():
            new_params[param] = kb_params[param]["default"]
            continue

        # Check if provided value is in accepted parameter.
        if callable(kb_params[param]["checks"]):
            #  Below is type ignored as type checkers include the range functions return as a callable.
            is_valid = kb_params[param]["checks"](_params[param])  # type: ignore
        elif isinstance(kb_params[param]["checks"], (list, tuple, range)):
            is_valid = all(
                [value in kb_params[param]["checks"] for value in _params[param]]
            )
        if is_valid is True:
            new_params[param] = _params[param]
            continue
        raise ValueError(f"Invalid value provided for {param}.")

    return new_params
