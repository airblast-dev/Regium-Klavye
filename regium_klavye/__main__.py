"""Command line interface for regium_klavye."""
from __future__ import annotations

import os
import platform
import sys
from argparse import ArgumentParser
from enum import Enum
from typing import TYPE_CHECKING

from .rkapi import PROFILES, KeyboardNotFoundError, get_keyboards
from .udev import UDEV_PATH, get_udev, is_rules_up_to_date, setup_rules

if TYPE_CHECKING:
    from typing import Any, NoReturn


class NamedColors(Enum):
    """Named colors for ease of use."""

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    orange = (255, 165, 0)
    pink = (255, 102, 204)
    cyan = (127, 255, 212)
    magenta = (252, 116, 253)
    purple = (128, 0, 128)


def _parse_color(color: tuple[str] | str) -> list[int]:
    if isinstance(color, str) or isinstance(color[0], str):
        try:
            return list(NamedColors[color[0]].value)
        except KeyError:
            pass
    if len(color) == 3:
        try:
            return [int(_color) for _color in color]
        except ValueError:
            pass
    sys.exit(
        f"Invalid RGB value provided for color parameter. Color values must be one of "
        f"{tuple([color.name for color in NamedColors])} or an RGB value."
    )


def _check_linux(write=False) -> None:
    """Perform checks for Linux based systems."""
    if platform.system() != "Linux":
        return

    if os.getuid() == 0 and write is True:
        return

    if not os.path.isfile(UDEV_PATH) and write is False:
        sys.exit(
            'Udev rules were not found. Run "regium_klavye udev -w" as root to '
            "write the rules."
        )

    if not is_rules_up_to_date():
        sys.exit(
            'Udev rules are not up to date. Run "regium_klavye udev -w" as root '
            "to update the rules."
        )

    return


def _handle_udev(udev_parser: ArgumentParser, choices: dict[str, Any]) -> NoReturn:
    if choices["read"] is True:
        print(get_udev())
    elif choices["write"] is True:
        setup_rules(choices["path"])
        print("Udev rules have been succesfully written.")
    else:
        udev_parser.print_help()
    sys.exit()


def _handle_list(list_parser: ArgumentParser, choices: dict[str, Any]) -> NoReturn:
    keyboards = choices["keyboards"]
    if choices["all"] is True:
        # device_list is the general name and then the list of
        # specific models or versions of the keyboard.

        profiles = sorted(PROFILES.values(), key=lambda profile: profile["name"])

        device_list: dict[str, list[str]] = {}
        for profile in profiles:
            name = profile["name"]
            long_names = [model["long_name"] for model in profile["models"]]
            long_names.sort()
            device_list[name] = long_names

        supported_devices = ["Full list of supported devices for Regium Klavye\n\n"]

        for name, models in device_list.items():
            formatted_model = [
                f"Supported Models for {name} \n" ":\n" + "\n - ".join([""] + models)
            ]
            supported_devices.extend(formatted_model)

        print(supported_devices)
    else:
        if not keyboards:
            sys.exit("Unable to find any supported keyboards.")

        supported_devices = ["List of detected and supported devices."]

        for keyboard in keyboards:
            valid_commands = []
            if keyboard.has_rgb:
                valid_commands.append("set-color")
            if keyboard.has_anim:
                valid_commands.append("set-anim")
            if keyboard.has_custom_anim:
                valid_commands.append("set-custom-anim")
            supported_devices[-1] += "\n" + len(keyboard.long_name) * "-"
            supported_devices.append(
                keyboard.long_name + "\n" + " - " + ", ".join(valid_commands)
            )
        print("\n".join(supported_devices))
    sys.exit()


def _handle_set_color(parser: ArgumentParser, choices: dict[str, Any]) -> NoReturn:
    keyboard = choices["keyboards"][choices["device"]]
    if not keyboard.has_rgb:
        sys.exit(f"{keyboard.long_name} does not support color changing.")

    color = tuple([val for val in choices["color"]])
    keyboard.apply_color(color)

    sys.exit()


def _handle_set_anim(parser: ArgumentParser, choices: dict[str, Any]) -> NoReturn:
    keyboards = choices["keyboards"]
    keyboard = choices["keyboards"][choices["device"]]
    if choices["animation"] is None:
        anim_info = "Below is a list of accepted animations for detected "
        "keyboards."
        anim_options = [anim_info]
        for keyboard in keyboards:
            long_name = keyboard.long_name

            options = f'Options: {", ".join(keyboard.anim_options)}'

            params: list[str] = []
            for param in keyboard.anim_params:
                params.append(
                    f"{keyboard.anim_params[param]['description']} "
                    f"--{param} {keyboard.anim_params[param]['choices']}"
                )
            final_params = "Parameters:\n\t[" + str("]\n\t[".join(params)) + "]"
            explanation = (
                f"{'-' * len(long_name)}\n{long_name}\n{options}\n{final_params}"
            )

            anim_options.append(explanation)
        print("\n".join(anim_options))
    else:
        if choices["animation"] not in keyboard.anim_options:
            sys.exit(f"Invalid animation provided for {keyboard.long_name}.")
        parsed_params: dict[str, int | list[int]] = {}
        for param in keyboard.anim_params:
            if choices[param] is False:
                continue

            try:
                parsed_params[param] = [int(_param) for _param in choices[param]]
            except ValueError:
                sys.exit(f"Invalid argument provided for {param}.")
        try:
            keyboard.set_animation(choices["animation"], parsed_params)
        except ValueError:
            sys.exit(
                "Invalid argument provided for animation parameters. "
                'Run "regium_klavye set-anim" for a full list options '
                "available for the keyboard."
            )
        keyboard.apply_animation()
    sys.exit()


def _get_choices() -> tuple[ArgumentParser, dict[str, Any]]:
    """Parse choices and return subparser used nad the choices."""
    udev_parser = ArgumentParser()
    # Set udev_parser as ArgumentParser.
    # So type checkers dont complain in final match check for unbound variable.
    parser = ArgumentParser(
        "Regium Klavye",
        description="Regium Klavye is a command line (CLI) application for "
        "controlling RGB, Keymapping and animations for supported keyboards.",
        epilog=(
            "While every keyboard supported is tested to assure there isnt any issues."
            "\nThis application was made through reverse engineering devices, "
            "and therefor I cannot provide any guarantee or promises that this will "
            "not break any keyboards.\nUse the application at your own risk."
        ),
    )

    subparsers = parser.add_subparsers(help="commands", dest="command")

    parser.add_argument(
        "-d",
        "--device",
        required=False,
        default=0,
        type=int,
        help="Number of the device to apply settings for. List of detected devices "
        'can be read via "regium_klavye list"',
    )

    # UDEV PARSER
    if platform.system() == "Linux":
        udev_parser = subparsers.add_parser(
            "udev", description="Commands related to udev rules."
        )

        udev_parser.add_argument(
            "-r",
            "--read",
            action="store_true",
            help="Use to view udev rules before writing them.",
        )

        udev_parser.add_argument(
            "-w",
            "--write",
            action="store_true",
            help=f"Write udev rules to {UDEV_PATH}. Requires to be run as root.",
        )

        udev_parser.add_argument(
            "-p",
            "--path",
            default=UDEV_PATH,
            help="Requires superuser privileges. Path to store udev rules can be "
            "optionally provided.",
            metavar="WRITE_PATH",
        )

    # LIST DEVICE PARSER
    list_parser = subparsers.add_parser(
        "list",
        description="Lists found devices. Can be used with --all for a full list "
        "of supported devices.",
    )
    list_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="List all supported keyboards including ones not found on this device.",
    )

    try:
        keyboards = get_keyboards()
    except KeyboardNotFoundError:
        sys.exit("No supported keyboards detected.")

    # SET-COLOR PARSER
    set_color_parser = subparsers.add_parser(
        "set-color",
        help="Set color for keyboard. The device number can be provided with"
        " --device to change the color for a specific device.",
    )

    set_color_parser.add_argument(
        "-c",
        "--color",
        help=f"Color values to set the keyboard to. Colors can be also set by name. "
        f"Valid named colors are {[i.name for i in NamedColors]}.",
        required=True,
        nargs="+",
    )

    # SET-ANIM PARSER
    # Help response is handled later since it relies on detected keyboards to display.
    set_anim_parser = subparsers.add_parser(
        "set-anim",
        description="Set animation for keyboard. The device number can be provided with"
        " --device to change the color for a specific device.",
    )

    set_anim_parser.add_argument(
        "-an",
        "--animation",
        type=str,
        help='Run "regium_klavye set-anim" to see a full list of available '
        "animations and parameters for detected keyboards.",
    )

    all_anim_params: set[str] = set()
    for profile in PROFILES.values():
        anim_params = profile["commands"]["animations"]["params"].keys()
        all_anim_params.update(anim_params)

    # Iterate over all profiles and get length of argument
    for param in all_anim_params:
        arg_len_params = {}
        for profile in PROFILES.values():
            try:
                animations = profile["commands"]["animations"]
                default = animations["params"][param]["default"]
                if len(default) != 1:
                    arg_len_params["nargs"] = "+"
                else:
                    arg_len_params = {}
            except KeyError:
                continue
            set_anim_parser.add_argument(
                "--" + param,
                required=False,
                default=False,
                **arg_len_params,
            )

    choices = vars(parser.parse_args())

    _check_linux(choices.get("write", False))

    if choices.get("color", False):
        choices["color"] = _parse_color(choices["color"])

    choices["keyboards"] = keyboards

    match choices["command"]:
        case "udev":
            _parser = udev_parser
        case "list":
            _parser = list_parser
        case "set-color":
            _parser = set_color_parser
        case "set-anim":
            _parser = set_anim_parser
        case _:
            sys.exit(parser.format_help())

    return _parser, choices


def main():  # noqa: D103
    parser, choices = _get_choices()

    match choices["command"]:
        case "udev":
            _handle_udev(parser, choices)
        case "list":
            _handle_list(parser, choices)
        case _ if len(choices["keyboards"]) - 1 < choices["device"]:
            sys.exit(
                "Invalid device number provided or device not supported. "
                'Use "regium_klavye list" for a list of supported and detected devices.'
            )
        case "set-color":
            _handle_set_color(parser, choices)
        case "set-anim":
            _handle_set_anim(parser, choices)



main()