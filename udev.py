from keyboard_profiles import PROFILES


UDEV_PATH = "/etc/udev/rules.d/99-rkapi.rules"


def _construct_rule(vid_pid: tuple[int, int]) -> str:
    #  When formatting integer to hexadecimal string leading 0's are removed.
    #  This adds the 0 values while still fitting in 4 characters so its valid.
    #  5e -> 005e
    return (
        f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"\n'
        + f'SUBSYSTEM=="hidraw", ATTRS{{idVendor}}=="{vid_pid[0]:>04x}", ATTRS{{idProduct}}=="{vid_pid[1]:>04x}", MODE="0666"'
    )


def _construct_comment(name: str, long_name: tuple[str, ...]) -> str:
    return f"#  Rules for device {name}. {long_name}\n"


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
    #  This file should not be edited manually.
    #  Use command

    #  Rules for device Royal Kludge RK68. ('Royal Kludge RK68 BT and USB',)
    SUBSYSTEM=="usb", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="005e", MODE="0666"
    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="005e", MODE="0666"
    """
    udev = "#  This file should not be edited manually.\n#  Use command xx.\n\n"  #  TO-DO add command name for cli implementation.
    for comment, rule in zip(_construct_comments(), _construct_rules()):
        udev += comment + rule + "\n\n"
    return udev


def write_udev(path: str = UDEV_PATH, refresh_rules: bool = True) -> None:
    """Write the rules to udev path, requires administrator priveleges."""
    with open(path, "w") as file:
        file.write(get_udev())


def setup_rules() -> None:
    """Write rules to udev path, reload rules and trigger them."""
    write_udev()

    import subprocess

    #  In case rules fail to reload automatically.
    subprocess.run(["udevadm", "control", "--reload"])

    #  Force udev to trigger rules.
    subprocess.run(["udevadm", "trigger"])
