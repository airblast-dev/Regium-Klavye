"""
Regium Klavye

A simple API to control settings related to RGB and keymapping for supported keyboards.
"""

from .keyboard_parts import Keyboard, Key, KeyboardNotFound  # noqa: F401
from .keyboard_profiles import PROFILES  # noqa: F401
from . import udev  # noqa: F401
from . import rkapi  # noqa: F401
