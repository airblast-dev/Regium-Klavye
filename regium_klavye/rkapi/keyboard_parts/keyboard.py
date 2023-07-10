from itertools import repeat
from time import sleep
from typing import Iterator, overload

import hid

from ..keyboard_parts import Key
from ..keyboard_profiles import PROFILES
from ..helpers import parse_params


class Keyboard:
    """
    Represents a Keyboard for ease of use for rebinding keys and RGB controls.

    Iterating over this object will yield each Key that it capsulates.
    This is to simplify setting all of the keys to an RGB value, set animations or remap keys.
    """

    __slots__ = (
        "_name",
        "_anim_params",
        "_kb_size",
        "_vid",
        "_pid",
        "_keys",
        "_colors",
        "_final_data",
        "_model",
        "_final_anim_data",
        "_final_color_data",
        "_anim_base",
        "_anim_options",
        "layout",
        "_color_param_base",
        "_current_color_params",
        "_color_params",
        "_color_padding",
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

        self.layout = _profile.get("layout")
        self._kb_size = _profile["kb_size"]

        for model in _profile["models"]:
            if model["vendor_id"] == self._vid and model["product_id"] == self._pid:
                self._model = model

        self._anim_options = _profile["commands"]["animations"]["options"]
        self._anim_params = _profile["commands"]["animations"]["params"]
        self._anim_base: list[int] = _profile["commands"]["animations"]["base"]
        self._final_anim_data: bytearray
        self._final_color_data: tuple[bytearray, ...]
        self._colors = _profile["commands"]["colors"]
        self._color_param_base = _profile["commands"]["colors"]["color_params"]["base"]
        self._color_params = _profile["commands"]["colors"]["color_params"]["params"]
        self._kb_size = _profile["kb_size"]
        self._current_color_params: dict[str, list[int]] = {}
        self._color_padding = self._colors["padding"]
        self._anim_padding = _profile["commands"]["animations"]["padding"]
        self._has_rgb = self._model["has_rgb"]
        self._has_anim = self._model["has_anim"]
        self._has_custom_anim = self._model["has_custom_anim"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def long_name(self) -> str:
        return self._model["long_name"]

    @property
    def valid_keys(self) -> list[str]:
        return sorted(self._keys.keys())

    @property
    def anim_options(self) -> list[str]:
        return sorted(self._anim_options.keys())

    @property
    def anim_param_choices(self) -> dict[str, tuple[tuple[int], str]]:
        return {
            k: (v["choices"], v["description"]) for k, v in self._anim_params.items()
        }

    @property
    def color_param_choices(self) -> dict[str, tuple[int, ...]]:
        return {k: v["choices"] for k, v in self._color_params.items()}

    @property
    def has_rgb(self) -> bool:
        return self._has_rgb

    @property
    def has_anim(self) -> bool:
        return self._has_anim

    @property
    def has_custom_anim(self) -> bool:
        return self._has_custom_anim

    @property
    def width(self) -> int:
        return self._kb_size[0]

    @property
    def height(self) -> int:
        return self._kb_size[1]

    def get_anim_choice(self, param: str) -> tuple[int, ...]:
        return self._anim_params[param]["choices"]

    def get_param_choice(self, param: str) -> tuple[int, ...]:
        return self._color_params[param]["choices"]

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

    def set_key_color(self, key: str, rgb: tuple[int, int, int]) -> None:
        """Sets RGB values for only a specific key."""

        if key in self.valid_keys:
            self[key].set_color(rgb)
            return
        raise KeyNotFoundError(self.name, key)

    def set_color(self, rgb: tuple[int, int, int] | list[int]) -> None:
        """Set all key objects present to the provided color."""
        for key in self:
            key.set_color(rgb)

    def set_color_params(self, options: dict[str, int]):
        self._current_color_params = parse_params(options, self._color_params)  # type: ignore

    def _color_data(self) -> None:
        """Construct final bytes to be written for static color selection."""
        steps: list[list[int]] = self._colors["steps"]
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
        param_base = self._colors["color_params"]["base"]
        new_param = list(param_base)
        for param in self._current_color_params.values():
            new_param += param
        new_param += (self._anim_padding - len(new_param)) * [0x00]
        steps.append(new_param)

        self._final_color_data: tuple[bytearray, ...] = tuple(map(bytearray, steps))

    def apply_color(
        self,
        rgb: tuple[int, int, int] | list[int] | None = None,
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

    def set_animation(
        self,
        anim_name: str,
        options: dict[str, int] | None = None,
    ) -> None:
        """
        Set a specific animation with its parameters.

        Options can either be provided as a dictionary or via keywords, if no option is provided defaults will be used.
        If options are partially provided such as sleep but no speed setting. The default will be used to fill the rest in.

        Keyword arguments should be only used when you already know the keyboard supports said parameter.
        """

        new_options = {"base": self._anim_options[anim_name]["value"]}
        new_options.update(parse_params(options, self._anim_params))

        anim_data: list[int] = self._anim_base
        for option in new_options.values():
            anim_data.extend(option)

        self._final_anim_data = bytearray(
            anim_data + (self._anim_padding - len(anim_data)) * [0x00]
        )

    def apply_animation(self) -> bytearray:
        """Apply the previously set animation to the keyboard."""
        if not self._final_anim_data:
            raise AnimationNotSet
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
        self._final_data = None
        return data

    def apply_custom_animation(self, animation: str):
        raise NotImplemented


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
