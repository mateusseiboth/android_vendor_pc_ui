"""Settings opens on the desktop layout, with the Device category (mouse, touchpad, keyboard)."""

import unittest

import tree

OVERLAY = tree.REPO / "overlay/PcDesktopSettingsOverlay"


class SettingsOverlayTest(unittest.TestCase):

    def test_device_category_is_shown(self):
        values = {(kind, name): value for kind, name, value, _ in tree.read_overlay_values(OVERLAY)}
        self.assertEqual(values.get(("bool", "config_show_top_level_device_category")), "true")

    def test_overlay_targets_settings(self):
        manifest = (OVERLAY / "AndroidManifest.xml").read_text()
        self.assertIn('android:targetPackage="com.android.settings"', manifest)


if __name__ == "__main__":
    unittest.main()
