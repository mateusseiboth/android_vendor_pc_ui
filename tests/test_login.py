"""The PC starts on a login screen: headless system user mode with user 0 as a login screen."""

import re
import unittest
import xml.etree.ElementTree as ET

import tree

LOGIN_MK = tree.REPO / "pc_login.mk"
OVERLAY = tree.REPO / "overlay/PcLoginFrameworkOverlay"
SETUP_WIZARD_SYSCONFIG = tree.REPO / "sysconfig/preinstalled-packages-pc-login.xml"

LOGIN_ACTIVITY = "org.lineageos.pclogin/.LoginActivity"

# Googlebook's user settings (FrameworkDesktopOverlay, lapis) that exist in this tree.
LOGIN_SPEC = {
    ("bool", "config_userSwitchingMustGoThroughLoginScreen"): "true",
    ("bool", "config_allowChangeUserSwitcherEnabled"): "false",
    ("bool", "config_enableUserSwitcherUponUserCreation"): "false",
    ("bool", "config_hideUserSwitchingUiDuringSetup"): "true",
    ("bool", "config_guestUserEphemeral"): "true",
    ("bool", "config_guestUserAllowEphemeralStateChange"): "false",
    ("bool", "config_isMainUserPermanentAdmin"): "false",
    ("bool", "config_animateUserAvatarDuringUserSwitch"): "true",
    ("bool", "config_disableLockscreenByDefault"): "true",
    ("bool", "config_supportsInsecureLockScreen"): "false",
    ("bool", "config_allowAlarmsOnStoppedUsers"): "false",
    ("integer", "config_hsuActivitiesAllowlistMode"): "1",
}

# android.multiuser flags Googlebook ships enabled that the login flow relies on.
LOGIN_FLAGS = [
    "android.multiuser.create_initial_user",
    "android.multiuser.hsu_allowlist_activities",
    "android.multiuser.hsu_device_provisioner",
    "android.multiuser.hsu_disable_notifications",
    "android.multiuser.hsu_app_management",
    "android.multiuser.user_switching_dialog_signout_message",
]


def read_overlay(kind, name):
    for value_kind, value_name, text, _ in tree.read_overlay_values(OVERLAY):
        if (value_kind, value_name) == (kind, name):
            return text
    return None


def read_array(name):
    for xml in OVERLAY.glob("res/values/*.xml"):
        for element in ET.parse(xml).getroot():
            if element.get("name") == name:
                return [(item.text or "").strip() for item in element]
    return []


class LoginProductTest(unittest.TestCase):

    def test_inherits_aosp_hsu_as_login(self):
        self.assertIn("$(SRC_TARGET_DIR)/product/hsu_as_login.mk", LOGIN_MK.read_text())

    def test_installs_the_login_app_and_overlay(self):
        installed = tree.read_product_packages(LOGIN_MK)
        self.assertIn("PcLogin", installed)
        self.assertIn("PcLoginFrameworkOverlay", installed)

    def test_overlay_carries_googlebook_user_settings(self):
        for (kind, name), value in LOGIN_SPEC.items():
            with self.subTest(resource=f"{kind}/{name}"):
                self.assertEqual(read_overlay(kind, name), value)

    def test_login_screen_may_start_on_the_headless_system_user(self):
        allowed = read_array("hsu_allowlist_activities")
        self.assertIn(LOGIN_ACTIVITY, allowed)
        self.assertIn("com.android.settings/.FallbackHome", allowed)

    def test_allowlist_holds_component_names(self):
        for component in read_array("hsu_allowlist_activities"):
            with self.subTest(component=component):
                self.assertRegex(component, r"^[a-z][\w.]+/\.?[\w.$]+$")

    def test_setup_wizard_is_not_installed_for_the_headless_system_user(self):
        root = ET.parse(SETUP_WIZARD_SYSCONFIG).getroot()
        entry = root.find("install-in-user-type[@package='org.lineageos.setupwizard']")
        user_types = {element.get("user-type") for element in entry.findall("install-in")}
        self.assertEqual(user_types, {"FULL", "PROFILE"})

    def test_login_mk_installs_the_sysconfig(self):
        self.assertRegex(LOGIN_MK.read_text(),
                         re.escape("sysconfig/preinstalled-packages-pc-login.xml:")
                         + r"\$\(TARGET_COPY_OUT_PRODUCT\)/etc/sysconfig/")

    def test_login_flags_are_enabled(self):
        enabled = {f"{package}.{name}" for _, package, name, _, _ in tree.read_flag_values()}
        for flag in LOGIN_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, enabled)


if __name__ == "__main__":
    unittest.main()
