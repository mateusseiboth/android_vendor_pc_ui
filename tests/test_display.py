"""Monitors run at their own refresh rate: no phone cap on how often Android draws."""

import unittest

import tree

FRAMEWORK = tree.REPO / "overlay/PcDesktopFrameworkOverlay"


class RefreshRateTest(unittest.TestCase):

    def test_render_rate_is_not_capped(self):
        values = {(kind, name): value for kind, name, value, _ in tree.read_overlay_values(FRAMEWORK)}
        self.assertEqual(values.get(("integer", "config_defaultRefreshRate")), "0")


if __name__ == "__main__":
    unittest.main()
