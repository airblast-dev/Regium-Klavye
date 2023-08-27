"""
Regium Klavye

A simple API to control settings related to RGB and keymapping for supported keyboards.
"""

from .keyboard_parts import Keyboard, Key, KeyboardNotFound
from .keyboard_profiles import PROFILES
from . import udev
from . import rkapi
