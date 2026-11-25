"""Settings treats the default display of a PC as a monitor."""

import unittest

import tree

OVERLAY = tree.REPO / "overlay/PcDesktopSettingsOverlay"


class SettingsOverlayTest(unittest.TestCase):

    def test_default_display_gets_the_monitor_settings(self):
        values = {(kind, name): value for kind, name, value, _ in tree.read_overlay_values(OVERLAY)}
        self.assertEqual(values.get(("bool", "config_defaultDisplayIsConnected")), "true")

    def test_overlay_targets_settings(self):
        manifest = (OVERLAY / "AndroidManifest.xml").read_text()
        self.assertIn('android:targetPackage="com.android.settings"', manifest)


if __name__ == "__main__":
    unittest.main()
