"""Overlays only override resources that exist in their target, and every one is installed."""

import unittest

import tree

EM_DASH = "—"


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class OverlaysTest(unittest.TestCase):

    def test_repo_has_overlays(self):
        self.assertTrue(tree.find_overlays())

    def test_every_overlay_targets_a_known_package(self):
        for overlay_dir, target in tree.find_overlays():
            with self.subTest(overlay=overlay_dir.name):
                self.assertIn(target, tree.TARGET_RES_DIRS)

    def test_every_value_exists_in_the_target(self):
        for overlay_dir, target in tree.find_overlays():
            declared = tree.find_declared_resources(target)
            for kind, name, _, _ in tree.read_overlay_values(overlay_dir):
                with self.subTest(overlay=overlay_dir.name, resource=f"{kind}/{name}"):
                    self.assertTrue((kind, name) in declared, "not in the target")

    def test_every_file_resource_exists_in_the_target(self):
        for overlay_dir, target in tree.find_overlays():
            declared = tree.find_declared_resources(target)
            for kind, name in tree.read_overlay_files(overlay_dir):
                with self.subTest(overlay=overlay_dir.name, resource=f"{kind}/{name}"):
                    self.assertTrue((kind, name) in declared, "not in the target")

    def test_every_overlay_is_a_module_installed_by_pc_ui_mk(self):
        installed = tree.read_product_packages()
        for overlay_dir, _ in tree.find_overlays():
            with self.subTest(overlay=overlay_dir.name):
                module = tree.read_overlay_module(overlay_dir)
                self.assertEqual(module, overlay_dir.name)
                self.assertIn(module, installed)

    def test_no_user_text_has_an_em_dash(self):
        for overlay_dir, _ in tree.find_overlays():
            for kind, name, value, _ in tree.read_overlay_values(overlay_dir):
                with self.subTest(overlay=overlay_dir.name, resource=f"{kind}/{name}"):
                    self.assertNotIn(EM_DASH, value)


if __name__ == "__main__":
    unittest.main()
