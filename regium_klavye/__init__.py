"""
Regium Klavye

A simple API to control settings related to RGB and keymapping for supported keyboards.
"""

from . import rkapi, udev
from .keyboard_parts import Key, Keyboard, KeyboardNotFound
from .keyboard_profiles import PROFILES
