"""The framework overlay carries Googlebook's desktop values (FrameworkDesktopOverlay, lapis)."""

import unittest

import tree

FRAMEWORK_SPEC = {
    ("bool", "config_isDesktopModeSupported"): "true",
    ("bool", "config_canInternalDisplayHostDesktops"): "true",
    ("bool", "config_enterDesktopByDefaultOnFreeformDisplay"): "true",
    ("bool", "config_showHomeBehindDesktop"): "true",
    ("dimen", "desktop_view_default_header_height"): "40dp",
    ("dimen", "status_bar_height_default"): "36dp",
    ("dimen", "status_bar_height_portrait"): "36dp",
    ("dimen", "config_dialogCornerRadius"): "28dp",
    ("integer", "config_navBarInteractionMode"): "2",
    ("bool", "config_buttonTextAllCaps"): "false",
}

SETTINGS_PROVIDER_SPEC = {
    ("integer", "def_screen_off_timeout"): "600000",
    ("bool", "def_sound_effects_enabled"): "false",
}


def read_values(overlay_name):
    overlay_dir = tree.REPO / "overlay" / overlay_name
    return {(kind, name): value for kind, name, value, values_dir in
            tree.read_overlay_values(overlay_dir) if values_dir == "values"}


class GooglebookSpecTest(unittest.TestCase):

    def assert_spec(self, overlay_name, spec):
        values = read_values(overlay_name)
        for key, expected in spec.items():
            with self.subTest(resource=f"{key[0]}/{key[1]}"):
                self.assertEqual(values.get(key), expected)

    def test_framework_overlay_matches_googlebook(self):
        self.assert_spec("PcDesktopFrameworkOverlay", FRAMEWORK_SPEC)

    def test_settings_provider_overlay_matches_googlebook(self):
        self.assert_spec("PcDesktopSettingsProviderOverlay", SETTINGS_PROVIDER_SPEC)


if __name__ == "__main__":
    unittest.main()
