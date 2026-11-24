# Desktop UI of LineageOS for PCs: Googlebook-like desktop windowing, taskbar, status bar and
# window headers. Inherit from the device's product makefile:
#   $(call inherit-product, vendor/pc/ui/pc_ui.mk)

PC_UI_DIR := vendor/pc/ui

# Runtime resource overlays (overlay/).
PRODUCT_PACKAGES += \
    PcDesktopFrameworkOverlay \
    PcDesktopSettingsProviderOverlay

# aconfig values that Googlebook ships enabled, added to the cp2a release config (flags/).
PRODUCT_RELEASE_CONFIG_MAPS += $(PC_UI_DIR)/flags/release_config_map.textproto

# Window extensions (activity embedding for all apps) and Settings' large screen layout come
# from build/make/target/product/large_screen_common.mk, which vendor/lineage/config/tablet.mk
# already inherits.
