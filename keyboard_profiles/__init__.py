from . import RK68
from .profile_types import Profile, Model, Commands
from typing import List, Tuple, Dict
from types import ModuleType


def _create_profiles() -> Dict[Tuple[int, int], Profile]:
    profiles = {}
    for item in [globals()[name] for name in globals()]:
        if not isinstance(item, ModuleType):
            continue
        if not hasattr(item, "profile"):
            continue
        for model in item.profile["models"]:
            profile: Profile = item.profile.copy()
            vid_pid: Tuple[int, int] = (model["vendor_id"], model["product_id"])
            profiles[vid_pid] = profile
    return profiles


def get_profile(vid: int, pid: int) -> Profile:
    return PROFILES[(vid, pid)]


PROFILES = _create_profiles()
