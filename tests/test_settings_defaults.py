"""First-boot defaults of the settings provider overlay."""

import unittest

import tree

SETTINGS_OVERLAY = tree.REPO / "overlay/PcDesktopSettingsProviderOverlay"


def read_default(name):
    values = {n: v for _, n, v, _ in tree.read_overlay_values(SETTINGS_OVERLAY)}
    return values.get(name)


class SettingsDefaultsTest(unittest.TestCase):
    # Many PCs have no Bluetooth controller, and the Bluetooth stack aborts when the HAL finds
    # none: Bluetooth starts off, and turning it on once keeps it on.
    def test_bluetooth_starts_off(self):
        self.assertEqual(read_default("def_bluetooth_on"), "false")


if __name__ == "__main__":
    unittest.main()
