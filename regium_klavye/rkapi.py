"""Regium Klavye is a library to control various settings for supported keyboards."""
import hid

from .keyboard_parts import Keyboard
from .keyboard_profiles import PROFILES


def get_keyboards(vid: int | None = None, pid: int | None = None) -> list[Keyboard]:
    """Get all connected and supported keyboards.

    Providing a vendor ID will only return keyboards with matching information.
    Providing a product ID will only return keyboards with matching information.

    Parameters
    __________
    vid: Optional[:class:`int`]
        Vendor ID of keyboards to get.
    pid: Optional[:class:`int`]
        Product ID of keyboards to get.
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
            if device["interface_number"] == model["endpoint"]:
                keyboards.append(Keyboard(device["vendor_id"], device["product_id"]))
    keyboards.sort(key=lambda kb: kb.name + kb.long_name)
    return keyboards


def get_keyboard(vid: int, pid: int) -> Keyboard:
    """Get a single Keyboard object found with the provided vid and pid.

    If a supported device is not found NoKeyboardsFound exception is Raised.

    Args:
        vid: Vendor ID of keyboards to get.
        pid: Product ID of keyboards to get.

    Raises:
        KeyboardNotFoundError: Requested keyboard was not found.
    """
    for device in hid.enumerate(vid, pid):
        dev_profile = PROFILES.get((device["vendor_id"], device["product_id"]))
        if dev_profile is None:
            continue
        for model in dev_profile["models"]:
            if device["interface_number"] == model["endpoint"]:
                return Keyboard(device["vendor_id"], device["product_id"])
    raise KeyboardNotFoundError(vid, pid)


class KeyboardNotFoundError(Exception):
    """Raised if a single keyboard was requested but it wasnt found."""

    def __init__(self, vid: int, pid: int):
        super().__init__(
            f"Unable to find interface with the vendor id of "
            f"{vid} and product id of {pid}."
        )
