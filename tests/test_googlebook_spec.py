"""The framework overlay carries Googlebook's desktop values (FrameworkDesktopOverlay, lapis)."""

import unittest

import tree

FRAMEWORK_SPEC = {
    ("bool", "config_isDesktopModeSupported"): "true",
    ("bool", "config_canInternalDisplayHostDesktops"): "true",
    ("bool", "config_enterDesktopByDefaultOnFreeformDisplay"): "true",
    ("bool", "config_showHomeBehindDesktop"): "true",
    ("dimen", "desktop_view_default_header_height"): "40dp",
    # Lineage's SystemBarUtils reads the large header height for app headers.
    ("dimen", "desktop_view_default_large_header_height"): "40dp",
    ("dimen", "status_bar_height_default"): "36dp",
    ("dimen", "status_bar_height_portrait"): "36dp",
    ("dimen", "config_dialogCornerRadius"): "28dp",
    ("integer", "config_navBarInteractionMode"): "2",
    ("bool", "config_buttonTextAllCaps"): "false",
}

# SystemUIDesktopOverlay: desktop status bar, shade popups at the top end, smaller window header.
SYSTEMUI_SPEC = {
    ("bool", "config_useDesktopStatusBar"): "true",
    ("bool", "config_notificationShadeOnTopEnd"): "true",
    ("bool", "config_statusBarTapToExpandShade"): "true",
    ("bool", "config_qsInlinePowerMenu"): "true",
    ("bool", "config_useInfiniteGridLayoutAsDefault"): "true",
    ("bool", "config_includeQSAndShadeScenes"): "false",
    ("dimen", "desktop_mode_header_window_control_button_width_large"): "32dp",
    ("dimen", "desktop_mode_header_window_control_button_height_large"): "32dp",
    ("dimen", "desktop_mode_header_window_control_button_padding_large"): "6dp",
    ("dimen", "freeform_edge_handle_outset"): "8dp",
    # pc branch of frameworks/base: header theme from the topmost opaque activity.
    ("bool", "config_windowDecorThemeFromTopOpaqueBackground"): "true",
}

LAUNCHER_SPEC = {
    ("bool", "desktop_form_factor"): "true",
    ("bool", "reduce_workspace_blur_usage"): "true",
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

    def test_systemui_overlay_matches_googlebook(self):
        self.assert_spec("PcDesktopSystemUIOverlay", SYSTEMUI_SPEC)

    def test_launcher_overlay_matches_googlebook(self):
        self.assert_spec("PcDesktopLauncherOverlay", LAUNCHER_SPEC)

    def test_settings_provider_overlay_matches_googlebook(self):
        self.assert_spec("PcDesktopSettingsProviderOverlay", SETTINGS_PROVIDER_SPEC)


if __name__ == "__main__":
    unittest.main()
