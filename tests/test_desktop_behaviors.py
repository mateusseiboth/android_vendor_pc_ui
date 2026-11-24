"""Every config our flags2 branches add for Googlebook's desktop behaviors is turned on here."""

import unittest

import tree


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class DesktopBehaviorConfigsTest(unittest.TestCase):

    def test_branches_add_configs(self):
        self.assertTrue(tree.read_behavior_configs())

    def test_every_config_is_overlaid(self):
        overlaid = {(target, kind, name)
                    for overlay_dir, target in tree.find_overlays()
                    for kind, name, _, _ in tree.read_overlay_values(overlay_dir)}
        for target, kind, name, _ in tree.read_behavior_configs():
            with self.subTest(target=target, resource=f"{kind}/{name}"):
                self.assertIn((target, kind, name), overlaid)

    def test_every_overlaid_bool_differs_from_its_default(self):
        values = {(target, kind, name): value
                  for overlay_dir, target in tree.find_overlays()
                  for kind, name, value, _ in tree.read_overlay_values(overlay_dir)}
        for target, kind, name, default in tree.read_behavior_configs():
            with self.subTest(target=target, resource=f"{kind}/{name}"):
                self.assertNotEqual(values.get((target, kind, name)), default)


if __name__ == "__main__":
    unittest.main()
