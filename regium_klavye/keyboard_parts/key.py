from ..helpers import color_check


class Key:
    """
    Represents a key on a Keyboard.

    The RGB objects color attribute can also be used to safely assign new values.
    For example:
        Key().rgb.color = [100, 200, 100]

    key: `str`
        Label that is printed on the key such as "A" or "ALT".

    rgb: :class:`RGB`
        RGB color class to safely check assigned values.

    indexes: tuple[tuple[`int`, `int`], tuple[`int`, `int`], tuple[`int`, `int`]]
        Each nested tuple represents the location on the base data that will be
        sent for red green and blue colors.
    """

    __slots__ = ("label", "_rgb", "_indexes")

    def __init__(
        self,
        label: str,
        indexes: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
        rgb: tuple[int, int, int] = (0, 0, 0),
    ):
        self.label: str = label
        self.indexes = indexes
        self.rgb = rgb

    def __repr__(self) -> str:
        return f'Key(label="{self.label}", rgb={self.rgb}, indexes={self.indexes})'

    def set_color(self, rgb: tuple[int, int, int]) -> None:
        color_check(rgb)
        self._rgb = rgb

    def get_color(self) -> tuple[int, int, int]:
        return self._rgb

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self._rgb

    @rgb.setter
    def rgb(self, val: tuple[int, int, int]) -> None:
        color_check(val)
        self._rgb: tuple[int, int, int] = val

    @property
    def indexes(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        return self._indexes

    @indexes.setter
    def indexes(
        self, indexes: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
    ) -> None:
        if not isinstance(indexes, (tuple, list)):
            raise TypeError(f"Expected list or tuple, found {type(indexes)}.")
        if len(indexes) != 3:
            raise ValueError(f"Expected 3 values in indexes, found {len(indexes)}.")
        for index in indexes:
            if not isinstance(index, (tuple, list)):
                raise TypeError(f"Expected list or tuple, found {type(index)}.")
            if len(index) != 2:
                raise ValueError(f"Expected 2 values in index, found {len(index)}.")
            if not all(map(lambda val: type(val) is int, index)):
                types = (type(index[0]), type(index[1]))
                raise TypeError(f"Expected 2 int's in index found {types}.")

        self._indexes: tuple[
            tuple[int, int], tuple[int, int], tuple[int, int]
        ] = indexes
