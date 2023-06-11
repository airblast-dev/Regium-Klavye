from typing import TypedDict, List, Tuple, Dict
from commands import Commands
from model import Model

#  This is not used in the application or testing.
#  It serves as an example structure for development purposes.


class Profile(TypedDict):
    name: str
    models: Tuple[Model]
    commands: Commands
    present_keys: Tuple[Tuple[str, Tuple[Tuple[int, int], Tuple[int, int],
                                        Tuple[int, int]]], ...]