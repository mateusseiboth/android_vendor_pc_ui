"""Lock screen clock styles: packages/apps/PcClocks is installed and SystemUI may load it."""

import re
import unittest
import xml.etree.ElementTree as ET

import tree

CLOCK_PACKAGES = [
    "com.android.systemui.clocks.bignum",
    "com.android.systemui.clocks.calligraphy",
    "com.android.systemui.clocks.growth",
    "com.android.systemui.clocks.inflate",
    "com.android.systemui.clocks.metro",
    "com.android.systemui.clocks.numoverlap",
    "com.android.systemui.clocks.weather",
]

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def read_plugin_allowlist():
    overlay = tree.REPO / "overlay/PcDesktopSystemUIOverlay/res/values/config.xml"
    for element in ET.parse(overlay).getroot():
        if element.get("name") == "config_pluginAllowlist":
            return [item.text for item in element]
    return None


class ClockProductTest(unittest.TestCase):

    def test_product_inherits_the_clock_styles(self):
        self.assertIn("packages/apps/PcClocks/pc_clocks.mk", (tree.REPO / "pc_ui.mk").read_text())

    def test_plugin_allowlist_keeps_systemui_and_adds_every_clock(self):
        self.assertEqual(read_plugin_allowlist(), ["com.android.systemui"] + CLOCK_PACKAGES)


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class ClockTreeTest(unittest.TestCase):

    def test_every_clock_is_known_to_systemui_and_the_picker(self):
        registry = (tree.TOP / "frameworks/base/packages/SystemUI/customization/src/com/android/"
                    "systemui/shared/clocks/ClockRegistry.kt").read_text()
        picker = (tree.TOP / "packages/apps/ThemePicker/src/com/android/customization/picker/"
                  "clock/data/repository/ClockRegistryProvider.kt").read_text()
        for package in CLOCK_PACKAGES:
            with self.subTest(package=package):
                self.assertIn(f'"{package}" to', registry)
                self.assertIn(f'"{package}"', picker)

    @unittest.skipUnless((tree.TOP / "packages/apps/PcClocks").is_dir(),
                         "needs packages/apps/PcClocks")
    def test_pc_clocks_ships_exactly_these_packages(self):
        manifests = sorted((tree.TOP / "packages/apps/PcClocks/apps").glob("*/AndroidManifest.xml"))
        packages = sorted(ET.parse(m).getroot().get("package") for m in manifests)
        self.assertEqual(packages, sorted(CLOCK_PACKAGES))

    @unittest.skipUnless((tree.TOP / "packages/apps/PcClocks").is_dir(),
                         "needs packages/apps/PcClocks")
    def test_pc_clocks_makefile_lists_every_module(self):
        modules = set(re.findall(r'name:\s*"(PcClocks-(?!defaults)\w+)"',
                                 (tree.TOP / "packages/apps/PcClocks/Android.bp").read_text()))
        makefile = (tree.TOP / "packages/apps/PcClocks/pc_clocks.mk").read_text()
        self.assertEqual(len(modules), len(CLOCK_PACKAGES))
        for module in modules:
            with self.subTest(module=module):
                self.assertIn(module, makefile)


if __name__ == "__main__":
    unittest.main()
