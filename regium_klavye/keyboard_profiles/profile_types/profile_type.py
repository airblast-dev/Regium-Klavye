from typing import NotRequired, TypedDict

from .commands import Commands
from .model import Model

# The profile type is defined for hatch optimization
# and support for pylance or pyright...


class Profile(TypedDict):
    name: str
    kb_size: tuple[int, int]
    models: tuple[Model, ...]
    commands: Commands
    present_keys: tuple[
        tuple[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]], ...
    ]
    layout: NotRequired[tuple[tuple[str | None, int], ...]]
