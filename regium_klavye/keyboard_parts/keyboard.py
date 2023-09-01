from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

import hid

from ..helpers import parse_params
from ..keyboard_profiles import PROFILES
from . import Key

if TYPE_CHECKING:
    from typing import Iterator

    from ..keyboard_profiles.profile_types.commands import AnimationParam, ColorParam


class Keyboard:
    """Represents a Keyboard for ease of use for rebinding keys and RGB controls.

    Iterating over this object will yield each Key that it capsulates.
    This is to simplify setting all of the keys to an RGB value, set
    animations or remap keys.

    Args:
        vid: Vendor ID of keyboards to get.
        pid: Product ID of keyboards to get.
    """

    __slots__ = (
        "_name",
        "_anim_params",
        "_kb_size",
        "_vid",
        "_pid",
        "_keys",
        "_colors",
        "_model",
        "_final_anim_data",
        "_final_color_data",
        "_anim_base",
        "_anim_options",
        "_layout",
        "_current_color_params",
        "_color_params",
        "_anim_padding",
        "_has_rgb",
        "_has_anim",
        "_has_custom_anim",
    )

    def __init__(self, vid: int, pid: int):
        _profile = PROFILES[(vid, pid)]
        self._name: str = _profile["name"]
        self._vid: int = vid
        self._pid: int = pid

        self._keys: dict[str, Key] = {
            key[0]: Key(*key) for key in _profile["present_keys"]
        }

        self._layout = _profile.get("layout")

        for model in _profile["models"]:
            if model["vendor_id"] == self._vid and model["product_id"] == self._pid:
                self._model = model

        self._anim_options = _profile["commands"]["animations"]["options"]
        self._anim_params = _profile["commands"]["animations"]["params"]
        self._anim_base: list[int] = _profile["commands"]["animations"]["base"]
        self._final_anim_data: bytearray
        self._colors = _profile["commands"]["colors"]
        self._color_params = _profile["commands"]["colors"]["color_params"]["params"]
        self._kb_size = _profile["kb_size"]
        self._current_color_params: dict[str, list[int]] = {}
        self._anim_padding = _profile["commands"]["animations"]["padding"]
        self._has_rgb = self._model["has_rgb"]
        self._has_anim = self._model["has_anim"]
        self._has_custom_anim = self._model["has_custom_anim"]

    @property
    def name(self) -> str:
        """Short name of the keyboard.

        Excludes special editions and such descriptions in the name.
        """
        return self._name

    @property
    def long_name(self) -> str:
        """Long name of the keyboard.

        Includes the full name of the keyboard.
        This often includes supported connection methods or special edition naming.
        """
        return self._model["long_name"]

    @property
    def valid_keys(self) -> list[str]:
        """Get all key labels on this keyboard."""
        return sorted(self._keys.keys())

    @property
    def anim_options(self) -> list[str]:
        """Get supported animation options.

        This only returns the animation names supported on this keyboard.
        """
        return sorted(self._anim_options.keys())

    @property
    def anim_params(self) -> dict[str, AnimationParam]:
        """Get supported animation parameters."""
        return self._anim_params

    @property
    def color_params(self) -> dict[str, ColorParam]:
        """Get parameter choices for color settings."""
        return self._color_params

    @property
    def has_rgb(self) -> bool:
        """Check if keyboard supports RGB settings."""
        return self._has_rgb

    @property
    def has_anim(self) -> bool:
        """Check if keyboard supports animation settings."""
        return self._has_anim

    @property
    def has_custom_anim(self) -> bool:
        """Check if keyboard supports custom animations."""
        return self._has_custom_anim

    def __len__(self) -> int:
        """Get number of keys."""
        return len(self._keys)

    def __getitem__(self, key: str) -> Key:
        """Get corresponding Key object with the key label provided."""
        return self._keys[key]

    def __iter__(self) -> Iterator[Key]:
        """Iterate over each key found on the keyboard."""
        yield from self._keys.values()

    def __repr__(self) -> str:
        """Get keyboard as string."""
        return (
            f"Keyboard(name={self.name}, "
            f"long_name={self.long_name}, _vid={self._vid}, _pid={self._pid})"
        )

    def set_key_color(self, key: str, rgb: tuple[int, int, int]) -> None:
        """Set RGB values for only a specific key.

        Args:
            key: Label for the specified key.
            rgb: Red green and blue value.
        """
        if key in self.valid_keys:
            self[key].set_color(rgb)
            return
        raise KeyNotFoundError(self.name, key)

    def set_color(
        self, rgb: tuple[int, int, int], options: dict[str, int] | None = None
    ) -> None:
        """Set all key objects present to the provided color.

        Args:
            rgb: Red green and blue values.

            options: A dictionary of options for the color setting.
                The string value (depending on what options the keyboard can provide)
                can be "sleep" or something alike depending on what is available for the
                keyboard.

                The integer is the value for whatever settings that corresponds.

                To get the accepted options for color settings, the
                :attr:`~color_param_choices` property can be used.
        """
        for key in self:
            key.set_color(rgb)

        parse_params(options, self._color_params)  # type: ignore

    def set_color_params(self, options: dict[str, int]):
        """Set color parameters.

        Args:
            options: A dictionary of options for the color setting.

                The string value (depending on what options the keyboard can provide)
                can be "sleep" or something alike depending on what is available for the
                keyboard.

                The integer is the value for whatever settings that corresponds.
        """
        self._current_color_params = parse_params(
            options, self._color_params  # type: ignore
        )

    def _color_data(self) -> None:
        """Construct final bytes to be written for static color selection."""
        steps: list[list[int]] = self._colors["steps"]
        # The steps are the blank version of the data to be sent.
        for valid_key in self.valid_keys:
            key: Key = self._keys[valid_key]
            # Zipping results in iterating each key color index and each rgb value.
            # As result indexes first value is the step count and the second value
            # is its index on that step.
            # Each value for indexes is an index for each color.

            # Basically its iterating over:
            # ((red_step, red_index), red_value),
            # ((green_step, green_index), green_value)...
            for indexes, color in zip(key.indexes, key.get_color()):
                step_index = indexes[0]  # responds to the nth list for the data.
                color_index = indexes[1]  # responds to index in that list.
                steps[step_index][color_index] = color

        param_base = self._colors["color_params"]["base"]
        new_param = list(param_base)
        for param in self._current_color_params.values():
            new_param += param
        new_param += (self._anim_padding - len(new_param)) * [0x00]
        steps.append(new_param)

        self._final_color_data: tuple[bytearray, ...] = tuple(map(bytearray, steps))

    def apply_color(
        self,
        rgb: tuple[int, int, int] | None = None,
    ) -> tuple[bytearray, ...]:
        """Write the final data to the interface.

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

    def set_animation(
        self,
        anim_name: str,
        options: dict[str, int] | None = None,
    ) -> None:
        """Set a specific animation with its parameters.

        If no option is provided defaults will be used.
        If options are partially provided such as sleep but no speed setting.
        The default will be used to fill the rest in.

        Keyword arguments should be only used when you already
        know the keyboard supports said parameter.

        Args:
            anim_name: To get the accepted animation names for this keyboard, the
                :attr:`~anim_options` property can be used.
            options: To get the accepted animation parameters for this keyboard, the
                :attr:`~anim_params` property can be used.
        """
        new_options = parse_params(options, self._anim_params)  # type: ignore

        anim_data: list[int] = self._anim_base + self._anim_options[anim_name]["value"]
        for option in new_options.values():
            anim_data.extend(option)

        self._final_anim_data = bytearray(
            anim_data + (self._anim_padding - len(anim_data)) * [0x00]
        )

    def apply_animation(self) -> bytearray:
        """Apply the previously set animation to the keyboard."""
        if not self._final_anim_data:
            raise AnimationNotSetError
        for interface in hid.enumerate():
            if (
                interface["usage_page"] != self._model["usage_page"]
                or interface["usage"] != self._model["usage"]
            ):
                continue
            dev = hid.device()
            dev.open_path(interface["path"])
            report_type = self._colors["report_type"]
            if report_type == 0x02:
                dev.send_feature_report(self._final_anim_data)
            elif report_type == 0x03:
                dev.write(self._final_anim_data)

            dev.close()
            sleep(0.01)
        data = self._final_anim_data
        return data

    def apply_custom_animation(self, animation: str):
        """TODO"""  # noqa
        raise NotImplementedError


class KeyNotFoundError(Exception):
    """Raised if a key is not found on a keyboard."""

    def __init__(self, keyboard_model: str, key: str):
        super().__init__(f"The {key} key was not found on {keyboard_model}.")


class AnimationNotSetError(Exception):
    """Raised if an animation is applied without setting first."""

    def __init__(self) -> None:
        super().__init__(
            "No animation has been specified. Before calling this "
            "function you must set an animation using set_animation."
        )
