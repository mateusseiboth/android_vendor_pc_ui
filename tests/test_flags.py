"""Flag values name declared flags, sit in their package's folder, and are wired into cp2a."""

import re
import unittest

import tree

# Desktop windowing as Googlebook ships it (values read from its system/system_ext aconfig storage).
GOOGLEBOOK_DESKTOP_FLAGS = [
    "com.android.window.flags.show_home_behind_desktop",
    "com.android.window.flags.enable_desktop_taskbar_in_fullscreen_mode",
    "com.android.window.flags.enable_freeform_box_shadows_v2",
    "com.android.window.flags.enable_fullscreen_window_controls",
    "com.android.window.flags.enable_stepped_cascading",
    "com.android.window.flags.enable_overflow_button_for_taskbar_pinned_items",
    "com.android.systemui.status_bar_for_desktop",
    "com.android.systemui.desktop_sizing",
    "com.android.launcher3.enable_taskbar_customization",
    # Handoff: remote tasks of the user's other devices as taskbar suggestions.
    "android.companion.task_continuity",
    # Declared in frameworks/libs/systemui, not in frameworks/base.
    "com.android.systemui.shared.enable_recents_in_taskbar",
    "com.android.systemui.shared.workspace_items_label_hidden",
]


class FlagValuesTest(unittest.TestCase):

    def test_repo_has_flag_values(self):
        self.assertTrue(tree.read_flag_values())

    def test_values_live_in_their_package_folder(self):
        for textproto, package, name, _, _ in tree.read_flag_values():
            with self.subTest(flag=f"{package}.{name}"):
                self.assertEqual(textproto.parent.name, package)

    def test_values_are_read_only_enabled(self):
        for _, package, name, state, permission in tree.read_flag_values():
            with self.subTest(flag=f"{package}.{name}"):
                self.assertEqual((state, permission), ("ENABLED", "READ_ONLY"))

    def test_no_flag_is_set_twice(self):
        names = [f"{package}.{name}" for _, package, name, _, _ in tree.read_flag_values()]
        self.assertEqual(len(names), len(set(names)))

    def test_googlebook_desktop_flags_are_enabled(self):
        enabled = {f"{package}.{name}" for _, package, name, _, _ in tree.read_flag_values()}
        for flag in GOOGLEBOOK_DESKTOP_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, enabled)

    def test_every_package_folder_has_an_aconfig_values_module(self):
        for folder in {textproto.parent for textproto, *_ in tree.read_flag_values()}:
            with self.subTest(package=folder.name):
                text = (folder / "Android.bp").read_text()
                self.assertIn("aconfig_values", text)
                self.assertIn(f'package: "{folder.name}"', text)

    def test_value_set_joins_the_cp2a_release_config(self):
        release = (tree.REPO / "flags/release_configs/cp2a.textproto").read_text()
        value_set = re.search(r'aconfig_value_sets:\s*"([^"]+)"', release).group(1)
        self.assertIn(f'name: "{value_set}"', (tree.REPO / "flags/aconfig/cp2a/Android.bp").read_text())
        self.assertIn("flags/release_config_map.textproto",
                      (tree.REPO / "pc_ui.mk").read_text())


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class FlagDeclarationsTest(unittest.TestCase):

    def test_every_value_names_a_declared_flag(self):
        declared = tree.find_declared_flags()
        for _, package, name, _, _ in tree.read_flag_values():
            with self.subTest(flag=f"{package}.{name}"):
                self.assertIn(f"{package}.{name}", declared)


if __name__ == "__main__":
    unittest.main()
