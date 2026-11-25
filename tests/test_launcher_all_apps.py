"""Launcher panel of the desktop: Launcher3's desktop grid sizes the taskbar All Apps panel."""

import unittest
import xml.etree.ElementTree as ET

import tree

LAUNCHER = "packages/apps/Launcher3"
DEVICE_PROFILES = f"{LAUNCHER}/res/xml/device_profiles.xml"
QUICKSTEP_DIMENS = f"{LAUNCHER}/quickstep/res/values/dimens.xml"
NS = "{http://schemas.android.com/apk/res-auto}"

# Googlebook's desktop grid: 6 columns of 48dp icons with 12dp gutters. Our cells are compact,
# so a 720dp panel holds 6 apps a row and a few rows above the taskbar.
DESKTOP_ALL_APPS = {
    "allAppsIconSize": "48",
    "allAppsIconTextSize": "14",
    "allAppsCellWidthLandscape": "104",
    "allAppsCellHeightLandscape": "88",
    "allAppsBorderSpaceLandscape": "12",
}

# The panel: at most 720dp wide, 48dp from the screen edges, 8dp above the taskbar, a short slide,
# and a shadow that sets it apart from the windows under it.
PANEL_DIMENS = {
    "taskbar_all_apps_sheet_elevation": "8dp",
    "taskbar_all_apps_sheet_max_width": "720dp",
    "taskbar_all_apps_sheet_screen_margin": "48dp",
    "taskbar_all_apps_sheet_bottom_margin": "8dp",
    "taskbar_all_apps_sheet_inner_padding": "16dp",
    "taskbar_all_apps_sheet_slide_distance": "32dp",
}


def desktop_display_option():
    root = ET.parse(tree.TOP / DEVICE_PROFILES).getroot()
    for grid in root.iter("grid-option"):
        if grid.get(f"{NS}deviceCategory") == "desktop":
            return grid.find("display-option")
    return None


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class DesktopAllAppsGridTest(unittest.TestCase):

    def test_desktop_grid_has_compact_all_apps_cells(self):
        option = desktop_display_option()
        self.assertIsNotNone(option)
        for attribute, expected in DESKTOP_ALL_APPS.items():
            with self.subTest(attribute=attribute):
                self.assertEqual(option.get(f"{NS}{attribute}"), expected)

    def test_panel_dimens(self):
        root = ET.parse(tree.TOP / QUICKSTEP_DIMENS).getroot()
        dimens = {element.get("name"): (element.text or "").strip()
                  for element in root if element.tag == "dimen"}
        for name, expected in PANEL_DIMENS.items():
            with self.subTest(dimen=name):
                self.assertEqual(dimens.get(name), expected)


if __name__ == "__main__":
    unittest.main()
