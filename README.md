# vendor/pc/ui

Desktop UI of LineageOS for PCs: Googlebook-like desktop windowing, taskbar, status bar, quick
settings, notifications and window headers, on top of LineageOS 24.0 (Android 17).

This repository holds the product level pieces. Code changes live on branch `pc` of
`frameworks/base` (WM Shell) and `packages/apps/Launcher3`. `DESIGN.md` maps every Googlebook
element to what implements it and what is still missing.

## Layout

| Path | What |
|---|---|
| `pc_ui.mk` | Product makefile the device inherits: installs the overlays, adds the flag values, inherits `packages/apps/PcClocks/pc_clocks.mk` (lock screen clocks) when present |
| `overlay/PcDesktopFrameworkOverlay` | `android`: desktop windowing on the internal display, 40dp headers, 36dp status bar, radii, icon mask, shade panel colors, letterbox, laptop power keys |
| `overlay/PcDesktopSystemUIOverlay` | `com.android.systemui`: desktop status bar, shade popups at the top end, quick settings, window header button sizes (WM Shell resources live in SystemUI), screen capture (toolbar, recordings folder), clock plugin allowlist |
| `overlay/PcDesktopLauncherOverlay` | `com.android.launcher3`: desktop form factor, blur, popups |
| `overlay/PcDesktopSettingsProviderOverlay` | `com.android.providers.settings`: desktop defaults |
| `flags/` | aconfig values Googlebook ships enabled, contributed to the `cp2a` release config |
| `permissions/` | Default runtime permissions (SystemUI reads the calendar for the status bar calendar) |
| `tests/` | Host tests (Python) |

## Use

In the device's product makefile:

```make
$(call inherit-product, vendor/pc/ui/pc_ui.mk)
```

and build with the `pc` branch of `packages/apps/Launcher3` and the `capture` branch of
`frameworks/base` (screen capture, on top of `pc`), plus `packages/apps/PcClocks` (see
`DESIGN.md`, "Integration").

## Flag values

`pc_ui.mk` adds `flags/release_config_map.textproto` to `PRODUCT_RELEASE_CONFIG_MAPS`. Its
`release_configs/cp2a.textproto` contributes `aconfig_value_set-pc-ui-cp2a` to the `cp2a` release
config defined by `vendor/lineage/release`; the release config tool appends it after AOSP's and
LineageOS's value sets, so these values win. The folder is not one of the `vendor/*/*/release`
folders the build discovers on its own, so other products in the tree are not affected.

Check the result without building:

```sh
out/release-config -map build/release/release_config_map.textproto \
    -map vendor/lineage/release/release_config_map.textproto \
    -map vendor/pc/ui/flags/release_config_map.textproto \
    -product lineage_pc_x86_64 -release cp2a -variant userdebug -out_dir /tmp/rc -json -quiet
grep -o 'aconfig_value_set-pc-ui-cp2a' /tmp/rc/*.varmk
```

`flags/aconfig/cp2a/com.android.systemui/scene_container_flag_values.textproto` is kept apart:
it switches SystemUI to the scene container, which the desktop status bar and the shade popups
need, and is the first file to drop if LineageOS's SystemUI changes do not work with it.

## Tests

```sh
cd vendor/pc/ui/tests && python3 -m unittest
```

They check that every overlaid resource exists in its target package (also when it is declared
only on the project's `pc` branch, before that branch is checked out), that every flag value
names a flag declared in the tree, that the release config wiring is in place, and that the
overlays carry Googlebook's values. `ANDROID_BUILD_TOP` points at the tree (default: three
folders up).
