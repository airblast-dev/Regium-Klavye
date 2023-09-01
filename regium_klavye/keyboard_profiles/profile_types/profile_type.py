"""Profile type that represents a whole profile.

The actual profile is defined in the profiles folder. This is just for type checking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing import NotRequired

    from .commands import Commands
    from .model import Model


class Profile(TypedDict):
    name: str
    kb_size: tuple[int, int]
    models: tuple[Model, ...]
    commands: Commands
    present_keys: tuple[
        tuple[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]], ...
    ]
    layout: NotRequired[tuple[tuple[str | None, int], ...]]
