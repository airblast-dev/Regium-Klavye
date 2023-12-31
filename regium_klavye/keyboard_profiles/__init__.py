"""Profile generator for device profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .profile_types import Profile


def _create_profiles() -> dict[tuple[int, int], "Profile"]:
    from .profiles import RK68

    # All profiles should be imported above.

    local_imports = locals()
    # Take locals right after import so we can use create and use other variables.

    _profiles: dict[tuple[int, int], Profile] = dict()

    for module in local_imports.values():
        profile: "Profile" = module.profile
        for model in profile["models"]:
            _profiles[(model["vendor_id"], model["product_id"])] = profile
    return _profiles


def get_profile(vid: int, pid: int) -> Profile:
    """Get a specific keyboards profile."""
    return PROFILES[(vid, pid)]


PROFILES = _create_profiles()
