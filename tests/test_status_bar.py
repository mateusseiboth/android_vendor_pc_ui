"""Desktop status bar: notifications next to the clock, quick settings at the end."""

import unittest
import xml.etree.ElementTree as ET

import tree
from test_googlebook_spec import read_values

# The notifications chip sits next to the clock with the icons of the notifying apps, and its
# shade opens at the top start under it; the end keeps only the quick settings chip. The overlay
# draws its own empty state ("You're all caught up") as Googlebook's does.
STATUS_BAR_SPEC = {
    ("bool", "config_desktopStatusBarNotificationsAtStart"): "true",
    ("bool", "config_notificationShadeOnTopEnd"): "false",
    ("bool", "config_composeEmptyNotificationShade"): "true",
    # The clock keeps its calendar popup.
    ("bool", "config_statusBarClockOpensCalendar"): "true",
}

SYSTEMUI_CONFIGS = "frameworks/base/packages/SystemUI/res/values/config_pc_sysuia.xml"


class StatusBarOverlayTest(unittest.TestCase):

    def test_overlay_puts_notifications_next_to_the_clock(self):
        values = read_values("PcDesktopSystemUIOverlay")
        for key, expected in STATUS_BAR_SPEC.items():
            with self.subTest(resource=f"{key[0]}/{key[1]}"):
                self.assertEqual(values.get(key), expected)


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class StatusBarConfigsTest(unittest.TestCase):

    def test_systemui_declares_the_configs_off_by_default(self):
        root = ET.parse(tree.TOP / SYSTEMUI_CONFIGS).getroot()
        defaults = {element.get("name"): (element.text or "").strip() for element in root}
        for name in ("config_desktopStatusBarNotificationsAtStart",
                     "config_composeEmptyNotificationShade"):
            with self.subTest(config=name):
                self.assertEqual(defaults.get(name), "false")


if __name__ == "__main__":
    unittest.main()
