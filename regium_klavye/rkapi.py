"""Regium Klavye is a library to control various settings for supported keyboards."""
import hid

from .keyboard_parts import Keyboard
from .keyboard_profiles import PROFILES


def _filter_device(device: dict) -> bool:
    valid_device_ids = set(PROFILES.keys())
    if (vid := device["vendor_id"], pid := device["product_id"]) in valid_device_ids:
        for model in PROFILES[(vid, pid)]["models"]:
            if model["endpoint"] == device["interface_number"]:
                return True
    return False


def _enumerate_devices(vid: int | None = None, pid: int | None = None) -> list[dict]:
    match vid, pid:
        case None, None:
            devices = hid.enumerate()
        case int(vid), None:
            devices = hid.enumerate(vid)
        case int(vid), int(pid):
            devices = hid.enumerate(vid, pid)
        case _, int(pid):
            raise ValueError("Cannot take product id without vendor id.")
        case _:
            raise TypeError(f"Expected int or None, found {type(vid)} and {type(pid)}")
    return [device for device in devices if _filter_device(device)]


def get_keyboards(vid: int | None = None, pid: int | None = None) -> list[Keyboard]:
    """Get all connected and supported keyboards.

    Providing a vendor ID will only return keyboards with matching information.
    Providing a product ID will only return keyboards with matching information.

    Args:
        vid: Optional[:class:`int`]
            Vendor ID of keyboards to get.
        pid: Optional[:class:`int`]
            Product ID of keyboards to get.
    """
    keyboards = [
        Keyboard(device["vendor_id"], device["product_id"], device["path"])
        for device in _enumerate_devices(vid, pid)
    ]
    keyboards.sort(key=lambda kb: kb.name + kb.long_name)

    return keyboards


def get_keyboard(vid: int, pid: int | None = None) -> Keyboard:
    """Get a single Keyboard object found with the provided vid and pid.

    If only a vendor ID is provided, returns first supported device matching vendor ID.
    If a supported device is not found NoKeyboardsFound exception is Raised.

    Args:
        vid: Vendor ID of keyboards to get.
        pid: Product ID of keyboards to get.

    Raises:
        KeyboardNotFoundError: Requested keyboard was not found.
    """
    for device in _enumerate_devices(vid, pid):
        return Keyboard(device["vendor_id"], device["product_id"], device["path"])

    raise KeyboardNotFoundError(vid, pid)


class KeyboardNotFoundError(Exception):
    """Raised if a single keyboard was requested but it wasnt found."""

    def __init__(self, vid: int, pid: int | None):
        super().__init__(
            f"Unable to find interface with the vendor id of "
            f"{vid} and product id of {pid}."
        )
