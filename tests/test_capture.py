"""Desktop screen capture: the large screen capture UI, region recordings and their folder."""

import unittest

import tree
from test_googlebook_spec import read_values

# SystemUI's large screen capture (QS "Screen capture" tile, toolbar for screenshots and
# recordings of the screen, a window or a region). Googlebook gets it from product="desktop";
# setting it in the overlay keeps it on whatever the device's characteristics are.
CAPTURE_SPEC = {
    ("bool", "config_enableLargeScreenScreencapture"): "true",
    # capture branch of frameworks/base: folder of new screen recordings.
    ("string", "config_screenRecordingFolder"): "Movies/Screen recordings",
}

# The large screen capture flags cp2a already enables, plus region recording (capture branch of
# frameworks/base records the selected area).
CAPTURE_FLAGS_FROM_CP2A = [
    "large_screen_screencapture",
    "large_screen_recording",
    "large_screen_sharing",
    "new_screen_record_toolbar",
]


class ScreenCaptureTest(unittest.TestCase):

    def test_overlay_enables_capture_and_names_the_recordings_folder(self):
        values = read_values("PcDesktopSystemUIOverlay")
        for key, expected in CAPTURE_SPEC.items():
            with self.subTest(resource=key):
                self.assertEqual(values.get(key), expected)

    def test_region_recording_flag_is_enabled(self):
        enabled = {(package, name) for _, package, name, state, _ in tree.read_flag_values()
                   if state == "ENABLED"}
        self.assertIn(("com.android.systemui", "large_screen_region_recording"), enabled)

    def test_screen_capture_tile_is_a_default_tile(self):
        tiles = read_values("PcDesktopSystemUIOverlay")[("string", "quick_settings_tiles_default")]
        self.assertIn("screenrecord", tiles.split(","))


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class ReleaseConfigCaptureFlagsTest(unittest.TestCase):

    def test_cp2a_already_enables_the_large_screen_capture_flags(self):
        cp2a = tree.TOP / "build/release/aconfig/cp2a/com.android.systemui"
        for name in CAPTURE_FLAGS_FROM_CP2A:
            with self.subTest(flag=name):
                text = (cp2a / f"{name}_flag_values.textproto").read_text()
                self.assertIn("ENABLED", text)


if __name__ == "__main__":
    unittest.main()
