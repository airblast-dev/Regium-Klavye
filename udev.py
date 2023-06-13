import subprocess
from keyboard_profiles import PROFILES
from keyboard_profiles.profile_types import Profile, Model
from typing import List, Tuple


def _construct_rule(vid_pid: Tuple[int, int]) -> str:

    #  When formatting integer to hexadecimal string leading 0's are removed.
    #  This adds the 0 values while still fitting in 4 characters so its valid.
    #  5e -> 005e
    return (
        f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"\n'
        +
        f'SUBSYSTEM=="hidraw", ATTRS{{idVendor}}=="{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"'
    )


def _construct_comment(name: str, long_name: Tuple[str, ...]) -> str:
    return f"#  Rules for device {name}. {long_name}\n"


def _construct_rules() -> Tuple[str, ...]:
    """Returns tuple of rules for each single vendor id and product id."""
    return tuple(map(_construct_rule, PROFILES.keys()))


def _construct_comments() -> List[str]:
    devices: Tuple[Profile] = tuple(profile for profile in PROFILES.values())
    comments: List[str] = list()
    for device in devices:
        name = device["name"]
        long_name = tuple(model["long_name"] for model in device["models"])
        comments.append(_construct_comment(name, long_name))
    return comments
        
def get_udev() -> str:
    udev = "#  This file should not be edited manually.\n#  Use command xx.\n\n" #  TO-DO add command name for cli implementation.
    for comment, rule in zip(_construct_comments(), _construct_rules()):
        udev += (comment + rule + "\n\n")
    return udev

print(get_udev())