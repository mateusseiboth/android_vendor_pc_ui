# Desktop UI design: Googlebook on LineageOS

Goal: the desktop of LineageOS for PCs looks and behaves like Google's Googlebook (lapis,
Android 17, build CL3B.260622.271.R1). Googlebook's binaries are reference only: values (sizes,
colors, radii, timings, layout structure) are reproduced; code and assets are written anew on top
of AOSP/LineageOS.

Reference material (local only, never in git): `gbos-ref/decoded/<App>` (aapt2 resource dumps,
xmltrees, jadx) for SystemUITitan, NexusLauncherRelease and the product overlays; Googlebook's
aconfig storage read from its `system_a` (super partition of the stock image) and from
`system_ext`/`product`.

## How Googlebook builds its desktop

Most of Googlebook's desktop is AOSP code that this tree already has, switched on by:

1. aconfig flags (window, WM Shell, SystemUI, Launcher3);
2. resource overlays (`FrameworkDesktopOverlay`, `SystemUIDesktopOverlay`,
   `NexusLauncherOverlayDesktop`, `LargeScreenConfigOverlay`, `SettingsProviderDesktopOverlay`);
3. a few launcher and Shell code paths that only exist in Google's tree.

We follow the same split: `flags/` and `overlay/` here, code on branch `pc`.

## Elements

### 1. Desktop windowing

| | |
|---|---|
| Googlebook | Freeform windows with 40dp headers on the internal display, desktop by default, home behind the desktop, pinned taskbar. `FrameworkDesktopOverlay`: `config_isDesktopModeSupported`, `config_canInternalDisplayHostDesktops`, `config_enterDesktopByDefaultOnFreeformDisplay`, `config_showHomeBehindDesktop`, `desktop_view_default_header_height` 40dp. Flags `show_home_behind_desktop`, `enable_desktop_taskbar_in_fullscreen_mode`, `enable_desktop_taskbar_on_freeform_displays` and 130+ more |
| Implemented | `overlay/PcDesktopFrameworkOverlay` (those values, plus `desktop_view_default_large_header_height` 40dp: Lineage's `SystemBarUtils` reads the large id). `flags/aconfig/cp2a/*`: the 134 flags of `com.android.window.flags`, `com.android.wm.shell`, `com.android.systemui` and `com.android.launcher3` that Googlebook enables and cp2a leaves disabled. frameworks/base `pc`: "WMShell: Make a PC's internal display desktop-first" |
| Why the Shell change | `DesktopDisplayModeController` makes the internal display desktop-first only with a touchpad plus a physical keyboard, a laptop lid state or an extended display (Googlebook laptops always have a touchpad). A desktop PC with a mouse came up touch-first. `DesktopState.isPcDevice` (`FEATURE_PC`) now makes it desktop-first. The device must declare `android.hardware.type.pc` (it does: `pc_core_hardware.xml`) |
| Remains | 239 Googlebook flags are not declared in this tree (Google-only or newer, e.g. `enable_handle_menu_below_header`, `enable_rect_maximized_windows`, `desktop_scrim_*`, `enable_desktop_first_policy_*`); some are ported by hand below, the list is in the research notes. `config_desktopLaunchInFullscreenPackages` (games list) not copied |

### 2. Taskbar (shelf)

| | |
|---|---|
| Googlebook | Pinned, full width, flush with the bottom, square top corners on the desktop form factor; 56dp tall, 44dp icons, 12dp spacing, centered; running indicator 12x2dp line (tertiary), minimized 6dp (outline), 4dp under the icon; pill All Apps button at the start (68x48dp, 24dp glyph, surface container highest, primary while open); divider; overflow after 10 pinned apps (24 stored). NexusLauncher `taskbar/*`, `customization/*`, `NexusLauncherOverlayDesktop`, `device_profiles.xml` (`desktop` grids), `default_workspace_desktop.xml` |
| Already equal in AOSP | Heights, icon sizes, spacing, background colors, stroke, running/minimized indicators and their animations, hover tooltips, the context menu, overflow (flags) |
| Implemented | `overlay/PcDesktopLauncherOverlay`: `desktop_form_factor` (device type desktop), `reduce_workspace_blur_usage`, `popup_blur_radius` 34dp. Launcher3 `pc`: "Taskbar: Keep square corners on the desktop form factor" (`TaskbarCornerRoundness`), "Taskbar: Googlebook style All Apps on the desktop form factor" (`TaskbarAllAppsPill`, new pill drawables and tints, layout width, 10 hotseat icons, 24 stored, `default_workspace_desktop.xml`) |
| Pinned apps | Googlebook: Gemini, Chrome, Gmail, Calendar, Messages, YouTube, Photos, Files, Play Store. Ours by role (intent categories, so LineageOS's apps resolve): browser, email, calendar, messaging, music, gallery, files, settings |
| Remains | Desktop divider drawable (52dp viewport, 21dp line, outline color); recents section container and divider placement as in Googlebook; `taskbar_button_margin_desktop`; remote apps and handoff (Google services) |

### 3. Status bar, quick settings, notifications

| | |
|---|---|
| Googlebook | Top status bar 36dp: clock and date (`EEEMMMd`) on the left; ongoing chips, notification bell chip and quick settings chip (status icons, battery) on the right; transparent with adaptive tint, opaque over a maximized window. Bell and QS chip open popups (dual shade overlays) at the top end, 376dp wide, 36dp radius, 24dp margin, translucent shade panel colors; tiles 56dp; inline power menu. Heads-up at the top end. SystemUITitan `DesktopStatusBar`, `SystemUIDesktopOverlay`, flags `status_bar_for_desktop`, `scene_container`, `status_bar_popup_chips`, `desktop_sizing`, `opaque_status_bar` |
| Already in AOSP | All of it (`DesktopStatusBar.kt`, dual shade overlays, `desktop_sizing` dimens) behind those flags and configs |
| Implemented | Flags (above). `overlay/PcDesktopSystemUIOverlay`: `config_useDesktopStatusBar`, `config_notificationShadeOnTopEnd`, `config_includeQSAndShadeScenes`=false, tap to expand, infinite grid, inline power menu, end side brightness dialog, default tiles without Google's (`ime` tile does not exist here), desktop falsing and input, lock screen values. Framework overlay: status bar height 36dp, shade panel colors, battery percentage |
| Remains | Calendar popup on the clock (Googlebook only, `enable_desktop_calendar_overlay`); tap on the status bar closing All Apps (`desktop_status_bar_taps_close_all_apps`); 14sp status icon sizes; night light button next to brightness; `overlay_panel_margin_from_middle` |

### 4. App launcher (All Apps)

| | |
|---|---|
| Googlebook | From the taskbar: a floating panel above the taskbar, two thirds of the screen tall at most (1280dp), 8dp above the taskbar, every corner rounded with the dialog radius (28dp), search focused; 6 columns (8 on 2400dp wide), 48dp icons; no blur. On the home screen: launcher All Apps |
| Implemented | Launcher3 `pc`: `DesktopAllAppsSheetGeometry`, `AllAppsSheetCorners`, search focus from the button, desktop sheet layout in `TaskbarAllAppsController`. Overlays: dialog radius 28dp (framework), no blur (launcher) |
| Remains | Responsive `spec_desktop_*` grid specs and the `desktop` grid options (14x7, 15x8 by display size); search bar dimens (48dp field, 33dp header margin); open/close durations 300/250ms; hiding the sheet handle on desktop |

### 5. Window header (caption)

| | |
|---|---|
| Googlebook | 40dp header; app chip (24dp icon, 14sp name, chevron) at the start; minimize, maximize, close at the end as 32dp buttons with 6dp padding (20dp glyphs), 20dp gaps, no ripple inset; header colors from the dynamic scheme (secondary container / surface container low; surface container high / dim in dark); box shadows v2; square corners when maximized; handle menu opens below the header; 8dp resize outset, edge only mouse corners |
| Already equal in AOSP | Colors, shadows and borders (flag `enable_freeform_box_shadows_v2`), double click and drag to top maximize, snap, maximize menu |
| Implemented | Framework overlay: 40dp (`desktop_view_default_large_header_height`). SystemUI overlay: Shell `*_large` button size, padding, ripple insets, chip inset, drag only width, caption margin, resize outset and corner, fullscreen handle height, home peek, to desktop animation. frameworks/base `pc`: "WMShell: Open the app header's handle menu below the header", "WMShell: Square corners for maximized desktop windows" |
| Remains | Rounded 20dp Material Symbols for the header buttons (new vectors in Shell `res/drawable`); 20dp gap between buttons (hard coded 8dp in the layout); "App info" row in the handle menu; header theme from the top opaque background color (needs a framework API); no-resize pointer icons; Googlebook's mouse pointer set |

### 6. Theming

| | |
|---|---|
| Googlebook | Tonal spot from the wallpaper (AOSP default), light by default, Google Sans / Google Sans Text, dialog 28dp, buttons not all caps, circular icon mask, round icons |
| Implemented | Framework overlay: night mode off by default, round icons and circular mask, radii, no all caps. Fonts: LineageOS already ships Google Sans Flex (OFL) through `FontGoogleSansFlexOverlay`, the closest open font |
| Remains | A wallpaper of our own; `google-sans-text`/`-medium` font family aliases to Google Sans Flex in `fonts_customization.xml` (the variable label families fall back to them) |

## Integration

What the device tree and manifests need (not edited by this work):

1. `.repo/local_manifests/pc.xml`: use the `pc` branches and add this repository:

   ```xml
   <remove-project name="LineageOS/android_frameworks_base" />
   <project path="frameworks/base" name="android_frameworks_base" remote="pc" revision="pc" />
   <remove-project name="LineageOS/android_packages_apps_Launcher3" />
   <project path="packages/apps/Launcher3" name="android_packages_apps_Launcher3" remote="pc" revision="pc" />
   <project path="vendor/pc/ui" name="android_vendor_pc_ui" remote="pc" revision="pc" />
   ```

   Locally the branches already exist in the synced projects:
   `git -C frameworks/base checkout pc` and `git -C packages/apps/Launcher3 checkout pc`.
2. `device/pc/pc_x86_64/lineage_pc_x86_64.mk`: `$(call inherit-product, vendor/pc/ui/pc_ui.mk)`.
3. `device/pc/pc_x86_64/device.mk`: `PRODUCT_CHARACTERISTICS := desktop` (instead of `tablet`;
   gives `ro.build.characteristics=desktop` and the framework's `product="desktop"` strings).
4. Nothing else: no release config or lunch change (still `lineage_pc_x86_64-cp2a-userdebug`).

## Verification status

Verified on the host: overlay resource names against the tree, flag names against the tree's
aconfig declarations, the release config (release-config lists the value set last in cp2a).
Not verified without a build: compilation of the Launcher3 and Shell changes and their unit tests
(`WMShellUnitTests`; Launcher3's quickstep tests have no test module in AOSP), RRO compilation,
and the runtime result of the 134 flags together (in particular `scene_container` with
LineageOS's SystemUI changes).
