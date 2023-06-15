import unittest
from typing import Tuple, Optional

from keyboard_parts import Keyboard, Key
from keyboard_profiles import PROFILES


class TestKeyboard(Keyboard):
    def __init__(self, vid: int, pid: int):
        super().__init__(vid, pid)

    def apply_color(
        self, rgb: Optional[Tuple[int, int, int]] = None
    ) -> tuple[bytearray]:
        self._color_data()
        self.set_color((0, 0, 0))
        return self._final_color_data


class KeyboardsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        keyboards = []
        for device in PROFILES.keys():
            keyboards.append(TestKeyboard(device[0], device[1]))

        self.keyboards: list[TestKeyboard] = keyboards

    def test_iteration(self):
        for keyboard in self.keyboards:
            for key in keyboard:
                with self.subTest(key=key):
                    self.assertIsInstance(key, Key)

    def test_set_color(self):
        colors = (0, 10, 20)
        for keyboard in self.keyboards:
            keyboard.set_color(colors)
            for key in keyboard:
                with self.subTest(
                    msg="Test keyboard settings through each key.", key=key
                ):
                    self.assertEqual(key.get_color(), colors)

    def test_set_color_invalid_arg(self):
        test_values = ["WumboSized", ("A", 2, 3)]
        for keyboard, value in zip(self.keyboards, test_values):
            with self.subTest(
                msg="Set invalid colors using color keywords. (red, green, blue)",
                value=value,
            ):
                self.assertRaises(
                    TypeError,
                    keyboard.set_color,
                    rgb=value,
                )
            with self.subTest(
                msg="Set invalid colors using Sequence of integers.", value=value
            ):
                self.assertRaises(TypeError, keyboard.set_color, value)
            with self.subTest(
                msg="Set invalid colors using 3 color values as seperate arguments.",
                value=value,
            ):
                self.assertRaises(TypeError, keyboard.set_color, *value)

    def test_set_key_color(self):
        label = "A"
        colors = ((10, 20, 30), (40, 50, 60))
        for keyboard in self.keyboards:
            for color in colors:
                keyboard.set_key_color(label, color)
                with self.subTest(label=label, color=color):
                    self.assertEqual(keyboard[label].get_color(), color)

    def test_set_key_color_invalid_arg(self):
        test_values = ["WumboSized", ("A", 2, 3)]
        label = "A"
        for keyboard, value in zip(self.keyboards, test_values):
            with self.subTest(
                msg="Set invalid colors using color keywords. (red, green, blue)",
                value=value,
            ):
                self.assertRaises(
                    TypeError,
                    keyboard.set_key_color,
                    label,
                    value,
                )

    def test_set_key_color_data(self):
        for keyboard in self.keyboards:
            profile = PROFILES[(keyboard._vid, keyboard._pid)]
            present_keys: Tuple[
                str, Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
            ] = profile["present_keys"]
            colors = ((0xFF, 0x10, 0x20), (0x10, 0xFF, 0x20), (0x10, 0x20, 0xFF))
            for key in present_keys:
                indexes = key[1]
                for color in colors:
                    keyboard.set_key_color(key[0], color)
                    data: tuple[bytearray] = keyboard.apply_color()

                    for i in range(0, 3):
                        with self.subTest(
                            msg="Compare bytearray results to color value.",
                            label=key[0],
                            step=(indexes[i][0], indexes[i][1]),
                            data=data[indexes[i][0]],
                            value=color[i],
                        ):
                            self.assertEqual(
                                data[indexes[i][0]][indexes[i][1]], color[i]
                            )
