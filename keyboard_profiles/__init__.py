from . import RK68
import types


def _create_profiles():
    profiles = {}
    for item in [globals()[name] for name in globals()]:
        if not isinstance(item, types.ModuleType):
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


PROFILES: dict = _create_profiles()
