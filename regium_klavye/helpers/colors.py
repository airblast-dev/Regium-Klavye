"""Operations related to color value checking."""

from typing import Sequence


def validate_color(rgb: Sequence[int] | None) -> None:
    """Check if provided argument is a valid RGB color value.

    Raises:
        TypeError: Non int type found in Sequence.
            Provided value is not a Sequence.
        ValueError: Incorrect length of values.
            Values are bigger than 1 byte or negative.
    """
    match rgb:
        case None:
            return
        case [int(), int(), int()] if all([0 <= c <= 255 for c in rgb]):
            return

    if not isinstance(rgb, Sequence):
        raise TypeError(f"Expected tuple or list, found {rgb}")
    if (rgb_len := len(rgb)) != 3:
        raise ValueError(f"Expected length 3 Sequence found {rgb_len} values.")

    for color in rgb:
        if not isinstance(color, int):
            raise TypeError(f"Expected sequence of integers, found {rgb}.")
        if 0 <= color <= 255:
            raise ValueError("Color values must be between 0 and 255.")
