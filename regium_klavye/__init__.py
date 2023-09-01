"""Regium Klavye is a command line application and API for Royal Kludge keyboards.

Regium Klavye provides simple API to control settings related to RGB and
keymapping for supported keyboards.
For a full list of supported actions please read the documentation.
"""

from . import rkapi, udev
from .keyboard_parts import AnimationNotSetError, Key, Keyboard, KeyNotFoundError
from .keyboard_profiles import PROFILES
