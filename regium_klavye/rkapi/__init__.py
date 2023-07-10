"""
Regium Klavye 

A simple API to control settings related to RGB and keymapping for supported keyboards.
"""
import hid
from .keyboard_parts import Keyboard, KeyboardNotFound
from .keyboard_profiles import PROFILES
from .udev import setup_rules, get_udev, is_rules_up_to_date, UDEV_PATH


def get_keyboards(vid: int | None = None, pid: int | None = None) -> list[Keyboard]:
    """
    Returns a list of Keyboards for supported keyboards.

    If a vid and/or pid value is provided it will only return keyboards found with provided values.

    :param vid: Vendor ID to search keyboards with a specific vendor.
    :param pid: Product ID to specify a model of keyboard.
    :type vid: int
    :type pid: int
    :rtype: list[Keyboard]
    :raise NoKeyboardsFound: Unable to find any supported keyboard.
    """
    keyboards = []
    if vid is None and pid is None:
        enumerated_devices = hid.enumerate()
    elif vid is not None and pid is None:
        enumerated_devices = hid.enumerate(vid)
    else:
        enumerated_devices = hid.enumerate(vid, pid)
    for device in enumerated_devices:
        dev_profile = PROFILES.get((device["vendor_id"], device["product_id"]))
        if dev_profile is None:
            continue
        for model in dev_profile["models"]:
            if (
                model["usage"] == device["usage"]
                and model["usage_page"] == device["usage_page"]
            ):
                keyboards.append(Keyboard(device["vendor_id"], device["product_id"]))
    if not keyboards:
        raise NoKeyboardsFound()

    return sorted(keyboards, key=lambda kb: kb.name + kb.long_name)


def get_keyboard(vid: int, pid: int) -> Keyboard:
    """
    Returns a single Keyboard object found with the provided vid and pid.

    If a supported device is not found NoKeyboardsFound exception is Raised.
    """
    for device in hid.enumerate(vid, pid):
        dev_profile = PROFILES.get((device["vendor_id"], device["product_id"]))
        if dev_profile is None:
            continue
        for model in dev_profile["models"]:
            if (
                model["usage"] == device["usage"]
                and model["usage_page"] == device["usage_page"]
            ):
                return Keyboard(device["vendor_id"], device["product_id"])
    raise KeyboardNotFound(vid, pid)


class NoKeyboardsFound(Exception):
    def __init__(self) -> None:
        super().__init__(f"Unable to find any supported keyboards.")
