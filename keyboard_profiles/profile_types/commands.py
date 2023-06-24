from typing import (
    TypedDict,
    Literal,
    Callable,
    OrderedDict,
)


class ColorParam(TypedDict):
    checks: Callable[[list[int]], bool] | list[int] | range
    #  Check to be done to confirm provided value is valid.

    default: list[int]
    #  Default value for when one is not provided.

    valid_values: tuple[int, ...]
    #  Tuple of valid values to be used as feedback.

    choices: tuple[int, ...]
    #  Accepted choices for this parameter.


class ColorParams(TypedDict):
    base: list[int]
    #  Base data to add param on top of.

    params: dict[str, ColorParam]


class Colors(TypedDict):
    label: str
    #  One or two word label for whatever this effect may do. (RGB stuff duh)

    description: str
    #  A sentence or so long, short description.

    steps: list[list[int]]
    #  Base color values. By default all colors are zero/off.

    report_type: Literal[0x02, 0x03]
    #  Feature report = 0x02, Write = 0x03

    color_params: ColorParams

    padding: int
    #  Amount of padding for Colors.


class AnimationOption(TypedDict):
    name: str
    # Animation name...

    value: list[int]
    # The value that will be added once selected.


class AnimationParam(TypedDict):
    checks: Callable[[list[int]], bool] | list[int] | range
    #  If a callable is provided it is used
    #  by providing the value that will be checked as argument.
    #  Any other value is checked for inclusion for each parameter value.

    default: list[int]
    #  Default values to be used where non is provided.

    choices: tuple[int, ...]
    #  Accepted choices for this parameter.


class Animations(TypedDict):
    base: list[int]
    #  Base values to build animation on top of.

    report_type: Literal[0x02, 0x03]
    # Feature report = 0x02, Write = 0x03

    options: dict[str, AnimationOption]
    #  Animation options available for the keyboard.
    #  This is only for non-custom animations and effects.

    params: dict[str, AnimationParam]
    #  Their definition should be the same with
    #  the order they will be combined.

    padding: int
    #  Amount of padding for Colors.


class Commands(TypedDict):
    colors: Colors
    animations: Animations
