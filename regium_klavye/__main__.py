import argparse
import sys, platform, os
from enum import Enum

import rkapi


class NamedColors(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    orange = (255, 165, 0)
    pink = (255, 102, 204)
    cyan = (127, 255, 212)
    magenta = (252, 116, 253)
    purple = (128, 0, 128)


def _check_linux(write=False) -> None:
    """Performs checks for Linux based systems."""
    if platform.system() != "Linux":
        return

    if os.getuid() == 0 and write is True:
        return

    if not os.path.isfile(rkapi.UDEV_PATH) and write is False:
        sys.exit(
            'Udev rules were not found. Run "regium_klavye udev -w" as root to write the rules.'
        )

    if not rkapi.is_rules_up_to_date():
        sys.exit(
            'Udev rules are not up to date. Run "regium_klavye udev -w" as root to update the rules.'
        )

    return


def main():
    parser = argparse.ArgumentParser(
        "Regium Klavye",
        description="Regium Klavye is a command line (CLI) application for controlling RGB, Keymapping and animations for supported keyboards.",
        epilog=(
            "While every keyboard supported is tested to assure there isnt any issues.\nThis application was made through reverse engineering devices "
            + "and therefor I cannot provide any guarantee or promises that this will not break any keyboards.\n"
            + "Use the application at your own risk."
        ),
    )

    subparsers = parser.add_subparsers(help="commands", dest="command")

    #  UDEV PARSER
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
            help=f"Write udev rules to {rkapi.UDEV_PATH}. Requires to be run as root.",
        )

        udev_parser.add_argument(
            "-p",
            "--path",
            default="/etc/udev/rules.d/99-rkapi.rules",
            help="Requires superuser privileges. Path to store udev rules can be optionally provided.",
            metavar="WRITE_PATH",
        )

    #  LIST DEVICE PARSER
    list_parser = subparsers.add_parser(
        "list",
        description="Lists found devices. Can be used with --all for a full list of supported devices.",
    )
    list_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="List all supported keyboards including ones not found on this device.",
    )

    keyboards = rkapi.get_keyboards()

    # SET-COLOR PARSER
    set_color_parser = subparsers.add_parser(
        "set-color",
        help="Set color for keyboard. The device number can be provided with --device to change the color for a specific device.",
    )
    set_color_parser.add_argument(
        "-d",
        "--device",
        type=int,
        choices=range(0, len(keyboards)),
        help='Number of the device to change color. Use "regium_klavye list" for a list of found and supported devices.',
        default=0,
    )

    set_color_parser.add_argument(
        "-c",
        "--color",
        help=f"Color values to set the keyboard to. Colors can be also set by name. Valid named colors are {[i.name for i in NamedColors]}.",
        required=True,
        nargs="+",
    )

    #  SET-ANIM PARSER
    set_anim_parser = subparsers.add_parser(
        "set-anim",
        description="Set animation for keyboard. The device number can be provided with --device to change the color for a specific device.",
    )

    set_anim_parser.add_argument(
        "-d",
        "--device",
        type=int,
        choices=range(0, len(keyboards)),
        help='Number of the device to set animation. Use "regium_klavye list" for a list of found and supported devices.',
        default=0,
    )

    set_anim_parser.add_argument(
        "-l", "--list", action="store_true", help="Lists accepted animations."
    )

    set_anim_parser.add_argument(
        "-a",
        "--animation",
        help='Animation to set the keyboard to. Use "regium_klavye set-anim --list" to see accepted animations and parameters such as sleep...',
    )

    choices = vars(parser.parse_args())

    _check_linux(choices.get("write", False))

    if "udev" == choices["command"]:
        if choices["read"] is True:
            print(rkapi.get_udev())
        elif choices["write"] is True:
            rkapi.setup_rules(choices["path"])
            print("Udev rules have been succesfully written.")
        else:
            udev_parser.print_help()  # type: ignore
        return

    elif "list" == choices["command"]:
        if choices["all"] is True:
            from rkapi import PROFILES

            #  device_list is the general name and then the list of specific models or versions of the keyboard.

            profiles = sorted(PROFILES.values(), key=lambda profile: profile["name"])

            device_list = {
                profile["name"]: sorted(
                    [model["long_name"] for model in profile["models"]]
                )
                for profile in profiles
            }

            supported_devices = "Full list of supported devices for Regium Klavye\n\n"

            for name, models in device_list.items():
                supported_devices += (
                    f"Supported Models for {name}" + ":\n" + "\n - ".join([""] + models)
                )

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
        return

    if len(keyboards) - 1 > choices["device"]:
        sys.exit(
            'Invalid device number provided. Use "regium_klavye list" for a list of supported and detected devices.'
        )

    keyboard: rkapi.Keyboard = keyboards[choices["device"]]

    if choices["command"] == "set-color":
        if len(choices["color"]) == 1:
            choice_color = choices["color"][0]
            try:
                color = NamedColors[choice_color]
            except KeyError:
                sys.exit(
                    f"The color {choice_color} was not found in known colors. Known valid colors are {[i.name for i in NamedColors]}"
                )
            keyboard.apply_color(color.value)

        elif len(choices["color"]) == 3:
            try:
                colors = [int(val) for val in choices["color"]]
            except TypeError:
                sys.exit(
                    "Only numbers must be provided to set a keyboard to a specific color."
                )
            for color in colors:
                if color < 0 or 255 < color:
                    sys.exit("Color values provided must be between 0-255.")
            keyboard.apply_color(colors)

        else:
            set_color_parser.print_help()

    elif choices["command"] == "set-anim":
        animations_options = keyboard.anim_options
        if choices["list"] is True:
            long_name = keyboard.anim_options
            animation_choices = (
                f"Aniamtions supported for {long_name}:\n"
                + len(long_name) * "-"
                + "\n"
                + "\n".join(keyboard.anim_options)
            )

            animations_params = [f"Supported animation parameters for {long_name}:\n"]

            for param, choice in keyboard.anim_param_choices.items():
                animations_params.append(f"   {param}: {choice}")
            print(animation_choices + "\n".join(animations_params))

        elif choices["animation"]:
            if choices["animation"] in animations_options:
                keyboard.set_animation(choices["animation"])
        return


main()
