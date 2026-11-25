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
| Remains | 239 Googlebook flags are not declared in this tree (Google-only or newer, e.g. `enable_handle_menu_below_header`, `enable_rect_maximized_windows`, `desktop_scrim_*`, `enable_desktop_first_policy_*`); some are ported by hand below; every one is classified, with what was done, in "Googlebook flags this tree does not declare". `config_desktopLaunchInFullscreenPackages` (games list) not copied |

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
| Implemented | Flags (above). `overlay/PcDesktopSystemUIOverlay`: `config_useDesktopStatusBar`, `config_notificationShadeOnTopEnd`, `config_includeQSAndShadeScenes`=false, tap to expand, infinite grid, inline power menu, end side brightness dialog, default tiles without Google's (Nearby Share; `ime` is our own tile, branch `flags2`), desktop falsing and input, lock screen values. Framework overlay: status bar height 36dp, shade panel colors, battery percentage |
| Calendar popup | Googlebook: a click on clock and date opens a Material 3 date picker on the panel background (`CalendarPopup`, `QuickActionChipId.Calendar`). Ours, frameworks/base `pc` "SystemUI: Calendar popup on the desktop status bar clock": a quick action panel anchored to the clock with the month (Material 3 `DatePicker`, today marked), the next week's events from `CalendarContract.Instances`, a click on an event opens it, "Open calendar" opens the selected day. Enabled by `config_statusBarClockOpensCalendar` (SystemUI overlay); SystemUI requests `READ_CALENDAR`, granted by `permissions/default-permissions-pc-ui.xml` |
| Notifications next to the clock | Asked by the user (2026-11-25), not Googlebook's layout (Googlebook keeps a bell at the end): the notifications chip sits right after clock and date, with the status bar icons of the first four notifications and "+N" for the rest, or a bell when there are none; a click opens the notifications popup, which opens at the top start under it (`config_notificationShadeOnTopEnd` false); the end keeps only the quick settings chip. The clock keeps its calendar popup; with the calendar off, a click on the clock opens the notifications too. frameworks/base `pc` "SystemUI: Notifications chip next to the desktop status bar clock" (`config_desktopStatusBarNotificationsAtStart`, `StartNotificationIconsModel`; icons load as the user who got the notification, for HSUM) |
| Empty notifications popup | Googlebook composes the empty state in the popup (`EmptyNotificationShade`: trophy icon over "You're all caught up", or the mode hiding notifications; titleMediumEmphasized, 16/32dp padding). Ours left it to the notification stack's empty view, and the popup opened as an empty rounded panel (cause in the stack not found without a device). frameworks/base `pc` "SystemUI: Empty state of the notifications popup": the overlay draws the empty shade message itself and the stack hides its own (`config_composeEmptyNotificationShade`) |
| Remains | 14sp status icon sizes; night light button next to brightness; `overlay_panel_margin_from_middle` |

### 4. App launcher (All Apps)

| | |
|---|---|
| Googlebook | From the taskbar: a floating panel above the taskbar, two thirds of the screen tall at most (1280dp), 8dp above the taskbar, every corner rounded with the dialog radius (28dp), search focused; 6 columns (8 on 2400dp wide), 48dp icons; no blur. On the home screen: launcher All Apps |
| Implemented | Launcher3 `pc`: `DesktopAllAppsSheetGeometry`, `AllAppsSheetCorners`, search focus from the button, desktop sheet layout in `TaskbarAllAppsController`. Overlays: dialog radius 28dp (framework), no blur (launcher). Launcher3 `flags`: "Taskbar: Uninstall from All Apps on the desktop form factor" (Googlebook's `enable_desktop_all_apps_uninstall`) |
| Desktop launcher panel | Launcher3 `pc` "Taskbar: Desktop launcher panel for the taskbar's All Apps": the panel is at most 720dp wide (48dp from narrow screen edges), centered above the taskbar with an 8dp gap and its bottom corners visible (the bottom sheet's predictive back overdraw is off), with an 8dp shadow, no scrim over the desktop and no drag handle; it fades in while it slides up 32dp. The search field fills the panel with 16dp margins. Compact cells in the desktop grid: 48dp icons, 104x88dp cells, 12dp gutters, 14sp labels, 6 columns. The row above the list shows the predictions, or, with no app prediction service (none in this tree), the apps used last from Recents (`TaskbarAllAppsSuggestions`). "Pin to taskbar"/"Unpin" is in the menu of every app on the desktop form factor (`TaskbarPinFromMenu`), next to App info, Uninstall and, for apps that support it, New window. Keyboard: typing goes to the search field, arrows move between apps, Enter opens the first result or the focused app, Esc clears the search, then closes the panel; the taskbar button and the Meta key toggle it |
| Remains | Responsive `spec_desktop_*` grid specs and the `desktop` grid options (14x7, 15x8 by display size); open/close durations 300/250ms |

### 5. Window header (caption)

| | |
|---|---|
| Googlebook | 40dp header; app chip (24dp icon, 14sp name, chevron) at the start; minimize, maximize, close at the end as 32dp buttons with 6dp padding (20dp glyphs), 20dp gaps, no ripple inset; header colors from the dynamic scheme (secondary container / surface container low; surface container high / dim in dark); box shadows v2; square corners when maximized; handle menu opens below the header; 8dp resize outset, edge only mouse corners |
| Already equal in AOSP | Colors, shadows and borders (flag `enable_freeform_box_shadows_v2`), double click and drag to top maximize, snap, maximize menu |
| Implemented | Framework overlay: 40dp (`desktop_view_default_large_header_height`). SystemUI overlay: Shell `*_large` button size, padding, ripple insets, chip inset, drag only width, caption margin, resize outset and corner, fullscreen handle height, home peek, to desktop animation. frameworks/base `pc`: "WMShell: Open the app header's handle menu below the header", "WMShell: Square corners for maximized desktop windows". frameworks/base `flags`: "WMShell: No minimize button on the fullscreen header", "WMShell: Window header title from the base intent's activity label" |
| Header theme | Googlebook keys the header's light or dark scheme off `TaskDescription.getTopOpaqueBackgroundColor()`. Ours, frameworks/base `pc` "Window header theme from the top opaque activity's background": a hidden `TaskDescription.topOpaqueBackgroundColor` that `Task` fills from the topmost activity filling the task (as AOSP does for `topOpaqueSystemBarsAppearance`), used by WM Shell's `DecorThemeUtil` when `config_windowDecorThemeFromTopOpaqueBackground` is set (SystemUI overlay) |
| Remains | Rounded 20dp Material Symbols for the header buttons (new vectors in Shell `res/drawable`); 20dp gap between buttons (hard coded 8dp in the layout); "App info" row in the handle menu; the starting window color as a second fallback of the header theme; no-resize pointer icons; Googlebook's mouse pointer set |

### 6. Theming

| | |
|---|---|
| Googlebook | Tonal spot from the wallpaper (AOSP default), light by default, Google Sans / Google Sans Text, dialog 28dp, buttons not all caps, circular icon mask, round icons |
| Implemented | Framework overlay: night mode off by default, round icons and circular mask, radii, no all caps. Fonts: LineageOS already ships Google Sans Flex (OFL) through `FontGoogleSansFlexOverlay`, the closest open font |
| Remains | A wallpaper of our own; `google-sans-text`/`-medium` font family aliases to Google Sans Flex in `fonts_customization.xml` (the variable label families fall back to them) |

### 7. Screen capture and recording

| | |
|---|---|
| Googlebook | SystemUI's large screen capture: the Quick Settings "Screen capture" tile opens a toolbar over the screen to take a screenshot or a recording of the whole screen or of one window, with device audio and microphone options; recording chip and stop popup in the status bar, post recording shelf. Flags `large_screen_screencapture`, `large_screen_recording`, `large_screen_sharing`, `new_screen_record_toolbar(_selfie)`; `config_enableLargeScreenScreencapture` from `product="desktop"`. Region recording (`large_screen_region_recording`) is off on Googlebook. `DesktopRecorderPrebuilt` is not a screen recorder: it is Google's Recorder app (`com.google.android.apps.recorder`, audio recording with transcription) |
| Already in AOSP 17 | All of the above (SystemUI `screencapture/`, `screenrecord/`, `statusbar/quickactions/screenrecord`), and cp2a already enables those four flags. Region recording UI too (region box, "Record selected area"), but starting it did nothing: `PreCaptureViewModel.startRecording` mapped `PARTIAL` to a no-op, as no API crops a mirrored display |
| Implemented | frameworks/base `capture`: "SystemUI: Record a region of the screen" (`cropRegion` in `ScreenRecordingParameters`; `ScreenMediaRecorder` draws through `RecordingSurfaces`: straight into the encoder, or `CroppedRecordingSurface`, a GL stage that mirrors the display into a SurfaceTexture and scales the region onto the encoder surface) and "SystemUI: Configurable folder for screen recordings" (`config_screenRecordingFolder`). Here: `large_screen_region_recording` enabled (`flags/.../screen_capture_flag_values.textproto`), `config_enableLargeScreenScreencapture` and `config_screenRecordingFolder` = `Movies/Screen recordings` in the SystemUI overlay. The `screenrecord` default tile is the capture entry |
| Remains | Device check of region recordings (GL stage, encoder sizes of odd regions) |

### 8. Lock screen clock styles

| | |
|---|---|
| Googlebook | Seven clock plugins in `system_ext/priv-app/SystemUIClocks-*` (BigNum, Calligraphy, Growth, Inflate, Metro, NumOverlap, Weather), chosen in the wallpaper and style picker |
| Already in AOSP 17 | The plugin mechanism: `ClockRegistry` knows these seven packages and their clock ids (`KNOWN_PLUGINS`, lazy loading), ThemePicker's `ClockRegistryProvider` allowlists them, `SystemUIClocks-CommonLib` and the sample plugin show how a plugin APK is built |
| Implemented | `packages/apps/PcClocks` (new repo): seven APKs with those packages and ids, faces written anew with system fonts (Roboto Flex, Noto Serif, Google Sans Flex); see its `DESIGN.md`. Here: `pc_ui.mk` inherits `pc_clocks.mk`, and the SystemUI overlay adds the seven packages to `config_pluginAllowlist` (needed on `user` builds) |
| Remains | Tuning each face's sizes on a device |

### 9. Login screen (multiple users)

| | |
|---|---|
| Googlebook | Headless system user mode (HSUM) with the system user as a login screen, AOSP's `hsu_as_login.mk`: `system_ext` sets `ro.fw.mu.headless_system_user=true` and `debug.run-as.use_current_user=true` (`hsum_common.mk`); `HsuAsLoginConfigOverlay` sets `config_canSwitchToHeadlessSystemUser=true` and `config_hsumBootStrategy=1` (boot to user 0 once the device is provisioned, to the first full user before); `HsumDefaultConfigOverlay`: `config_enableMultiUserUI`, `config_enableMultipleAdmins`, `config_multiuserMaxRunningUsers` 4. `FrameworkDesktopOverlay`: `config_userSwitchingMustGoThroughLoginScreen`, no user switcher, ephemeral guests, no permanent admin, animated avatar on switch, lock screen disabled by default and no swipe lock, no alarms of stopped users, the HSU activity allowlist (`config_hsuActivitiesAllowlistMode` 1, `hsu_allowlist_activities` starting with `com.google.android.desktop.identity.login/.LoginLauncherActivity`). The login app (`system_ext/priv-app/Login`, `com.google.android.desktop.identity.login`) is user 0's home (HOME filter, priority 4): user pods (190dp pictures, 120dp past a few users) with the name under them, a bottom bar with Accessibility, "Use as guest" and "Add user", progress while switching, blurred wallpaper. A pod switches to the user; the user's lock screen asks for the PIN or password. "Add user" creates "New User" and switches to it; the setup wizard runs there. The system tray signs out through the global action `logout` (`config_globalActionsList`); `android.multiuser` flags `create_initial_user`, `hsu_allowlist_activities`, `hsu_device_provisioner`, `hsu_disable_notifications`, `hsu_app_management`, `user_switching_dialog_signout_message` and the SystemUI `desktop_users_and_accounts` flags (keyguard sign out button, bouncer user pill) are on |
| Already in AOSP 17 | All the framework side: `HsumBootUserInitializer` creates the first admin user (`config_createInitialAdminUserOnHsum`), `UserManagerService.getBootUser` boot strategies, `UserController.logoutUser` (switch to user 0, stop the user), `UserHelper` HSU activity allowlist, SystemUI's `UserLogoutInteractor` ("Sign out" in the QS power menu and on the keyguard status bar), no taskbar on user 0 (`LauncherProxyService` skips the launcher service for the HSU), `hsu_qs_changes` (no QS edit or settings on user 0). Missing: only the login app (`packages/apps/Login` is an empty placeholder in AOSP) |
| Implemented | `pc_login.mk` (inherit first): `hsu_as_login.mk`, `PcLogin` and `overlay/PcLoginFrameworkOverlay` (the Googlebook values above that exist in this tree; allowlist with our login activity, Settings' FallbackHome, Launcher3's second display home and the permission prompt), `sysconfig/preinstalled-packages-pc-login.xml` (LineageOS's setup wizard only in full users and profiles, so its home does not take user 0's place). `flags/aconfig/cp2a/android.multiuser` (the six flags above, plus `dont_show_other_users_apps_to_admin`); the SystemUI flags were already in `googlebook_flag_values`. `packages/apps/PcLogin` (new): the login screen, written anew (pods, bottom bar, guest cleanup, add user rules from `DISALLOW_ADD_USER`/`DISALLOW_ADD_GUEST`, blur), installed for the system user only |
| Not copied | `config_multiuserMaxRunningUsers` 3 (Googlebook's desktop overlay; AOSP's HSUM value 4 kept), `config_multiuserMaximumUsers` 50 (LineageOS's 4 kept), `config_user_types` (Googlebook turns off private space and clone profiles), `config_supportManagedProfileOnNonMainUser`, `config_lockPinEnhancedPrivacyDefault`, `config_enableUserInfoSetupInSuw` (LineageOS's setup wizard has no user info page). `config_showWallpaperDuringUserSwitch` and `config_useSystemUserVisualAppearanceUntilUnlocked` are not in this tree; `config_useSystemWallpaperDuringUserSwitch` is declared but nothing reads it. `android.os.login_add_user_enforcement` is declared but nothing reads it (PcLogin checks admin policies itself) |

## Googlebook flags this tree does not declare

Googlebook enables 239 aconfig flags of `com.android.window.flags`, `com.android.wm.shell`,
`com.android.systemui` (and `.shared`) and `com.android.launcher3` that `frameworks/base` and
`packages/apps/Launcher3` do not declare (Google-internal or newer than this tree). A value file cannot
turn them on; what they change has to be written in our code. Source: the aconfig storage of
Googlebook's `system` (`system_a` of the stock image) and `system_ext`, compared with the
declarations of this tree. Googlebook ships them read-only, so its compiled code has no trace of the
gates: each flag was classified from its name, the declared sibling flags and the code they gate here,
and Googlebook's resources and code paths (reference only).

Categories: visible-desktop 61, multiuser-login 3, visible-other 44, google-only 7, bugfix 79, internal 45. Decisions: flag value 2, implemented 37, ported earlier 4, skip 196.

- **implemented**: written anew in our code, on the branch named. On branch `flags2` each behavior sits
  behind our own config (default off in AOSP's resources, so the tree without this repository behaves
  as before), turned on by the `config_desktop_behaviors.xml` files of the overlays here.
- **flag value**: declared after all, in `frameworks/libs/systemui`; set in `flags/`.
- **ported earlier**: done on branch `pc` before this list was made.
- **skip**: with the reason (a fix for code this tree does not have, phone or lock screen only, Google services, internal).

| Flag | Category | Effect | Decision |
|---|---|---|---|
| `com.android.launcher3.enable_collapse_sysui_panels_for_quick_actions` | visible-desktop | Clicking the taskbar also closes open status bar quick action popups (calendar, notifications, quick settings chips), not only the shade. | implemented: frameworks/base `flags2`, "SystemUI: Collapsing panels also closes status bar quick action popups"; Launcher3 `flags2`, "Taskbar: A click also closes status bar quick action popups"; `config_collapsePanelsClosesQuickActions`, `config_taskbarClickClosesQuickActions`; sysui state bit 41 `SYSUI_STATE_QUICK_ACTIONS_SHOWING` |
| `com.android.launcher3.enable_desktop_all_apps_uninstall` | visible-desktop | Long-press/right-click on an app in the taskbar All Apps panel shows "Uninstall" on the desktop form factor. | implemented: Launcher3 `flags`, "Taskbar: Uninstall from All Apps on the desktop form factor" |
| `com.android.launcher3.enable_focus_rings` | visible-desktop | Keyboard focus rings on Compose-based launcher surfaces (BorderOnFocus modifier). | skip: our view-based launcher already draws focus outlines (enable_focus_outline is on); the Compose surfaces it targets (new popups, widget picker) are not in our Launcher3 |
| `com.android.launcher3.enable_home_as_default_desk_for_recents` | visible-desktop | unknown: Overview treats Home as the default desk; exact UI change not determinable from name and siblings. | skip: effect unknown and Overview is secondary on a mouse-driven PC |
| `com.android.launcher3.enable_papercut_hit_context_menu_changes` | visible-desktop | unknown: small fixes to launcher context menus ("papercuts"); which items change is not determinable. | skip: changes unknown |
| `com.android.launcher3.enable_recents_transition_tuning` | visible-desktop | unknown: retuned recents (Overview) transition animation parameters; values are inlined. | skip: parameter values unknown |
| `com.android.launcher3.enable_workspace_animation_for_overview_transition_from_desk` | visible-desktop | Home workspace animates in when going from a desk to Overview. | skip: Overview animation polish; Googlebook recents code differs from ours |
| `com.android.launcher3.update_trackpad_gesture_overview_transition` | visible-desktop | unknown: changes the touchpad swipe-up-to-Overview transition; details inlined. | skip: behavior unknown |
| `com.android.systemui.desktop_av_controls_icons` | visible-desktop | Status bar camera/microphone (AV controls) chip shows dedicated camera and mic icons. | implemented: already in this tree; AOSP `av_controls_chip_camera` and `av_controls_chip_mic` drawables are used by `AvControlsChipViewModel`, with Googlebook's chip colors (the earlier note was wrong) |
| `com.android.systemui.desktop_status_bar_taps_close_all_apps` | visible-desktop | A tap on an empty part of the desktop status bar closes the taskbar All Apps panel and other launcher floating views on that display. | implemented: frameworks/base `flags2`, "SystemUI: A tap on the desktop status bar closes launcher panels"; Launcher3 `flags2`, "Taskbar: Close All Apps and floating views on request from SystemUI"; `config_statusBarTapClosesLauncherPanels`; `ILauncherProxy.closeFloatingViews` = 41 |
| `com.android.systemui.enable_desktop_calendar_overlay` | visible-desktop | Click on the status bar clock opens a calendar popup. | ported earlier: branch pc (sections 1 and 5) |
| `com.android.systemui.enable_desktop_heads_up_appearance_controller` | visible-desktop | Heads-up notifications on the desktop status bar get fully rounded corners and always show their header row while pinned or animating away. | implemented: frameworks/base `flags2`, "SystemUI: Rounded heads-up notifications on the desktop status bar"; `config_desktopHeadsUpAppearance` |
| `com.android.systemui.enable_material_focus_rings` | visible-desktop | Material 3 keyboard focus rings on SystemUI surfaces (notifications, QS, dialogs). | implemented: frameworks/base `flags2`, "SystemUI: Material 3 focus rings on notifications, dialogs and QS"; `config_materialFocusRings` |
| `com.android.systemui.notification_accessible_dismiss_button` | visible-desktop | The hover X dismiss button on notifications is also reachable by keyboard focus and accessibility. | implemented: frameworks/base `flags2`, "SystemUI: Keyboard and accessibility reach for the notification X"; `config_notificationDismissButtonAccessible` |
| `com.android.systemui.qs_ime_tile` | visible-desktop | Quick settings tile to switch the input method/keyboard layout. | implemented: frameworks/base `flags2`, "SystemUI: Input method quick settings tile"; tile spec `ime` (in the default tiles), `config_quickSettingsExtraStockTiles` |
| `com.android.systemui.qs_immediate_mouse_drag` | visible-desktop | In QS edit mode a mouse drag moves a tile immediately, without a long press. | implemented: frameworks/base `flags2`, "SystemUI: Mouse drag moves quick settings tiles without a long press"; `config_qsEditModeImmediateMouseDrag` |
| `com.android.systemui.qs_toolbar_tweaks` | visible-desktop | unknown: tweaks to the QS toolbar (buttons row); details not determinable. | skip: changes unknown |
| `com.android.systemui.scroll_shade_on_bottom_notif_expand` | visible-desktop | Expanding a notification at the bottom of the notification list scrolls it into view. | implemented: frameworks/base `flags2`, "SystemUI: Scroll the shade to a notification expanded at its bottom"; `config_scrollShadeOnBottomNotificationExpand` |
| `com.android.systemui.share_screen_privacy_indicator` | visible-desktop | Status bar chip while the screen is shared, with a "Stop sharing" popup. | skip: already present in our tree (status_bar_popup_chips path) |
| `com.android.systemui.shared.enable_recents_in_taskbar` | visible-desktop | Taskbar shows strictly recent apps instead of hybrid hotseat predictions. | flag value: declared in frameworks/libs/systemui; `flags/aconfig/cp2a/com.android.systemui.shared` |
| `com.android.systemui.shared.enable_surface_shadow` | visible-desktop | unknown: surface-level shadow for some SystemUI/launcher surface. | skip: target surface unknown |
| `com.android.systemui.shared.selective_dialog_taskbar_stash` | visible-desktop | Taskbar stashes only for SystemUI dialogs that ask for it, instead of for every SystemUI dialog. | implemented: frameworks/base `flags2`, "SystemUI: Tell the taskbar which dialogs ask it to stash"; Launcher3 `flags2`, "Taskbar: Stash only for SystemUI dialogs that ask for it"; `config_taskbarStashesOnlyForDialogsThatAsk`; sysui state bit 39 `SYSUI_STATE_DIALOG_STASH_TASKBAR`, `DialogDelegate.shouldStashTaskbar` |
| `com.android.systemui.shared.workspace_items_label_hidden` | visible-desktop | Option to hide app icon labels on the home screen. | flag value: declared in frameworks/libs/systemui; `flags/aconfig/cp2a/com.android.systemui.shared` |
| `com.android.systemui.shortcut_helper_dialog` | visible-desktop | Keyboard shortcut helper opens as a centered dialog with a sidebar instead of a bottom sheet. | implemented: frameworks/base `flags2`, "SystemUI: Keyboard shortcut helper as a dialog with a sidebar"; `config_shortcutHelperAsDialog` |
| `com.android.systemui.updated_media_chip` | visible-desktop | Redesigned status bar media chip (icon plus title text with fading edge, min/max width). | implemented: frameworks/base `flags2`, "SystemUI: Media chip with the title on the desktop status bar"; `config_statusBarMediaChipShowsTitle` |
| `com.android.systemui.volume_dialog_horizontal_no_buttons` | visible-desktop | Horizontal volume dialog without the ringer/settings buttons (wider slider). | implemented: frameworks/base `flags2`, "SystemUI: Horizontal volume dialog without ringer and settings buttons"; `config_volumeDialogHorizontalWithoutButtons` |
| `com.android.window.flags.backnav_minimize_on_close` | visible-desktop | Back that would close a desktop window's last activity minimizes the window instead (inferred from name). | implemented: frameworks/base `flags2`, "WMShell: Desktop window closed by back stays minimized"; `config_minimizeDesktopWindowOnBackClose` |
| `com.android.window.flags.disable_desktop_windowing_full_immersive` | visible-desktop | Desktop windows of immersive apps no longer enter the "full immersive" state (window covering the display with header hidden) on maximize. | implemented: frameworks/base `flags2`, "WMShell: No full immersive state for desktop windows"; `config_disableDesktopFullImmersive` |
| `com.android.window.flags.disable_home_animation_when_sliding_to_desk` | visible-desktop | No home animation during the fullscreen-to-desk slide. | skip: part of the slide-to-desk transition our tree lacks |
| `com.android.window.flags.enable_alt_tab_desk_switch_animations_in_shell` | visible-desktop | Alt+Tab to a window on another desk animates the desk switch in Shell. | skip: animation only, matters only with several desks |
| `com.android.window.flags.enable_custom_header_in_fullscreen` | visible-desktop | Apps that draw their own caption (transparent caption bar appearance, e.g. browser tab strips) keep their custom header in fullscreen on desktop-first displays. | implemented: frameworks/base `flags2`, "WMShell: Keep an app's custom header in fullscreen"; `config_keepCustomHeaderInFullscreen` |
| `com.android.window.flags.enable_desktop_alttab_lastfocusedtime` | visible-desktop | Alt+Tab orders desktop windows by last focus time. | implemented: frameworks/base `flags2`, "WMShell: Alt+Tab orders desktop windows by last focus"; `config_desktopAltTabOrdersByLastFocus` |
| `com.android.window.flags.enable_desktop_task_snapshot_on_focus_loss` | visible-desktop | A desktop window is snapshotted when it loses focus, so Alt+Tab/Overview thumbnails are current. | implemented: frameworks/base `flags2`, "WMShell: Snapshot of a desktop window when it loses focus"; `config_desktopSnapshotOnFocusLoss` |
| `com.android.window.flags.enable_desktop_taskbar_autohide_on_homescreen` | visible-desktop | unknown: desktop taskbar auto-hide extended to the home screen; exact condition not determinable. | skip: effect unknown; our taskbar is pinned on the home screen as in Googlebook screenshots (DESIGN.md section 2) |
| `com.android.window.flags.enable_disconnect_resize` | visible-desktop | Windows moved off an unplugged display are resized to fit the remaining one. | skip: external display hot-unplug only |
| `com.android.window.flags.enable_dynamic_window_decor_task_description` | visible-desktop | Window header app name/icon update live when the app changes its TaskDescription. | implemented: frameworks/base `flags2`, "WMShell: Window header follows the app's task description"; `config_windowHeaderFollowsTaskDescription` (optional allowlist `config_windowHeaderTaskDescriptionPackages`, empty: every app) |
| `com.android.window.flags.enable_exclude_tiled_tasks_from_remembered_bounds` | visible-desktop | Snapped (half-screen) bounds are not saved as remembered launch bounds, so a relaunch opens the app at its free size. | implemented: frameworks/base `flags2`, "WMShell: Snapped window bounds not remembered for relaunch"; `config_excludeTiledBoundsFromRememberedBounds` |
| `com.android.window.flags.enable_fresh_start_on_reboot` | visible-desktop | After a reboot the desktop starts empty instead of restoring the previous session's desktop tasks (inferred from name). | skip: inferred only; confirm the restore behavior on our build first |
| `com.android.window.flags.enable_fullscreen_header_animation` | visible-desktop | Fullscreen header slides down/up (250 ms, FAST_OUT_SLOW_IN, translationY) when shown/hidden instead of popping. | implemented: frameworks/base `flags2`, "WMShell: Slide the fullscreen header in and out"; `config_animateFullscreenHeader` |
| `com.android.window.flags.enable_fullscreen_to_desk_slide_on_launch` | visible-desktop | Launching a desktop app from a fullscreen app slides the desk in. | skip: animation only, needs a new Shell transition handler |
| `com.android.window.flags.enable_handle_menu_below_header` | visible-desktop | Handle menu opens below the header. | ported earlier: branch pc (sections 1 and 5) |
| `com.android.window.flags.enable_hide_minimize_button_in_fullscreen` | visible-desktop | Fullscreen header has no minimize button (app chip, exit fullscreen, close only). | implemented: frameworks/base `flags`, "WMShell: No minimize button on the fullscreen header" |
| `com.android.window.flags.enable_home_focus_while_peeking` | visible-desktop | While the home screen is peeked (desktop windows moved aside), Home takes input focus so keyboard input reaches the launcher. | implemented: frameworks/base `flags2`, "WMShell: Home takes keyboard focus while peeked"; `config_focusHomeWhilePeeking` |
| `com.android.window.flags.enable_keyboard_shortcut_move_focused_window_to_desk` | visible-desktop | Keyboard shortcut moves the focused window to the previous/next desk (probable reading; Googlebook handles MOVE_FOCUSED_TASK_TO_PREVIOUS_DESK / _NEXT_DESK). | implemented: frameworks/base `flags2`, "WMShell: Keyboard shortcuts move the focused window to another desk"; `config_keyboardShortcutMovesFocusedWindowToDesk` (framework); key gestures 91/92, Meta+Shift+[ and Meta+Shift+] |
| `com.android.window.flags.enable_multi_instance_picker_refresh` | visible-desktop | unknown: refreshed multi-instance (manage windows) picker; details not determinable. | skip: changes unknown |
| `com.android.window.flags.enable_position_aware_status_bar_hover` | visible-desktop | SystemUI reports pointer position over the desktop status bar to Shell, so the fullscreen header reveal reacts to where the pointer hovers (exact rule unknown). | implemented: frameworks/base `flags2`, "WMShell: Status bar hover reveals the header of the task under it"; `config_fullscreenHeaderFollowsStatusBarHover`; rule in `StatusBarHoverHeaderReveal` |
| `com.android.window.flags.enable_preserve_desktop_z_order_on_exit` | visible-desktop | Leaving and re-entering the desktop keeps the windows' stacking order. | implemented: frameworks/base `flags2`, "WMShell: Desktop windows keep their stacking across exit"; `config_preserveDesktopZOrderOnExit` |
| `com.android.window.flags.enable_rect_maximized_windows` | visible-desktop | Square corners for maximized windows. | ported earlier: branch pc (sections 1 and 5) |
| `com.android.window.flags.enable_shell_slide_in_for_running_task_from_taskbar` | visible-desktop | Picking a running fullscreen app in the taskbar while on the desk slides it in. | skip: animation only, new Shell transition handler |
| `com.android.window.flags.enable_shrink_window_to_display_size_on_drag` | visible-desktop | A window dragged onto a smaller display shrinks to fit it. | skip: cross-display drag only |
| `com.android.window.flags.enable_splitscreen_fullscreen_header` | visible-desktop | Split-screen apps on desktop-first displays get the fullscreen header (app chip, exit, close). | implemented: frameworks/base `flags2`, "WMShell: Fullscreen header for split-screen apps"; `config_showFullscreenHeaderInSplitScreen` |
| `com.android.window.flags.enable_swipe_down_to_show_fullscreen_header` | visible-desktop | Swipe down from the top edge reveals the fullscreen header (touch). | skip: touch gesture; mouse reveal already works |
| `com.android.window.flags.enable_taskbar_desk_to_fullscreen_switch` | visible-desktop | Switching from the desk to a fullscreen app via the taskbar uses a dedicated desk-to-fullscreen transition. | skip: animation only, Launcher + Shell transition we lack |
| `com.android.window.flags.keep_empty_desk_active_in_desktop_first_showing_home` | visible-desktop | On a desktop-first display, closing the last window keeps the empty desk active while Home shows, so the next app opens as a window. | implemented: frameworks/base `flags2`, "WMShell: Empty desk stays active on a desktop-first display"; `config_keepEmptyDeskActiveShowingHome` |
| `com.android.window.flags.new_app_window_animations_full_opacity` | visible-desktop | unknown: new app window open animation keeps full opacity (no fade); which animation is not determinable. | skip: target animation unknown |
| `com.android.window.flags.reduce_header_and_taskbar_reveal_delay` | visible-desktop | Pointer at the top/bottom edge in fullscreen reveals header/status bar and taskbar sooner (Googlebook value unknown). | implemented: frameworks/base `flags2`, "Framework: Configurable mouse delay to reveal header and taskbar"; `config_mouseEdgeRevealDelayMs` (framework, 500; 200 here) |
| `com.android.window.flags.remove_move_to_display_animation` | visible-desktop | Moving a window to another display happens without animation. | skip: multi-display only |
| `com.android.window.flags.restore_tiling_on_unminimize` | visible-desktop | Restoring a minimized window that was snapped puts it back into its tiled half. | implemented: frameworks/base `flags2`, "WMShell: Restored window tiles back into its snapped half"; `config_restoreTilingOnUnminimize` |
| `com.android.window.flags.show_pointer_in_app_recording` | visible-desktop | Mouse pointer included when recording a single app. | skip: spans input/SurfaceFlinger capture, Googlebook code not in reference |
| `com.android.window.flags.use_base_intent_label_for_app_header_title` | visible-desktop | Window header app name comes from the task's base intent label. | implemented: frameworks/base `flags`, "WMShell: Window header title from the base intent's activity label" |
| `com.android.window.flags.use_top_opaque_background_color_for_caption` | visible-desktop | Header theme from the top opaque activity background. | ported earlier: branch pc (sections 1 and 5) |
| `com.android.systemui.hide_sign_out_button_when_user_setup_is_not_complete` | multiuser-login | Keyguard status bar sign-out button hidden while the user has not finished setup. | implemented: frameworks/base `login`, "SystemUI: Switch user to the login screen, and no sign out during setup" |
| `com.android.systemui.hsu_qs_disable_settings_icon_on_detail_panels` | multiuser-login | Headless system user: no settings icon on QS detail panels. | implemented: frameworks/base `login`, "SystemUI: No settings button on QS details over the login screen" |
| `com.android.systemui.shade_displays_mirror_display_multi_user` | multiuser-login | Shade on mirrored displays for multiple users. | skip: multi-user |
| `com.android.launcher3.hide_back_button_settings` | visible-other | Launcher's Home settings shows the up/back arrow only when the screen is not the task root. | implemented: Launcher3 `flags2`, "Launcher3: No up arrow on a Home settings screen that is its task root"; `config_settingsHidesUpArrowOnTaskRoot` |
| `com.android.launcher3.reject_overview_to_home_gesture` | visible-other | unknown: rejects the Overview-to-Home swipe in some state (condition not determinable). | skip: gesture navigation detail, condition unknown |
| `com.android.systemui.accessibility_key_launch_suw_assistive_options_in_oobe` | visible-other | Accessibility key during setup wizard opens the assistive options screen. | skip: setup wizard (OOBE) only |
| `com.android.systemui.allow_user_activity_on_keyguard` | visible-other | Input on the lock screen counts as user activity (screen-off timer reset). | skip: lock screen |
| `com.android.systemui.animation_library_override_dialog_background_opacity` | visible-other | Dialog launch animation can override the dialog background opacity. | skip: animation library detail |
| `com.android.systemui.block_automatic_keyguard_autofocus` | visible-other | Lock screen stops auto-focusing an input on show. | skip: lock screen |
| `com.android.systemui.compose_focus_rings_on_lock_screen` | visible-other | Keyboard focus rings on the Compose lock screen. | skip: lock screen |
| `com.android.systemui.disable_dream_suppression_v2` | visible-other | Disables dream suppression (v2). | skip: dreams |
| `com.android.systemui.enable_short_content_overscroll_unconditionally` | visible-other | Notification list overscrolls even when its content is shorter than the panel. | skip: scroll feel detail |
| `com.android.systemui.enabled_notes_lockscreen_consent_flow` | visible-other | Consent flow for the notes app on the lock screen. | skip: notes/lock screen |
| `com.android.systemui.face_unlock_retry_button_on_bouncer` | visible-other | Retry face unlock button on the bouncer. | skip: biometrics on bouncer |
| `com.android.systemui.floating_menu_layout_update` | visible-other | Accessibility floating menu layout update. | skip: accessibility floating menu |
| `com.android.systemui.focus_anything_on_bouncer_2` | visible-other | Keyboard focus can reach every bouncer element. | skip: bouncer (lock screen) |
| `com.android.systemui.hide_navigation_bars_on_lockscreen_if_bouncer_has_back_button` | visible-other | Hides navigation bars on the lock screen when the bouncer has its own back button. | skip: lock screen |
| `com.android.systemui.keyguard_surface_behind_animation_enabled_config` | visible-other | Config to enable the unlock surface-behind animation. | skip: unlock animation |
| `com.android.systemui.launch_default_notes_app_in_activity` | visible-other | Notes shortcut launches the notes app as an activity. | skip: notes |
| `com.android.systemui.media_compose_compressed_default_transition` | visible-other | Compose media controls compressed default transition. | skip: media |
| `com.android.systemui.media_compose_surface_effects` | visible-other | Surface effects on Compose media controls. | skip: media |
| `com.android.systemui.nesteddraggable_touchpad_pan_drags` | visible-other | Touchpad two-finger pan can drag NestedDraggable elements (e.g. shade). | skip: desktop shade opens as click popups, drag gesture not used |
| `com.android.systemui.privacy_indicator_oobe_hide` | visible-other | Hides privacy indicators during setup. | skip: OOBE |
| `com.android.systemui.screenshot_exclude_layers` | visible-other | unknown: screenshots leave out some layers; which layers is not determinable. | skip: effect unknown |
| `com.android.systemui.shared.brightness_system_ui_dialog` | visible-other | Brightness requests open SystemUI's brightness dialog. | skip: Settings entry point, desktop already has the brightness slider in QS |
| `com.android.systemui.shared.enable_lockscreen_shortcut_enablement_dialog_customization` | visible-other | Customizable dialog when enabling a lock screen shortcut. | skip: lock screen |
| `com.android.systemui.shared.notification_sound_enabled_preference` | visible-other | Preference to turn notification sounds on or off. | skip: Settings preference, not desktop shell |
| `com.android.systemui.show_language_code_on_bouncer` | visible-other | Bouncer shows the active keyboard language code. | skip: lock screen |
| `com.android.systemui.sync_note_lockscreen_shortcut_with_app_selection` | visible-other | Lock screen notes shortcut follows the notes app selection. | skip: notes/lock screen |
| `com.android.systemui.wallpaper_zoom_enabled_config` | visible-other | Config to turn the wallpaper zoom (on shade open) on or off. | skip: config plumbing; desktop popups do not zoom the wallpaper |
| `com.android.window.flags.camera_compat_enable_simulate_requested_orientation_override` | visible-other | Per-app override for camera compat simulated orientation. | skip: camera app compat |
| `com.android.window.flags.camera_compat_landscape_opt_in` | visible-other | Apps opt in to landscape camera compat. | skip: camera app compat |
| `com.android.window.flags.camera_compat_single_front_camera_treatment` | visible-other | Camera compat treatment for devices with one front camera. | skip: camera app compat |
| `com.android.window.flags.disable_taskbar_icon_menu_in_split_select` | visible-other | No taskbar icon menu while choosing the second split app. | skip: split screen |
| `com.android.window.flags.display_compat_mode_per_app_override` | visible-other | Per-app override of display compat mode. | skip: app compat |
| `com.android.window.flags.enable_external_display_connection_while_locked` | visible-other | Handles connecting an external display while locked. | skip: lock screen + external display |
| `com.android.window.flags.enable_recents_during_bubbles_mixed_transition` | visible-other | Recents gesture during a bubble transition. | skip: bubbles |
| `com.android.window.flags.extended_seamless_rotation` | visible-other | Seamless rotation for more cases. | skip: rotation, PC has no sensors |
| `com.android.window.flags.force_laptop_mode_landscape_rotation` | visible-other | Forces landscape in laptop posture. | skip: convertible posture, PC has no sensors |
| `com.android.window.flags.hide_3button_nav_on_external_display` | visible-other | No 3-button navigation on external displays. | skip: 3-button nav not used on our desktop |
| `com.android.window.flags.keyguard_default_display_on_top` | visible-other | Keyguard on top of the default display. | skip: lock screen |
| `com.android.window.flags.transparent_policy_reachability_position` | visible-other | Letterbox reachability position for transparent activities. | skip: letterbox app compat |
| `com.android.wm.shell.enable_bubble_swipe_down_to_collapse` | visible-other | Swipe down collapses an expanded bubble. | skip: bubbles |
| `com.android.wm.shell.enable_drag_out_of_bubble` | visible-other | Drag an app out of a bubble. | skip: bubbles |
| `com.android.wm.shell.no_bubble_scrim` | visible-other | No scrim behind expanded bubbles. | skip: bubbles |
| `com.android.wm.shell.set_max_height_for_bubbles_on_large_screens` | visible-other | Max height for bubbles on large screens. | skip: bubbles |
| `com.android.wm.shell.split_tighter_inner_corner_radius` | visible-other | Tighter inner corner radius in split screen. | skip: split screen visuals |
| `com.android.launcher3.enable_desktop_default_widget` | google-only | Default desktop home screen layout places a widget at the top left. | skip: the widget is Google's desktop tips app, not in our tree (an own default widget can be added to default_workspace_desktop.xml without the flag) |
| `com.android.launcher3.enable_options_popup_menu_ui_v2` | google-only | New home-screen options menu (right-click on wallpaper) with wallpaper carousel and widget suggestions. | skip: the dialog is NexusLauncher (Google) code, not AOSP Launcher3; reproducing it is a new feature |
| `com.android.launcher3.enable_taskbar_remote_apps` | google-only | Taskbar section with apps streamed from another device (remote apps). | skip: needs Google's app streaming service |
| `com.android.launcher3.show_task_description_icon_in_taskbar` | google-only | Taskbar shows a running task's TaskDescription icon/label instead of the app icon, for allowlisted packages. | skip: only applied to Google's app streaming package |
| `com.android.systemui.shared.cue_bar_ace_migration` | google-only | Cue bar (ambient AI suggestions) data from the new provider, rendered in the taskbar. | skip: Google's ambient cue service |
| `com.android.systemui.shared.enable_lpp_assist_invocation_initial_rumble` | google-only | Haptic rumble when long-pressing power to invoke the assistant. | skip: assistant (Gemini) invocation |
| `com.android.systemui.shared.extended_wallpaper_effects` | google-only | Extended wallpaper effects. | skip: needs Google's wallpaper effects service |
| `com.android.launcher3.block_trackpad_interruption_to_overview` | bugfix | Ignores a touchpad gesture that interrupts an ongoing transition to Overview (name). | skip: gesture-race fix inside Googlebook's newer Overview gesture code, no new behavior; revisit if touchpad swipes glitch Overview |
| `com.android.launcher3.dismiss_widget_picker_as_system_dialog` | bugfix | Widget picker closes on the close-system-dialogs broadcast like other system dialogs (name). | skip: home-screen widget picker edge case, no new feature |
| `com.android.launcher3.enable_autohidden_desktop_taskbar_insets_fix` | bugfix | Fixes the insets an auto-hidden desktop taskbar reports to apps (gap or overlap under maximized windows). | skip: only matters when the taskbar auto-hides; ours is pinned (DESIGN.md section 2); revisit if auto-hide is offered |
| `com.android.launcher3.enable_keyboard_quick_switch_thumbnail_loading_fix` | bugfix | Fixes thumbnail loading in the Alt+Tab keyboard quick switch view. | skip: fix inside Googlebook code we cannot see; revisit if Alt+Tab thumbnails are blank or stale |
| `com.android.launcher3.enable_previously_appeared_task_view_check` | bugfix | Checks whether a task view already appeared before reusing it in Overview. | skip: Overview internal fix |
| `com.android.launcher3.enable_recents_window_livetile_fix` | bugfix | Fixes the live tile when recents runs in its own window. | skip: Overview-in-window internals |
| `com.android.launcher3.finish_synthetic_transition_in_overview` | bugfix | Finishes a synthetic (fake) transition when it ends in Overview. | skip: Overview internal fix |
| `com.android.launcher3.fix_notification_shade_integration` | bugfix | Fixes how the taskbar reacts to the notification shade. | skip: fix details unknown; desktop shade is a popup overlay here |
| `com.android.launcher3.force_reload_stale_thumbnails` | bugfix | Reloads Overview thumbnails detected as stale. | skip: fix details unknown |
| `com.android.systemui.disable_status_bar_focus_restoration` | bugfix | Stops restoring keyboard focus to the status bar after a status bar popup closes (name). | skip: focus edge case, behavior not verifiable |
| `com.android.systemui.dismiss_action_does_not_run_cancel_action` | bugfix | Keyguard dismiss action no longer runs its cancel action. | skip: lock screen fix |
| `com.android.systemui.dual_shade_nssl_expansion_fix` | bugfix | Fixes notification stack expansion in dual shade. | skip: fix details unknown; revisit if the notification popup expands wrongly |
| `com.android.systemui.end_going_away_transition_on_lockscreen_shown` | bugfix | Ends the keyguard going-away transition when the lock screen shows again. | skip: lock screen fix |
| `com.android.systemui.face_auth_avoid_dropped_statuses` | bugfix | Face auth status updates are not dropped. | skip: face unlock |
| `com.android.systemui.face_unlock_default_ripple_location_fix` | bugfix | Fixes the face unlock ripple origin. | skip: face unlock |
| `com.android.systemui.hun_rendering_without_blur_fix` | bugfix | Fixes heads-up rendering when blur is unavailable. | skip: fix details unknown; revisit if heads-up notifications render wrong without GPU blur |
| `com.android.systemui.lockscreen_gone_visibility_race_fix` | bugfix | Fixes a race in lock screen visibility when going to Gone. | skip: lock screen fix |
| `com.android.systemui.magnification_fullscreen_border_fix_corners` | bugfix | Fixes corners of the fullscreen magnification border. | skip: accessibility magnification |
| `com.android.systemui.media_output_dialog_use_display_context` | bugfix | Media output dialog uses the display context. | skip: multi-display dialog fix |
| `com.android.systemui.media_output_dialog_volume_lockup_fix` | bugfix | Fixes a volume lockup in the media output dialog. | skip: media fix |
| `com.android.systemui.notification_section_clear_button_hover_fix` | bugfix | Fixes hover on the notification section clear button. | skip: fix details unknown |
| `com.android.systemui.qs_edit_mode_tooltip_hover_dismiss` | bugfix | QS edit mode tooltip dismisses on hover. | skip: small fix, details unknown |
| `com.android.systemui.qs_security_dialog_use_themed_context` | bugfix | QS security dialog uses a themed context. | skip: theming fix |
| `com.android.systemui.scene_bounds_update_on_config_change` | bugfix | Scene container bounds updated on configuration change. | skip: scene container fix, revisit if popups mis-size after a resolution change |
| `com.android.systemui.scene_filter_multiple_touch_streams` | bugfix | Scene container filters concurrent touch streams. | skip: input fix |
| `com.android.window.flags.adjust_dimmer_on_visible_token` | bugfix | Adjusts the dim layer when its window token becomes visible. | skip: WM dim fix |
| `com.android.window.flags.affect_system_bar_during_transition` | bugfix | System bar appearance follows the transitioning window. | skip: WM core fix, code not in reference |
| `com.android.window.flags.deactivate_desk_on_home_toback` | bugfix | Desk deactivated when Home is moved to back. | skip: desk state fix inside system_server, Googlebook code not in reference |
| `com.android.window.flags.desktop_minimize_multiple_tasks_bugfix` | bugfix | Fixes minimizing several desktop tasks at once. | skip: fix details unknown |
| `com.android.window.flags.desktop_scrim_always_use_altered_task_bounds_bugfix` | bugfix | Scrim state computed from the task's new (altered) bounds. | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.desktop_scrim_animation_driven_maximize` | bugfix | Scrim switches in step with the maximize animation instead of at its start. | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.desktop_scrim_display_layout_change_transition_bugfix` | bugfix | Scrim updated after display layout change transitions (resolution/rotation). | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.desktop_scrim_move_to_display_bugfix` | bugfix | Scrim updated on both displays when a window moves between displays. | skip: multi-display only |
| `com.android.window.flags.desktop_scrim_non_resizable_maximize_bugfix` | bugfix | Scrim correct when a non-resizable window is maximized. | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.desktop_scrim_pass_pending_task_bounds_on_desk_activation` | bugfix | Pending launch bounds counted when a desk activates. | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.desktop_scrim_stable_bounds_listener_bugfix` | bugfix | Scrim recomputed when the display's stable insets change (e.g. taskbar or status bar size), so maximized detection stays right. | implemented: frameworks/base `flags2`, "WMShell: Desktop scrim follows stable insets changes"; `config_desktopScrimFollowsStableInsets` |
| `com.android.window.flags.desktop_scrim_transition_observer_bugfix` | bugfix | Scrim recomputed when any tracked freeform transition finishes (TransitionObserver), fixing stale opaque/transparent status bar. | implemented: frameworks/base `flags2`, "WMShell: Desktop scrim follows untracked freeform transitions"; `config_desktopScrimTracksTransitions` |
| `com.android.window.flags.desktop_scrim_use_divider_bar_signal` | bugfix | Double-tiled state for the scrim taken from the tiling divider bar visibility. | skip: desktop scrim exists here (frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/desktopmode/DesktopScrimController.kt, opaque status bar/wallpaper dim for maximized or tiled windows) but this fix is not observed on a single internal display; revisit if the status bar stays opaque/transparent wrongly |
| `com.android.window.flags.display_aware_autofill_dialog` | bugfix | Autofill dialog shows on the right display. | skip: multi-display fix |
| `com.android.window.flags.enable_adjust_restored_bounds_in_fallback_display` | bugfix | Restored window bounds adjusted when falling back to another display. | skip: multi-display disconnect fix |
| `com.android.window.flags.enable_clipping_remembered_bounds_bugfix` | bugfix | Remembered launch bounds clipped to the current display. | skip: fix lives in launch-bounds code whose Googlebook version is not in reference; revisit after a resolution change bug |
| `com.android.window.flags.enable_close_task_policy_check_bugfix` | bugfix | Policy check before closing a task. | skip: fix details unknown |
| `com.android.window.flags.enable_desktop_first_policy_fullscreen_refocus_bugfix` | bugfix | Desktop-first policy when a fullscreen app regains focus. | skip: fix in system_server DesktopModeLaunchParamsModifier, Googlebook code not in reference (gbos-ref has no services.jar); revisit if the symptom shows |
| `com.android.window.flags.enable_desktop_first_policy_keyguard_locked_bugfix` | bugfix | Desktop-first policy for launches while the keyguard is locked. | skip: fix in system_server DesktopModeLaunchParamsModifier, Googlebook code not in reference |
| `com.android.window.flags.enable_desktop_first_policy_no_active_desk_bugfix` | bugfix | Desktop-first policy for launches when no desk is active (e.g. after boot or after the last window closes). | skip: fix in system_server DesktopModeLaunchParamsModifier, Googlebook code not in reference; revisit if an app launches fullscreen on the PC |
| `com.android.window.flags.enable_desktop_first_policy_relaunch_bugfix` | bugfix | Desktop-first policy when an existing task is relaunched. | skip: fix in system_server, Googlebook code not in reference |
| `com.android.window.flags.enable_desktop_first_policy_source_aware_launch_root_bugfix` | bugfix | Launch root chosen according to the source task under desktop-first. | skip: fix in system_server, Googlebook code not in reference |
| `com.android.window.flags.enable_desktop_focus_observer_pipeline_fix` | bugfix | Fixes the desktop focus observer pipeline. | skip: fix details unknown |
| `com.android.window.flags.enable_interactive_pip_float_over_fullscreen_bugfix` | bugfix | Interactive PiP floats over fullscreen apps. | skip: PiP |
| `com.android.window.flags.enable_recents_with_always_on_top_tasks_bugfix` | bugfix | Recents works with always-on-top tasks present. | skip: fix details unknown |
| `com.android.window.flags.enable_scrim_update_on_fullscreen_task_launch` | bugfix | Scrim cleared when a fullscreen task launches from the desk. | skip: already present under the older declared name |
| `com.android.window.flags.enable_slide_to_desk_wallpaper_fix` | bugfix | Wallpaper fix for the slide-to-desk transition. | skip: fixes a transition our tree lacks |
| `com.android.window.flags.enable_task_in_another_desk_relaunch_bugfix` | bugfix | Relaunching a task that lives in another desk. | skip: multi-desk fix, details unknown |
| `com.android.window.flags.enable_task_visibility_during_veiled_resize` | bugfix | Task surface stays visible under the resize veil. | skip: fix details unknown |
| `com.android.window.flags.exit_desktop_on_keyguard_occlude_bugfix` | bugfix | Exits desktop when an activity occludes the keyguard. | skip: lock screen fix |
| `com.android.window.flags.fallback_wallpaper_dim_amount_bugfix` | bugfix | Fallback wallpaper dim amount for the scrim. | skip: dim path unused with opaque_status_bar on |
| `com.android.window.flags.fix_cursor_resize_hitbox` | bugfix | Fixes the resize cursor hit area on window edges. | skip: fix details unknown; revisit if resize cursors appear off-edge |
| `com.android.window.flags.fix_desk_switch_alpha_animation` | bugfix | Fixes alpha in the desk switch animation. | skip: multi-desk animation fix |
| `com.android.window.flags.fix_focus_moved_while_dimming_task` | bugfix | Focus change while a task is dimmed. | skip: fix details unknown |
| `com.android.window.flags.fix_focused_app_desync` | bugfix | Fixes focused-app desync between WM and input. | skip: WM core fix |
| `com.android.window.flags.fix_split_veil_glitch` | bugfix | Fixes a split-screen veil glitch. | skip: split screen |
| `com.android.window.flags.focus_launcher_behind` | bugfix | Focus goes to the launcher behind when nothing else is focusable (name). | skip: condition unknown |
| `com.android.window.flags.ignore_vis_when_desk_activation_bugfix` | bugfix | Ignores visibility while a desk activates. | skip: fix details unknown |
| `com.android.window.flags.ignore_vis_when_unsecured_awake_bugfix` | bugfix | Ignores visibility when awake without a secure keyguard. | skip: fix details unknown |
| `com.android.window.flags.predictive_back_transition_fast_gesture_fix` | bugfix | Predictive back with very fast gestures. | skip: gesture fix |
| `com.android.window.flags.projected_mode_app_display_move_bugfix` | bugfix | App display move in projected mode. | skip: projected mode |
| `com.android.window.flags.reset_first_window_drawn_on_stopping` | bugfix | Resets firstWindowDrawn when an activity stops. | skip: WM core fix |
| `com.android.window.flags.resolve_resumed_activity_from_leaf_task` | bugfix | Resumed activity resolved from the leaf task. | skip: WM core fix |
| `com.android.window.flags.skip_incompatible_root_task_from_source` | bugfix | Skips an incompatible root task taken from the source. | skip: WM core fix |
| `com.android.window.flags.skip_screenshot_if_no_window_drawn` | bugfix | No task screenshot before any window drew. | skip: WM core fix |
| `com.android.window.flags.trampoline_launch_task_cleanup` | bugfix | Cleans up tasks left by trampoline launches. | skip: GB trampolines code we lack |
| `com.android.window.flags.transparent_fullscreen_launch_exit_desktop_bugfix` | bugfix | Transparent fullscreen launch exits desktop correctly. | skip: fix details unknown |
| `com.android.window.flags.update_app_compat_properties_on_root_change_bugfix` | bugfix | App compat properties refreshed on root change. | skip: app compat fix |
| `com.android.window.flags.update_desktop_scrim_on_drag_resize_end_bugfix` | bugfix | Scrim updated when a drag-resize ends. | skip: already present under the older declared name |
| `com.android.window.flags.use_task_description_background_color_bugfix` | bugfix | Header color from the TaskDescription background color. | skip: our header theme comes from the top opaque activity |
| `com.android.wm.shell.fix_notes_bubble_new_task` | bugfix | Notes bubble starts a new task. | skip: notes bubble |
| `com.android.wm.shell.fix_pip_with_bubble_transition` | bugfix | PiP with a bubble transition. | skip: PiP/bubbles |
| `com.android.wm.shell.set_remaining_split_stage_windowing_mode_on_desktop_exit` | bugfix | Remaining split stage windowing mode set on desktop exit. | skip: split screen fix |
| `com.android.wm.shell.task_view_clear_pending` | bugfix | TaskView clears pending state. | skip: TaskView fix |
| `com.android.launcher3.delay_handoff_recents_targets` | internal | Delays handing the recents animation targets to Launcher (timing of the recents transition). | skip: transition plumbing, no visible behavior of its own |
| `com.android.launcher3.enable_home_screen_files_file_operation_service_proxy` | internal | Home-screen file copy/move/trash runs through a proxy to DocumentsUI's file operation service. | skip: plumbing; needs the matching DocumentsUI service API (GB flag com.android.documentsui.flags.home_screen_files_ro) |
| `com.android.launcher3.enable_home_screen_files_perf_mitigations` | internal | Performance mitigations for file items on the home screen. | skip: perf only, no visible behavior |
| `com.android.launcher3.enable_swipe_handler_state_manager_transition_handling` | internal | Swipe-up gesture handler drives state through the StateManager. | skip: refactor |
| `com.android.launcher3.enable_system_drag_of_wrapped_item_info` | internal | System drag-and-drop out of Launcher carries a wrapped ItemInfo. | skip: plumbing |
| `com.android.launcher3.refactor_empty_desk_launch` | internal | Refactor of launching an app into an empty desk. | skip: refactor |
| `com.android.launcher3.reparent_overview_overlay_on_home_task_overlay` | internal | Reparents the Overview overlay onto the home task overlay layer. | skip: surface plumbing |
| `com.android.launcher3.snackbar_in_compose` | internal | Launcher snackbar rewritten in Compose (same look). | skip: rewrite, no visible change |
| `com.android.systemui.alternate_bouncer_handler_thread` | internal | Alternate bouncer on its own handler thread. | skip: threading |
| `com.android.systemui.animation_library_shared_container` | internal | Animation library uses a shared container for launch animations. | skip: refactor |
| `com.android.systemui.controls_unbind_after_inactivity` | internal | Device controls service unbinds after inactivity. | skip: service lifecycle |
| `com.android.systemui.controls_validate_preferred_packages` | internal | Validates the preferred device controls packages. | skip: validation, no UI |
| `com.android.systemui.depth_controller_cleanup` | internal | Cleanup of NotificationShadeDepthController (blur depth). | skip: refactor |
| `com.android.systemui.dream_occlusion_refactor` | internal | Dream occlusion refactor. | skip: dreams refactor |
| `com.android.systemui.flexiglass_aosp_slice_view` | internal | unknown: scene container (flexiglass) slice view variant. | skip: internal, effect unknown |
| `com.android.systemui.flexiglass_report_expensive_frames` | internal | Reports expensive frames in the scene container. | skip: perf logging |
| `com.android.systemui.notification_empty_shade_in_compose` | internal | Empty-shade view moved to Compose. | skip: rewrite |
| `com.android.systemui.shared.sidefps_controller_refactor` | internal | Side fingerprint sensor controller refactor. | skip: refactor, no side FPS on PC |
| `com.android.systemui.stl_fling_delegate_use_target_content` | internal | SceneTransitionLayout fling delegates to target content. | skip: animation framework internals |
| `com.android.systemui.stl_fling_dynamic_spring` | internal | SceneTransitionLayout fling uses a dynamic spring. | skip: animation framework internals |
| `com.android.systemui.stl_no_transition_read_during_element_composition` | internal | SceneTransitionLayout avoids reading transitions during composition. | skip: perf |
| `com.android.systemui.stl_remove_canceled_transition_filtration` | internal | SceneTransitionLayout stops filtering canceled transitions. | skip: internals |
| `com.android.systemui.udfps_dedicated_window_thread` | internal | Under-display fingerprint window on its own thread. | skip: threading |
| `com.android.systemui.use_on_device_entered_flow` | internal | Uses the device-entered flow for unlock state. | skip: plumbing |
| `com.android.window.flags.app_compat_properties_caching` | internal | Caches app compat properties. | skip: perf |
| `com.android.window.flags.attach_client_surface_with_sync` | internal | Client-created surfaces attached with sync. | skip: plumbing |
| `com.android.window.flags.can_control_touch_mode_api` | internal | API to control touch mode. | skip: API |
| `com.android.window.flags.enable_attach_drag_indicator_to_desk` | internal | Drag-to-desktop visual indicator attached to the desk surface. | skip: surface plumbing |
| `com.android.window.flags.enable_desktop_windowing_mode_modifier_done` | internal | Desktop launch params modifier returns DONE (stops later modifiers). | skip: launch params plumbing |
| `com.android.window.flags.enable_pinned_window_trusted_overlay` | internal | Pinned (always on top) window layer marked as trusted overlay. | skip: input plumbing |
| `com.android.window.flags.enable_skip_app_header_view_update_during_recents_transitions` | internal | Skips header view updates during recents transitions. | skip: perf |
| `com.android.window.flags.ignore_user_context_changes_for_specific_transitions` | internal | Ignores user-context changes in some transitions. | skip: plumbing |
| `com.android.window.flags.init_transform_of_default_start_tx` | internal | Initializes the transform in the default start transaction. | skip: plumbing |
| `com.android.window.flags.layout_insets_during_animation_mode_visible_types` | internal | Insets layout during animations for visible types. | skip: insets plumbing |
| `com.android.window.flags.log_task_trampolines` | internal | Logs task trampolines. | skip: logging |
| `com.android.window.flags.merge_display_window_settings_on_restore` | internal | Merges display window settings on backup restore. | skip: restore plumbing |
| `com.android.window.flags.offload_set_top_on_back_invoked` | internal | Offloads setTop on back invocation. | skip: perf |
| `com.android.window.flags.separate_starting_window_records` | internal | Separate records for starting windows. | skip: refactor |
| `com.android.window.flags.set_user_initiated_on_minimize_task` | internal | Marks minimize requests as user-initiated. | skip: metadata |
| `com.android.window.flags.simplify_window_movement` | internal | Simplified window movement code. | skip: refactor |
| `com.android.window.flags.trampoline_tracing` | internal | Tracing for trampolines. | skip: tracing |
| `com.android.window.flags.unique_global_desk_ids` | internal | Desk ids unique across displays. | skip: plumbing |
| `com.android.window.flags.update_focused_app_in_ae` | internal | Updates the focused app in activity embedding. | skip: activity embedding |
| `com.android.window.flags.use_gesture_interceptor_for_pinned_windows` | internal | Pinned windows header gestures handled through a gesture interceptor. | skip: input plumbing |
| `com.android.wm.shell.optimize_pip_app_icon_overlay` | internal | Optimized PiP app icon overlay. | skip: perf |

## Integration

What the device tree and manifests need (not edited by this work):

1. `.repo/local_manifests/pc.xml`: use the `pc` branches and add this repository:

   ```xml
   <remove-project name="LineageOS/android_frameworks_base" />
   <project path="frameworks/base" name="android_frameworks_base" remote="pc" revision="capture" />
   <remove-project name="LineageOS/android_packages_apps_Launcher3" />
   <project path="packages/apps/Launcher3" name="android_packages_apps_Launcher3" remote="pc" revision="pc" />
   <project path="vendor/pc/ui" name="android_vendor_pc_ui" remote="pc" revision="capture" />
   <project path="packages/apps/PcClocks" name="android_packages_apps_PcClocks" remote="pc" revision="lineage-24.0" />
   ```

   The `capture` branches (screen capture, section 7) sit on top of `pc`; until they are merged,
   build either both `capture` branches or both `pc` branches: the SystemUI overlay of `capture`
   sets `config_screenRecordingFolder`, which only frameworks/base `capture` declares.

   Locally the branches already exist in the synced projects:
   `git -C frameworks/base checkout capture`, `git -C vendor/pc/ui checkout capture` and
   `git -C packages/apps/Launcher3 checkout pc`; `packages/apps/PcClocks` is a local repository
   (branch `lineage-24.0`) with no remote yet.
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

4. The flag ports of "Googlebook flags this tree does not declare" live on branch `flags2` of
   `frameworks/base` and `packages/apps/Launcher3` (on top of `flags`, which is on top of `pc`); merge
   them into `pc` (or build from `flags2`) together with this repository's `flags2`, whose overlays
   turn them on. Without the code branches the overlays' new values have no target and the overlay
   build fails, so the three move together.
5. Nothing else: no release config or lunch change (still `lineage_pc_x86_64-cp2a-userdebug`).

## Verification status

Verified on the host: overlay resource names against the tree, flag names against the tree's
aconfig declarations, the release config (release-config lists the value set last in cp2a).
Screen capture and clocks: the new Kotlin compiles against the tree's built framework,
SystemUIPluginLib, SystemUIClocks-CommonLib and ICU jars (kotlinc, outside Soong); the plain
logic tests (region geometry, recordings folder, clock model) run on the host. Not verified:
Soong/R8 builds of the clock APKs, SystemUI's device tests, and recordings and faces on a device.

Not verified without a build: compilation of the Launcher3, Shell, SystemUI and framework changes

Branch `flags2` was checked on the host against the previous build's jars: every changed production
file of `framework`, `services`, WM Shell, SystemUI (with the generated `ILauncherProxy`) and Launcher3
compiles (`kotlinc`/`javac`, new resource ids added to the R classes), and the plain JUnit rule tests
pass (168 in frameworks/base, 10 in Launcher3). The Android unit tests that come with each change
(Mockito, Kosmos, `ShellTestCase`, `SysuiTestCase`) need `atest`.
Not verified without a build: Dagger graphs, resource compilation, compilation of the Launcher3, Shell, SystemUI and framework changes
and their unit tests (`WMShellUnitTests`, `SystemUITests`, `WmTests`, `FrameworksCoreTests`;
Launcher3's quickstep tests have no test module in AOSP), RRO compilation,
and the runtime result of the 134 flags together (in particular `scene_container` with
LineageOS's SystemUI changes).
