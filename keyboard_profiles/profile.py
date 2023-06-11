from typing import TypedDict, List, Tuple, Dict
from .profile_types import Commands, Model


class Profile(Dict):
    name: str
    models: List[Model]
    commands: Commands
    present_keys: List[Tuple[str, Tuple[Tuple[int, int], Tuple[int, int],
                                        Tuple[int, int]]]]
