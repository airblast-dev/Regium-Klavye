from keyboard_profiles.profile_types import AnimationParam, ColorParam


def parse_params(
    options: dict[str, int] | None,
    kb_options: dict[str, AnimationParam | ColorParam],
) -> dict[str, list[int]]:
    """Parse parameters and fill in missing parameters with defaults defined in kb_option."""

    if options is None:
        default_options = {}
        for param in kb_options.keys():
            default_options[param] = kb_options[param]["default"]
        return default_options

    if (options_s := set(options.keys())) != (color_param_s := set(kb_options)):
        extra_param = options_s - color_param_s
        ValueError(
            f"Expected one or more from ({kb_options.keys()}. Found {sorted(extra_param)})"
        )

    _options = {}
    for k, v in options.items():
        if type(v) is int:
            _options[k] = [v]
        elif isinstance(v, (list, tuple)):
            _options[k] = v

    new_options = {}
    for param in kb_options.keys():
        print(kb_options.keys())
        is_valid: bool = False
        if param not in _options.keys():
            print(kb_options[param])
            new_options[param] = kb_options[param]["default"]
            continue

        # Check if provided value is in accepted parameter.
        if callable(kb_options[param]["checks"]):
            #  Below is type ignored as type checkers include the range functions return as a callable.
            is_valid = kb_options[param]["checks"](_options[param])  # type: ignore
        elif isinstance(kb_options[param]["checks"], (list, tuple, range)):
            is_valid = all(
                [value in kb_options[param]["checks"] for value in _options[param]]
            )
        if is_valid is True:
            new_options[param] = _options[param]
            continue
        raise ValueError(f"Invalid value provided for {param}.")

    return new_options
