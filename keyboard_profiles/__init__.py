from . import RK68
from .profile import Profile
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
            profile = item.profile.copy()
            vid_pid = (model["vendor_id"], model["product_id"])
            profiles[vid_pid] = profile
    return profiles


def get_profile(vid, pid):
    return PROFILES[(vid, pid)]


PROFILES: Dict[Tuple[int, int], Profile] = _create_profiles()
