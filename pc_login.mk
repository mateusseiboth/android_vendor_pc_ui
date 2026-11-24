# The PC starts on a login screen, as on Googlebook: headless system user mode in which the system
# user (user 0) is the login screen (AOSP hsu_as_login.mk), with PcLogin as its home screen.
# First boot creates the first admin user and runs the setup wizard in it; every later boot ends
# on the login screen, and "Sign out" in the system tray comes back to it.
#
# HSUM changes which packages each user gets, so inherit this first, before other product
# makefiles:
#   $(call inherit-product, vendor/pc/ui/pc_login.mk)

PC_LOGIN_DIR := vendor/pc/ui

$(call inherit-product, $(SRC_TARGET_DIR)/product/hsu_as_login.mk)

# The login screen (packages/apps/PcLogin) and Googlebook's user settings.
PRODUCT_PACKAGES += \
    PcLogin \
    PcLoginFrameworkOverlay

# The setup wizard runs in the people's users only: on user 0 its home screen would win over the
# login screen's.
PRODUCT_COPY_FILES += \
    $(PC_LOGIN_DIR)/sysconfig/preinstalled-packages-pc-login.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/sysconfig/preinstalled-packages-pc-login.xml
