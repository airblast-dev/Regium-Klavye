from collections.abc import Iterator
from itertools import repeat
from pickle import LIST
from time import sleep
from typing import Iterator, overload, Optional, Tuple, List, Dict, Literal, Union
from collections import deque

import hid

from .key import Key
from keyboard_profiles import PROFILES
from keyboard_profiles.profile_types import (
    Profile,
    Colors,
    AnimationParam,
    AnimationOption,
)


class Keyboard:
    """
    Represents a Keyboard for ease of use for rebinding keys and RGB controls.

    Iterating over this object will yield each Key that it capsulates.
    This is to simplify setting all of the keys to an RGB value.

    To get a specific Key the dictionary syntax can be used.
        Example: Keyboard(0x0258A, 0x005E, 0x00)["A"]


    name: :class:`str`
        Basic name that represents the keyboard.

    keys: :list[:class:`Key`]

    valid_keys: set[:class:`str`]
        All keys present on the keyboard.
    """

    __slots__ = (
        "valid_keys",
        "name",
        "long_name",
        "animations",
        "anim_params",
        "_vid",
        "_pid",
        "_keys",
        "_colors",
        "_final_data",
        "_model",
        "_final_anim_data",
        "_final_color_data",
        "_anim_base",
        "_anims",
    )

    def __init__(self, vid: int, pid: int):
        _profile = PROFILES[(vid, pid)]
        self.name: str = _profile["name"]
        self._vid: int = vid
        self._pid: int = pid
        self._keys: Dict[str, Key] = {
            key[0]: Key(*key) for key in _profile["present_keys"]
        }
        for model in _profile["models"]:
            if model["vendor_id"] == self._vid and model["product_id"] == self._pid:
                self._model = model
        self.valid_keys: list[str] = sorted(self._keys.keys())
        self.long_name: str = self._model["long_name"]
        self._anims: Dict[str, AnimationOption] = _profile["commands"]["animations"][
            "animation_options"
        ]
        self.animations: List[str] = sorted(self._anims.keys())
        self.anim_params: Dict[str, AnimationParam] = _profile["commands"][
            "animations"
        ]["animation_params"]
        self._anim_base: list[int] = _profile["commands"]["animations"]["base"]
        self._colors: Colors = _profile["commands"]["colors"]
        self._final_anim_data: bytearray
        self._final_color_data: tuple[bytearray, ...]

    def __len__(self) -> int:
        """Returns number of keys."""
        return len(self._keys)

    def __getitem__(self, key: str) -> Key:
        """
        Get corresponding Key object with the key label provided.
        """
        return self._keys[key]

    def __iter__(self) -> Iterator[Key]:
        """Yields each key found on the keyboard."""
        yield from self._keys.values()

    def __repr__(self) -> str:
        return f"Keyboard(name={self.name}, long_name={self.long_name}, _vid={self._vid}, _pid={self._pid})"

    def set_key_color(self, key: str, rgb: Tuple[int, int, int]) -> None:
        """Sets RGB values for only a specific key."""

        if key in self.valid_keys:
            self[key].set_color(rgb)
            return
        raise KeyNotFoundError(self.name, key)

    def set_color(self, rgb: Tuple[int, int, int]) -> None:
        """Set all key objects present to the provided color."""
        tuple(map(self._set_key_color, self, repeat(rgb)))

    def _set_key_color(self, key: Key, rgb: Tuple[int, int, int]) -> None:
        key.set_color(rgb)

    def _color_data(self) -> None:
        """Construct final bytes to be written for static color selection."""
        steps: Tuple[List[int]] = self._colors["steps"]
        #  The steps are the blank version of the data to be sent.

        for valid_key in self.valid_keys:
            key: Key = self._keys[valid_key]

            #  Zipping results in iterating each key color index and each rgb value.
            #  As result indexes first value is the step count and the second value is its index on that step.
            #  Each value for indexes is an index for each color.
            #  Basically its iterating over ((red_step, red_index), red_value), ((green_step, green_index), green_value)...
            for indexes, color in zip(key.indexes, key.get_color()):
                step_index = indexes[0]
                color_index = indexes[1]
                steps[step_index][color_index] = color

        self._final_color_data: Tuple[bytearray, ...] = tuple(map(bytearray, steps))

    def apply_color(
        self,
        rgb: Optional[Tuple[int, int, int]] = None,
    ) -> tuple[bytearray, ...]:
        """
        Write the final data to the interface.

        An rgb can also be provided to set and apply with a single call.
        The rgb value (if provided) will be applied to all keys.
        """
        if rgb:
            self.set_color(rgb)
        self._color_data()
        for interface in hid.enumerate(self._vid, self._pid):
            if (
                interface["usage_page"] != self._model["usage_page"]
                or interface["usage"] != self._model["usage"]
            ):
                continue
            dev = hid.device()
            dev.open_path(interface["path"])
            dev.set_nonblocking(True)
            report_type: int = self._colors["report_type"]

            for data in self._final_color_data:
                if report_type == 0x02:
                    dev.send_feature_report(data)
                elif report_type == 0x03:
                    dev.write(data)

                #  Writing data too fast can cause incorrect settings to be set.
                sleep(0.01)

            dev.close()
            break
        return self._final_color_data

    def _construct_anim_params(
        self,
        anim_name: str,
        options: Optional[dict[str, int]] = None,
        kw_options: Optional[dict[str, int]] = None,
    ) -> dict:
        """
        Construct new options with defaults for missing values.

        This will also check if provided values are in valid range for said parameter.
        """
        if anim_name not in self._anims.keys():
            raise ValueError(
                f"{anim_name} was not found in the profile of {self.name}."
            )
        temp_options: Optional[dict[str, int]] = options or kw_options or None
        new_options: dict[str, List[int]] = {
            "animation": self._anims[anim_name]["value"]
        }
        if temp_options is None:
            # Returns defaults for parameters with the animation value if no parameter is provided.
            default_options: dict[str, List[int]] = {
                param: param_inf["default"]
                for param, param_inf in self.anim_params.items()
            }
            new_options.update(default_options)
            return new_options

        #  In some cases values provided can be a single number or list of values. This is to allow both parameter types.
        _options: Dict[str, List[int]] = {
            key: [value] for key, value in temp_options.items()
        }

        # Fill in missing values with defaults. This also does this in the correct order defined in profiles.
        for key in self.anim_params.keys():
            is_valid: bool = False
            if key not in _options.keys():
                new_options[key] = self.anim_params[key]["default"]
                continue

            # Checks if provided value is a accepted parameter.
            if callable(self.anim_params[key]["checks"]):
                is_valid = self.anim_params[key]["checks"](_options[key])
            elif isinstance(self.anim_params[key]["checks"], (tuple, list, range)):
                is_valid = all(
                    [
                        value in self.anim_params[key]["checks"]
                        for value in _options[key]
                    ]
                )

            if is_valid is True:
                new_options[key] = _options[key]
                continue
            raise ValueError(f"Invalid value provided for {key}.")

        return new_options

    @overload
    def set_animation(self, anim_name: str, options: Optional[dict[str, int]]) -> None:
        ...

    @overload
    def set_animation(self, anim_name: str, **kw_options) -> None:
        ...

    def set_animation(
        self,
        anim_name: str,
        options: Optional[Dict[str, int]] = None,
        **kw_options,
    ) -> None:
        """
        Set a specific animation with its parameters.

        Options can either be provided as a dictionary or via keywords, if no option is provided defaults will be used.
        If options are partially provided such as sleep but no speed setting. The default will be used to fill the rest in.
        """
        new_options: dict[str, List[int]] = self._construct_anim_params(
            anim_name, options, kw_options
        )
        anim_data: List[int] = self._anim_base
        for option in new_options.values():
            anim_data.extend(option)
        self._final_anim_data = bytearray(
            anim_data + [*((65 - len(anim_data)) * [0x00])]
        )

    def apply_animation(self) -> bytearray:
        """Apply the set animation to the keyboard."""
        if self._final_anim_data:
            raise AnimationNotSet
        for interface in hid.enumerate():
            if (
                interface["usage_page"] != self._model["usage_page"]
                or interface["usage"] != self._model["usage"]
            ):
                continue
            dev = hid.device()
            dev.open_path(interface["path"])
            report_type: Literal[0x02, 0x03] = self._colors["report_type"]
            if report_type == 0x02:
                dev.send_feature_report(self._final_anim_data)
            elif report_type == 0x03:
                dev.write(self._final_anim_data)

            dev.close()
            sleep(0.01)
        data = self._final_anim_data
        self._final_data = None
        return data


class KeyNotFoundError(Exception):
    """Raised if a key is not found on a keyboard."""

    def __init__(self, keyboard_model: str, key: str):
        super().__init__(f"The {key} key was not found on {keyboard_model}.")


class KeyboardNotFound(Exception):
    def __init__(self, vid: int, pid: int):
        super().__init__(
            f"Unable to find interface with the vendor id of {vid} and product id of {pid}."
        )


class AnimationNotSet(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No animation has been specified. Before calling this function you must set an animation using set_animation."
        )
