"""Operations related to color value checking."""

from typing import Sequence


def color_check(rgb: Sequence[int]) -> None:
    """Check if provided argument is a valid RGB color value.

    Raises:
        TypeError: Non int type found in Sequence.
            Provided value is not a Sequence.
        ValueError: Incorrect length of values.
            Values are bigger than 1 byte or negative.
    """
    if not isinstance(rgb, Sequence):
        raise TypeError(f"Expected sequence of integers, found {rgb}.")

    if (num := len(rgb)) != 3:
        raise ValueError(f"Expected length 3 Sequence found {num} values.")

    type_checks = (isinstance(color, int) for color in rgb)
    if not all(type_checks):
        faulty_types = [
            type(color) for color in rgb if type(color) is not int  # noqa: E721
        ]
        raise TypeError(f"Expected type int, found {faulty_types}.")

    rgb_validity = (color < 0 or 255 < color for color in rgb)
    if any(rgb_validity):
        raise ValueError("Color values must be between 0 and 255.")
