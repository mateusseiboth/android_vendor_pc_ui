"""Apps of LineageOS the PC build leaves out."""

import re
import unittest

import tree

# Left out on request: the audio recorder (Lineage's Recorder).
EXCLUDED = {"Recorder"}

_OVERRIDES_RE = re.compile(r'overrides:\s*\[([^\]]*)\]')


def read_overridden_modules():
    """Modules the overlays of the repo keep from being installed (their `overrides`)."""
    found = set()
    for overlay_dir, _ in tree.find_overlays():
        for match in _OVERRIDES_RE.finditer((overlay_dir / "Android.bp").read_text()):
            found |= set(re.findall(r'"([^"]+)"', match.group(1)))
    return found


class ExcludedAppsTest(unittest.TestCase):
    def test_excluded_apps_are_overridden(self):
        self.assertTrue(EXCLUDED <= read_overridden_modules())


if __name__ == "__main__":
    unittest.main()
