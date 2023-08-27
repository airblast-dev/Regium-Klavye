from .keyboard_profiles import PROFILES
from .version import VERSION

UDEV_PATH = "/etc/udev/rules.d/99-rkapi.rules"


def _construct_rule(vid_pid: tuple[int, int]) -> str:
    # When formatting integer to hexadecimal string leading 0's are removed.
    # This adds the 0 values while still fitting in 4 characters so its valid.
    # 5e -> 005e
    return (
        f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=='
        f'"{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"\n'
        f'SUBSYSTEM=="hidraw", ATTRS{{idVendor}}=='
        f'"{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"'
    )


def _construct_comment(name: str, long_name: tuple[str, ...]) -> str:
    return f"# Rules for device {name}. {long_name}\n"


def _construct_rules() -> tuple[str, ...]:
    """Returns tuple of rules for each single vendor id and product id."""
    return tuple(map(_construct_rule, PROFILES.keys()))


def _construct_comments() -> list[str]:
    devices = tuple(profile for profile in PROFILES.values())
    comments: list[str] = list()
    for device in devices:
        name = device["name"]
        long_name = tuple(model["long_name"] for model in device["models"])
        comments.append(_construct_comment(name, long_name))
    return comments


def get_udev() -> str:
    """
    Generate udev rules.

    Example result:
    # This file should not be edited manually.
    # Run this command "regium_klavye udev -w" as root.
    # VERSION= current-version

    # Rules for device Royal Kludge RK68. ('Royal Kludge RK68 BT and USB',)
    SUBSYSTEM=="usb", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="005e", MODE="0666"
    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="005e", MODE="0666"
    """
    info_text = (
        f"# Regium Klavye {VERSION}\n# This file should not be edited manually.\n"
        '# Run "regium_klavye udev" as root to regenerate the rules.\n\n'
    )
    udev_rules: list[str] = [info_text]
    for comment, rule in zip(_construct_comments(), _construct_rules()):
        udev_rules.append("".join(comment + rule + "\n\n"))
    return "".join(udev_rules)


def _write_udev(path: str = UDEV_PATH, refresh_rules: bool = True) -> None:
    """Write the rules to udev path, requires administrator priveleges."""
    with open(path, "w") as file:
        file.write(get_udev())


def setup_rules(path=UDEV_PATH) -> None:
    """Write rules to udev path, reload rules and trigger them."""
    _write_udev(path=path)

    import subprocess

    # In case rules fail to reload automatically.
    subprocess.run(["udevadm", "control", "--reload"])

    # Force udev to trigger rules.
    subprocess.run(["udevadm", "trigger"])


def is_rules_up_to_date(path=UDEV_PATH) -> bool:
    from os.path import isfile

    if not isfile(path):
        return False
    from re import match

    udev_rules = open(path, "r")
    current_rules = udev_rules.read()
    udev_rules.close()
    current_version = match(
        r".*Regium\sKlavye\s([0-9]\.[0-9]\.[0-9])", current_rules
    ).group(  # type: ignore
        1
    )
    return current_version == VERSION
