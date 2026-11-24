"""Every Googlebook flag this tree does not declare is classified in DESIGN.md, with a decision."""

import re
import unittest

import tree

DESIGN = tree.REPO / "DESIGN.md"
CATEGORIES = {"visible-desktop", "visible-other", "multiuser-login", "bugfix", "internal",
              "google-only"}
DECISIONS = ("implemented", "ported earlier", "flag value", "to do", "skip")
# Googlebook enables 239 aconfig flags of the window, WM Shell, SystemUI and Launcher3 packages that
# frameworks/base and Launcher3 do not declare.
UNDECLARED_COUNT = 239

_ROW_RE = re.compile(r"^\| `([\w.]+)` \| ([\w-]+) \| (.+?) \| (.+?) \|$", re.M)


def read_rows():
    text = DESIGN.read_text()
    section = text.split("## Googlebook flags this tree does not declare", 1)[1]
    return _ROW_RE.findall(section)


class UndeclaredFlagsTest(unittest.TestCase):

    def test_every_flag_is_listed_once(self):
        names = [name for name, *_ in read_rows()]
        self.assertEqual(len(names), UNDECLARED_COUNT)
        self.assertEqual(len(set(names)), UNDECLARED_COUNT)

    def test_every_flag_has_a_known_category(self):
        for name, category, _, _ in read_rows():
            with self.subTest(flag=name):
                self.assertIn(category, CATEGORIES)

    def test_every_flag_has_a_decision(self):
        for name, _, _, decision in read_rows():
            with self.subTest(flag=name):
                self.assertTrue(decision.startswith(DECISIONS), decision)

    def test_flag_values_name_flags_with_a_value_file(self):
        enabled = {f"{package}.{name}" for _, package, name, _, _ in tree.read_flag_values()}
        for name, _, _, decision in read_rows():
            if decision.startswith("flag value"):
                with self.subTest(flag=name):
                    self.assertIn(name, enabled)

    def test_nothing_is_left_to_do(self):
        left = [name for name, _, _, decision in read_rows() if decision.startswith("to do")]
        self.assertEqual(left, [])

    def test_no_em_dash(self):
        self.assertNotIn("—", DESIGN.read_text())


if __name__ == "__main__":
    unittest.main()
