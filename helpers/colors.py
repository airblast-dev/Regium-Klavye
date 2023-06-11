from typing import Sequence


def color_check(rgb: Sequence[int]) -> None:
    """
    Checks if three values were provided. Raises ValueError if any number of items other than 3 is provided.

    Checks if provided value is a list consisting of int's.

    Checks if all values are between 0 and 255.
    """
    if not isinstance(rgb, (tuple, list)):
        raise TypeError(f"Expected sequence of integers, found {rgb}.")

    type_checks = (type(color) is int for color in rgb)
    if not all(type_checks):
        faulty_types = [type(color) for color in rgb if type(color) is not int]
        raise TypeError(f"Expected type int, found {faulty_types}.")

    rgb_validity = (color < 0 or 255 < color for color in rgb)
    if any(rgb_validity):
        raise ValueError(f"Color values must be between 0 and 255.")


def color_arg_parser(
    rgb: dict | Sequence[int] = None, kw_rgb: dict = None
) -> Sequence[int]:
    """
    Set the color for this key.

    Must be passed a list of integers or red, green and blue values.
    Passed integers should be between 0-255.
    """
    color_names = ["red", "green", "blue"]
    rgb = rgb or kw_rgb
    if type(rgb) is dict:
        rgb = rgb.copy()
        new_rgb = {color_name: rgb.pop(color_name, 0) for color_name in color_names}
        if rgb.keys():
            raise ValueError(
                f"Expected colors {color_names} found {rgb.keys()} as extra."
            )
        return list(new_rgb.values())
    elif isinstance(rgb, (tuple, list)):
        if len(rgb) == 1 and len(rgb[0]) == 3:
            return color_arg_parser(kw_rgb=rgb[0])
        elif len(rgb) == 3:
            return rgb
        elif len(rgb) == 1 and isinstance(rgb[0], (tuple, list)) and len(rgb[0]) == 1:
            return color_arg_parser(kw_rgb=rgb[0])
        else:
            raise TypeError(
                f"Expected 3 integers or a tuple with 3 integers, found {rgb}."
            )

    else:
        raise TypeError(
            "Provided color values must be a Sequence of red, green and blue or red, green and blue as keywords."
        )
