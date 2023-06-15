import unittest

from keyboard_parts import Key


class KeyColorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.key = Key("A", ((0, 2), (0, 3), (0, 4)))

    def test_key_set_color(self):
        test_values = [[5, 10, 15], [100, 200, 150], [100, 200, 255], [10, 20, 30]]
        for value in test_values:
            with self.subTest(
                msg="Set colors using Sequence of integers.", value=value
            ):
                self.key.set_color(value)
                self.assertEqual(self.key.get_color(), value)

    def test_key_set_color_invalid_arg(self):
        test_values = ["WumboSized", ("A", 2, 3)]
        for value in test_values:
            with self.subTest(
                msg="Set invalid colors using color keywords. (red, green, blue)",
                value=value,
            ):
                self.assertRaises(
                    TypeError,
                    self.key.set_color,
                    red=value[0],
                    green=value[1],
                    blue=value[2],
                )
            with self.subTest(
                msg="Set invalid colors using Sequence of integers.", value=value
            ):
                self.assertRaises(TypeError, self.key.set_color, value)


class KeyIndexTestCase(unittest.TestCase):
    def test_key_index(self):
        with self.subTest(msg="Test valid index values."):
            key = Key("A", ((5, 6), (7, 8), (9, 0)))
            self.assertEqual(key.indexes, ((5, 6), (7, 8), (9, 0)))

    def test_key_index_invalid_arg(self):
        test_values_type = ["Hello", ("s", (1, 2), (2, 3)), ((5, "A"), (1, 2), (2, 3))]
        test_values_value = [((1, 2), (3, 4)), ((5, 6), (7, 8), (9, 0, 3)), []]
        for value in test_values_type:
            with self.subTest(
                msg="Test invalid index values for TypeError.", value=value
            ):
                self.assertRaises(TypeError, Key, "A", value)
        for value in test_values_value:
            with self.subTest(
                msg="Test invalid index values for ValueError.", value=value
            ):
                self.assertRaises(ValueError, Key, "A", value)
