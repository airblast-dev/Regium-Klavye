from .profile_types import Profile, Model, Commands
from typing import List, Tuple, Dict

_profiles = dict()


#  This used to work via importing  the profiles and then calling globals.
#  This caused bad performance as a bunch of checks had to be done while contstructing PROFILE.
#  It also removed the need to use the types module which also affects performance and uses ~0.2 Mb of RAM.
#  The main benefit is that this solution allows for more flexability when it comes to imports and etc.
def _create_profiles() -> Dict[Tuple[int, int], Profile]:
    from .profiles import RK68

    #  All profiles should be imported above.

    local_imports = locals()
    #  Take locals right after import so we can use create and use other variables.

    _profiles: dict[Tuple[int, int], Profile] = dict()

    #  The for loop iterates every module imported. Which we then call getattr to get the profile variable inside.
    for module in local_imports.values():
        profile: Profile = module.profile
        for model in profile["models"]:
            _profiles[(model["vendor_id"], model["product_id"])] = profile
    return _profiles


def get_profile(vid: int, pid: int) -> Profile:
    return PROFILES[(vid, pid)]


PROFILES = _create_profiles()
