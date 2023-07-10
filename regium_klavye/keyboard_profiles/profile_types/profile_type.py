from typing import TypedDict, NotRequired
from .commands import Commands
from .model import Model

#  This is not used in the application or testing.
#  It serves as an example structure for development purposes.


class Profile(TypedDict):
    name: str
    kb_size: tuple[int, int]
    models: tuple[Model, ...]
    commands: Commands
    present_keys: tuple[
        tuple[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]], ...
    ]
    layout: NotRequired[tuple[tuple[str | None, int], ...]]
