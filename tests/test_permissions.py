"""Runtime permissions the desktop UI's system apps get by default are granted and installed."""

import unittest
import xml.etree.ElementTree as ET

import tree

DEFAULT_PERMISSIONS = tree.REPO / "permissions/default-permissions-pc-ui.xml"


class DefaultPermissionsTest(unittest.TestCase):

    def read_grants(self):
        root = ET.parse(DEFAULT_PERMISSIONS).getroot()
        return {(exception.get("package"), permission.get("name"))
                for exception in root.iter("exception")
                for permission in exception.iter("permission")}

    def test_systemui_reads_the_calendar(self):
        self.assertIn(("com.android.systemui", "android.permission.READ_CALENDAR"),
                      self.read_grants())

    def test_pc_ui_mk_installs_the_file_in_product(self):
        text = (tree.REPO / "pc_ui.mk").read_text()
        self.assertIn("permissions/default-permissions-pc-ui.xml:"
                      "$(TARGET_COPY_OUT_PRODUCT)/etc/default-permissions/", text)


if __name__ == "__main__":
    unittest.main()
