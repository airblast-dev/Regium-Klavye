def color_check(rgb: tuple[int, int, int]) -> None:
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
