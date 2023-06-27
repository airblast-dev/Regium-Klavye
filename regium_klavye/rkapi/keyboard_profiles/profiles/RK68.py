profile = {
    "name": "Royal Kludge RK68",
    "kb_size": (16, 5),
    "models": (
        {
            "name": "Royal Kludge RK68",
            "long_name": "Royal Kludge RK68 BT and USB",
            "connection_protocols": ("USB", "BT"),
            "vendor_id": 0x0258A,
            "product_id": 0x005E,
            "endpoint": 0x00,
            "usage": 128,
            "usage_page": 1,
        },
    ),
    "commands": {
        # fmt: off
        "colors": {
            "label": "RGB settings",
            "description": "Set RGB values for keys",
            "steps": [
                [0x0A, 0x07, 0x01, 0x03, 0x7E, 0x01, *[0x00] * 59],
                [0x0A, 0x07, 0x02, *[0x00] * 62],
                [0x0A, 0x07, 0x03, *[0x00] * 62],
                [0x0A, 0x07, 0x04, *[0x00] * 62],
                [0x0A, 0x07, 0x05, *[0x00] * 62],
                [0x0A, 0x07, 0x06, *[0x00] * 62],
                [0x0A, 0x07, 0x07, *[0x00] * 62],
            ],
            "report_type": 0x02,
            "color_params": {
                "base": [0x0A, 0x01, 0x01, 0x02, 0x29, 0x0E, 0x00, 0x04, 0x05, 0x00, 0xFF, 0x00],
                "params":{
                    "sleep": {
                        "checks": range(0x01, 0x06),
                        "default": [0x01],
                        "choices": (0x01, 0x02, 0x03, 0x04, 0x05),
                    }
                }
            },
            "padding": 65
        },
        "animations": {
            "base": [0x0A, 0x01, 0x01, 0x02, 0x29],
            "report_type": 0x02,
            "options": {
                "neon_stream": {"name": "Neon Stream", "value": [0x01, 0x00]},
                "sin_wave": {"name": "Sin Wave", "value": [0x04, 0x00]},
            },
            "params": {
                #  Animation options will be combined with the same ordered defined here.
                #  For range key values a callable that returns a boolean value, a Sequence of accepted values or a range can be provided.
                "speed": {"checks": range(0x00, 0x05), "default": [0x03], "choices": (0x00, 0x01, 0x02, 0x03, 0x04)},
                "brightness": {"checks": range(0x00, 0x06), "default": [0x05], "choices": (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)},
                "color": {
                    "checks": lambda colors: all(
                        [0x00 <= color and color <= 0xFF for color in colors]
                    ),
                    "default": [0xFF, 0xFF, 0xFF],
                    "choices": (0x00, 0xff)
                },
                "color_mix": {"checks": [0x00, 0x01], "default": [0x00]}, "choices": (True, False),
                "sleep": {
                    "checks": range(0x00, 0x05),
                    "default": [0x00],
                    "increments": 10,
                    "unit": "minutes",
                    "choices": (0x00, 0x01, 0x02, 0x03, 0x04)
                },
            },
            "padding": 65
        },
        # fmt: on
    },
    #  Each value is stored as label (red index, green index, blue index)
    #  For some keys the red or blue value can be at a previous or next step which is why the step index has to be stored with each value.
    "present_keys": (
        # fmt: off
        #  label, color_indexes, size
        ("ESC", ((0, 9), (0, 10), (0, 11))),
        ("TAB", ((0, 12), (0, 13), (0, 14))),
        ("CPS", ((0, 15), (0, 16), (0, 17))),
        ("LSHFT", ((0, 18), (0, 19), (0, 20))),
        ("LCTRL", ((0, 21), (0, 22), (0, 23))),
        ("1", ((0, 27), (0, 28), (0, 29))),
        ("Q", ((0, 30), (0, 31), (0, 32))),
        ("A", ((0, 33), (0, 34), (0, 35))),
        ("Z", ((0, 36), (0, 37), (0, 38))),
        ("SPR", ((0, 39), (0, 40), (0, 41))),
        ("2", ((0, 45), (0, 46), (0, 47))),
        ("W", ((0, 48), (0, 49), (0, 50))),
        ("S", ((0, 51), (0, 52), (0, 53))),
        ("X", ((0, 54), (0, 55), (0, 56))),
        ("LALT", ((0, 57), (0, 58), (0, 59))),
        ("3", ((0, 63), (0, 64), (1, 3))),
        ("E", ((1, 4), (1, 5), (1, 6))),
        ("D", ((1, 7), (1, 8), (1, 9))),
        ("C", ((1, 10), (1, 11), (1, 12))),
        ("4", ((1, 19), (1, 20), (1, 21))),
        ("R", ((1, 22), (1, 23), (1, 24))),
        ("F", ((1, 25), (1, 26), (1, 27))),
        ("V", ((1, 28), (1, 29), (1, 30))),
        ("5", ((1, 37), (1, 38), (1, 39))),
        ("T", ((1, 40), (1, 41), (1, 42))),
        ("G", ((1, 43), (1, 44), (1, 45))),
        ("B", ((1, 46), (1, 47), (1, 48))),
        ("SPC", ((1, 49), (1, 50), (1, 51))),
        ("6", ((1, 55), (1, 56), (1, 57))),
        ("Y", ((1, 58), (1, 59), (1, 60))),
        ("H", ((1, 61), (1, 62), (1, 63))),
        ("N", ((1, 64), (2, 3), (2, 4))),
        ("7", ((2, 11), (2, 12), (2, 13))),
        ("U", ((2, 14), (2, 15), (2, 16))),
        ("J", ((2, 17), (2, 18), (2, 19))),
        ("M", ((2, 20), (2, 21), (2, 22))),
        ("8", ((2, 29), (2, 30), (2, 31))),
        ("I", ((2, 32), (2, 33), (2, 34))),
        ("K", ((2, 35), (2, 36), (2, 37))),
        (",", ((2, 38), (2, 39), (2, 40))),
        ("RALT", ((2, 41), (2, 42), (2, 43))),
        ("9", ((2, 47), (2, 48), (2, 49))),
        ("O", ((2, 50), (2, 51), (2, 52))),
        ("L", ((2, 53), (2, 54), (2, 55))),
        (".", ((2, 56), (2, 57), (2, 58))),
        ("FN", ((2, 59), (2, 60), (2, 61))),
        ("0", ((3, 3), (3, 4), (3, 5))),
        ("P", ((3, 6), (3, 7), (3, 8))),
        (";", ((3, 9), (3, 10), (3, 11))),
        ("/", ((3, 12), (3, 13), (3, 14))),
        ("RCTRL", ((3, 15), (3, 16), (3, 17))),
        ("-", ((3, 21), (3, 22), (3, 23))),
        ("[", ((3, 24), (3, 25), (3, 26))),
        ("'", ((3, 27), (3, 28), (3, 29))),
        ("RSHFT", ((3, 30), (3, 31), (3, 32))),
        ("=", ((3, 39), (3, 40), (3, 41))),
        ("]", ((3, 42), (3, 43), (3, 44))),
        ("BCK", ((3, 57), (3, 58), (3, 59))),
        ("\\", ((3, 60), (3, 61), (3, 62))),
        ("ENTR", ((3, 63), (3, 64), (4, 3))),
        ("LEAR", ((4, 7), (4, 8), (4, 9))),
        ("UPAR", ((4, 22), (4, 23), (4, 24))),
        ("DOAR", ((4, 25), (4, 26), (4, 27))),
        ("`", ((4, 31), (4, 32), (4, 33))),
        ("DEL", ((4, 34), (4, 35), (4, 36))),
        ("PGUP", ((4, 37), (4, 38), (4, 39))),
        ("PGDWN", ((4, 40), (4, 41), (4, 42))),
        ("RIAR", ((4, 43), (4, 44), (4, 45))),
        # fmt: on
    ),
    #  The is structured like this to allow keyboards with space between keys.
    #  Spaces between keys are defined by their first value in the tuple being None and the next value being its width in units.
    #  All key heights are set as 1. In case a key height is more than 1, it can be written again, under or over it in order to extend its size.
    #  For non rectangle keys the same key label with different sizing can be used in order to create them.
    #  For example ISO layout enter key:
    #
    #  Below each key line represents a row of keys on a keyboard.
    "layout": (
        # fmt: off
        ("ESC", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1), ("7", 1), ("8", 1), ("9", 1), ("0", 1), ("-", 1), ("=", 1), ("BCK", 2), ("`", 1),
        ("TAB", 1.5), ("Q", 1), ("W", 1), ("E", 1), ("R", 1), ("T", 1), ("Y", 1), ("U", 1), ("I", 1), ("O", 1), ("P", 1), ("[", 1), ("]", 1), ("\\", 1.5), ("DEL", 1),
        ("CPS", 1.75), ("A", 1), ("S", 1), ("D", 1), ("F", 1), ("G", 1), ("H", 1), ("J", 1), ("K", 1), ("L", 1), (";", 1), ("'", 1), ("ENTR", 2.25), ("PGUP", 1),
        ("LSHFT", 2.25), ("Z", 1), ("X", 1), ("C", 1), ("V", 1), ("B", 1), ("N", 1), ("M", 1), (",", 1), (".", 1), ("/", 1), ("RSHFT", 1.75), ("UPAR", 1), ("PGDWN", 1),
        ("LCTRL", 1.25), ("SPR", 1.25), ("LALT", 1.25), ("SPC", 6.25), ("RALT", 1), ("FN", 1), ("RCTRL", 1), ("LEAR", 1), ("DOAR", 1), ("RIAR", 1),
        # fmt: on
    ),
}
