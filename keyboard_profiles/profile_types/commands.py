from typing import TypedDict, List, Tuple, Literal, Union, Callable, NotRequired, Dict, OrderedDict


class Colors(TypedDict):
    label: str
    #  One or two word label for whatever this effect may do. (RGB stuff duh)

    description: str
    #  A sentence or so long, short description.

    steps: Tuple[List[int]]
    #  Base color values. By default all colors are zero/off.

    report_type: Literal[0x02, 0x03]
    # Feature report = 0x02, Write = 0x03


class AnimationOption(TypedDict):

    name: str
    # Animation name...

    value: List[int]
    # The value that will be added once selected.


class AnimationParam(OrderedDict):
    checks: Union[Callable[[List[int]], bool], List[int], range]
    #  If a callable is provided it is used
    #  by providing the value that will be checked as argument.
    #  Any other value is checked for inclusion for each parameter value.

    default: List[int]
    #  Default values to be used where non is provided.


class Animations(TypedDict):
    base: List[int]
    #  Base values to build animation on top of.

    report_type: Literal[0x02, 0x03]
    # Feature report = 0x02, Write = 0x03

    animation_options: Dict[str, AnimationOption]
    #  Animation options available for the keyboard.
    #  This is only for non-custom animations and effects.

    animation_params: Dict[str, AnimationParam]
    #  Their definition should be the same with
    #  the order they will be combined.


class Commands(TypedDict):
    colors: Colors
    animations: Animations
