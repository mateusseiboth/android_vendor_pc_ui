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
| Handoff | Googlebook's handoff (taskbar suggestion of the app open on another of the user's devices, from `TaskContinuityManager`) is the same code as AOSP's `taskbar/handoff` (`HandoffSuggestionRepository`, `TaskbarHandoffController`, `HandoffSuggestionLauncher`, badge #1A73E8). Launcher3 `pc` "Taskbar: Name the device of a handoff suggestion" labels it "<app> on <device>" (pt: "<app> em <device>") for the tooltip and accessibility. `flags/.../android.companion/handoff_flag_values.textproto` pins `task_continuity`; Launcher3's `READ_REMOTE_TASKS` and `REQUEST_TASK_HANDOFF` are already in frameworks/base's `com.android.launcher3.xml`. Suggestions only appear with another device associated through the companion device manager and running task continuity |
| Remains | Desktop divider drawable (52dp viewport, 21dp line, outline color); recents section container and divider placement as in Googlebook; `taskbar_button_margin_desktop`; remote apps (Google services) |

### 3. Status bar, quick settings, notifications

| | |
|---|---|
| Googlebook | Top status bar 36dp: clock and date (`EEEMMMd`) on the left; ongoing chips, notification bell chip and quick settings chip (status icons, battery) on the right; transparent with adaptive tint, opaque over a maximized window. Bell and QS chip open popups (dual shade overlays) at the top end, 376dp wide, 36dp radius, 24dp margin, translucent shade panel colors; tiles 56dp; inline power menu. Heads-up at the top end. SystemUITitan `DesktopStatusBar`, `SystemUIDesktopOverlay`, flags `status_bar_for_desktop`, `scene_container`, `status_bar_popup_chips`, `desktop_sizing`, `opaque_status_bar` |
| Already in AOSP | All of it (`DesktopStatusBar.kt`, dual shade overlays, `desktop_sizing` dimens) behind those flags and configs |
| Implemented | Flags (above). `overlay/PcDesktopSystemUIOverlay`: `config_useDesktopStatusBar`, `config_notificationShadeOnTopEnd`, `config_includeQSAndShadeScenes`=false, tap to expand, infinite grid, inline power menu, end side brightness dialog, default tiles without Google's (`ime` tile does not exist here), desktop falsing and input, lock screen values. Framework overlay: status bar height 36dp, shade panel colors, battery percentage |
| Calendar popup | Googlebook: a click on clock and date opens a Material 3 date picker on the panel background (`CalendarPopup`, `QuickActionChipId.Calendar`). Ours, frameworks/base `pc` "SystemUI: Calendar popup on the desktop status bar clock": a quick action panel anchored to the clock with the month (Material 3 `DatePicker`, today marked), the next week's events from `CalendarContract.Instances`, a click on an event opens it, "Open calendar" opens the selected day. Enabled by `config_statusBarClockOpensCalendar` (SystemUI overlay); SystemUI requests `READ_CALENDAR`, granted by `permissions/default-permissions-pc-ui.xml` |
| Remains | Tap on the status bar closing All Apps (`desktop_status_bar_taps_close_all_apps`); 14sp status icon sizes; night light button next to brightness; `overlay_panel_margin_from_middle` |

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
| Header theme | Googlebook keys the header's light or dark scheme off `TaskDescription.getTopOpaqueBackgroundColor()`. Ours, frameworks/base `pc` "Window header theme from the top opaque activity's background": a hidden `TaskDescription.topOpaqueBackgroundColor` that `Task` fills from the topmost activity filling the task (as AOSP does for `topOpaqueSystemBarsAppearance`), used by WM Shell's `DecorThemeUtil` when `config_windowDecorThemeFromTopOpaqueBackground` is set (SystemUI overlay) |
| Remains | Rounded 20dp Material Symbols for the header buttons (new vectors in Shell `res/drawable`); 20dp gap between buttons (hard coded 8dp in the layout); "App info" row in the handle menu; the starting window color as a second fallback of the header theme; no-resize pointer icons; Googlebook's mouse pointer set |

### 6. Theming

| | |
|---|---|
| Googlebook | Tonal spot from the wallpaper (AOSP default), light by default, Google Sans / Google Sans Text, dialog 28dp, buttons not all caps, circular icon mask, round icons |
| Implemented | Framework overlay: night mode off by default, round icons and circular mask, radii, no all caps. Fonts: LineageOS already ships Google Sans Flex (OFL) through `FontGoogleSansFlexOverlay`, the closest open font |
| Remains | A wallpaper of our own; `google-sans-text`/`-medium` font family aliases to Google Sans Flex in `fonts_customization.xml` (the variable label families fall back to them) |

### 7. Login screen (multiple users)

| | |
|---|---|
| Googlebook | Headless system user mode (HSUM) with the system user as a login screen, AOSP's `hsu_as_login.mk`: `system_ext` sets `ro.fw.mu.headless_system_user=true` and `debug.run-as.use_current_user=true` (`hsum_common.mk`); `HsuAsLoginConfigOverlay` sets `config_canSwitchToHeadlessSystemUser=true` and `config_hsumBootStrategy=1` (boot to user 0 once the device is provisioned, to the first full user before); `HsumDefaultConfigOverlay`: `config_enableMultiUserUI`, `config_enableMultipleAdmins`, `config_multiuserMaxRunningUsers` 4. `FrameworkDesktopOverlay`: `config_userSwitchingMustGoThroughLoginScreen`, no user switcher, ephemeral guests, no permanent admin, animated avatar on switch, lock screen disabled by default and no swipe lock, no alarms of stopped users, the HSU activity allowlist (`config_hsuActivitiesAllowlistMode` 1, `hsu_allowlist_activities` starting with `com.google.android.desktop.identity.login/.LoginLauncherActivity`). The login app (`system_ext/priv-app/Login`, `com.google.android.desktop.identity.login`) is user 0's home (HOME filter, priority 4): user pods (190dp pictures, 120dp past a few users) with the name under them, a bottom bar with Accessibility, "Use as guest" and "Add user", progress while switching, blurred wallpaper. A pod switches to the user; the user's lock screen asks for the PIN or password. "Add user" creates "New User" and switches to it; the setup wizard runs there. The system tray signs out through the global action `logout` (`config_globalActionsList`); `android.multiuser` flags `create_initial_user`, `hsu_allowlist_activities`, `hsu_device_provisioner`, `hsu_disable_notifications`, `hsu_app_management`, `user_switching_dialog_signout_message` and the SystemUI `desktop_users_and_accounts` flags (keyguard sign out button, bouncer user pill) are on |
| Already in AOSP 17 | All the framework side: `HsumBootUserInitializer` creates the first admin user (`config_createInitialAdminUserOnHsum`), `UserManagerService.getBootUser` boot strategies, `UserController.logoutUser` (switch to user 0, stop the user), `UserHelper` HSU activity allowlist, SystemUI's `UserLogoutInteractor` ("Sign out" in the QS power menu and on the keyguard status bar), no taskbar on user 0 (`LauncherProxyService` skips the launcher service for the HSU), `hsu_qs_changes` (no QS edit or settings on user 0). Missing: only the login app (`packages/apps/Login` is an empty placeholder in AOSP) |
| Implemented | `pc_login.mk` (inherit first): `hsu_as_login.mk`, `PcLogin` and `overlay/PcLoginFrameworkOverlay` (the Googlebook values above that exist in this tree; allowlist with our login activity, Settings' FallbackHome, Launcher3's second display home and the permission prompt), `sysconfig/preinstalled-packages-pc-login.xml` (LineageOS's setup wizard only in full users and profiles, so its home does not take user 0's place). `flags/aconfig/cp2a/android.multiuser` (the six flags above, plus `dont_show_other_users_apps_to_admin`); the SystemUI flags were already in `googlebook_flag_values`. `packages/apps/PcLogin` (new): the login screen, written anew (pods, bottom bar, guest cleanup, add user rules from `DISALLOW_ADD_USER`/`DISALLOW_ADD_GUEST`, blur), installed for the system user only |
| Not copied | `config_multiuserMaxRunningUsers` 3 (Googlebook's desktop overlay; AOSP's HSUM value 4 kept), `config_multiuserMaximumUsers` 50 (LineageOS's 4 kept), `config_user_types` (Googlebook turns off private space and clone profiles), `config_supportManagedProfileOnNonMainUser`, `config_lockPinEnhancedPrivacyDefault`, `config_enableUserInfoSetupInSuw` (LineageOS's setup wizard has no user info page). `config_showWallpaperDuringUserSwitch` and `config_useSystemUserVisualAppearanceUntilUnlocked` are not in this tree; `config_useSystemWallpaperDuringUserSwitch` is declared but nothing reads it. `android.os.login_add_user_enforcement` is declared but nothing reads it (PcLogin checks admin policies itself) |

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
2. `device/pc/pc_x86_64/lineage_pc_x86_64.mk`: `$(call inherit-product, vendor/pc/ui/pc_ui.mk)`
   (overlays, flag values, and `/product/etc/default-permissions/default-permissions-pc-ui.xml`).
3. `device/pc/pc_x86_64/device.mk`: `PRODUCT_CHARACTERISTICS := desktop` (instead of `tablet`;
   gives `ro.build.characteristics=desktop` and the framework's `product="desktop"` strings).
4. Login screen (optional, branch `login`): `$(call inherit-product, vendor/pc/ui/pc_login.mk)` as the
   first line of `lineage_pc_x86_64.mk`, the local manifest entry
   `<project path="packages/apps/PcLogin" name="android_packages_apps_PcLogin" remote="pc" revision="lineage-24.0" />`
   and the `login` branches of `frameworks/base` (SystemUI) and `packages/apps/SetupWizard`. It is a
   fresh install change: a device set up without HSUM keeps user 0 as a person; wipe data after
   switching.
5. Nothing else: no release config or lunch change (still `lineage_pc_x86_64-cp2a-userdebug`).

## Verification status

Verified on the host: overlay resource names against the tree, flag names against the tree's
aconfig declarations, the release config (release-config lists the value set last in cp2a).
Not verified without a build: compilation of the Launcher3, Shell, SystemUI and framework changes
and their unit tests (`WMShellUnitTests`, `SystemUITests`, `WmTests`, `FrameworksCoreTests`;
Launcher3's quickstep tests have no test module in AOSP), RRO compilation,
and the runtime result of the 134 flags together (in particular `scene_container` with
LineageOS's SystemUI changes).
