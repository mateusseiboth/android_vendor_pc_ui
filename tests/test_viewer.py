"""PcViewer is the system's image editor (share sheet "Edit") and DocumentsUI's quick viewer, as
Googlebook's Viewer is."""

import unittest

import tree

VIEWER_PACKAGE = "org.lineageos.pcviewer"
VIEWER_EDITOR = "org.lineageos.pcviewer/org.lineageos.pcviewer.MainActivity"


def find_value(target, name):
    for overlay_dir, overlay_target in tree.find_overlays():
        if overlay_target != target:
            continue
        for _, value_name, text, _ in tree.read_overlay_values(overlay_dir):
            if value_name == name:
                return text
    return None


@unittest.skipUnless(tree.has_tree(), "needs the Android source tree (ANDROID_BUILD_TOP)")
class ViewerTest(unittest.TestCase):

    def test_viewer_edits_shared_images(self):
        self.assertEqual(find_value("android", "config_preferredSystemImageEditor"), VIEWER_EDITOR)

    def test_viewer_is_the_file_manager_quick_viewer(self):
        self.assertEqual(find_value("com.android.documentsui", "trusted_quick_viewer_package"), VIEWER_PACKAGE)


if __name__ == "__main__":
    unittest.main()
