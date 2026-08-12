---
name: gnome-script-launchers
description: Use when creating, updating, troubleshooting, or organizing Ubuntu GNOME dock buttons, .desktop launchers, Zenity control menus, script shortcuts, launcher icons, or taskbar actions for commands stored across multiple projects.
---

# GNOME Script Launchers

## Overview

Create maintainable GNOME launchers that expose scripts as individual dock buttons or as actions in one Zenity control menu. Keep project commands in their projects and keep the desktop entry thin.

## Workflow

1. Inspect the desktop environment and dependencies: `zenity`, `notify-send`, and `update-desktop-database`.
2. Inventory each action, its absolute command path, interactivity, failure behavior, and destructive impact.
3. Read existing dispatcher and `.desktop` files before editing; preserve unrelated actions and user customization.
4. Store the dispatcher in the owning project and the launcher in `~/.local/share/applications/<id>.desktop`.
5. Validate paths and syntax, refresh the application database, then explain how to search for and pin the launcher.

## Choose the UI

- Create one `.desktop` file per action when the user explicitly wants several independent dock icons.
- Create one Zenity dispatcher when actions belong together or would clutter the dock.
- Use `Terminal=false` for non-interactive commands with graphical feedback.
- Use `Terminal=true` or launch a terminal when a command requires input, passwords, or sustained log viewing.

## Implementation Rules

- Use absolute paths in `Exec=` and dispatcher actions; `.desktop` files do not reliably inherit the user's interactive shell environment.
- Run aliases or shell functions through the intended interactive shell, such as `/usr/bin/zsh -lic 'command'`.
- Quote action labels and paths defensively; do not construct executable commands from untrusted menu text.
- Treat menu cancellation as a clean exit.
- Show success only when the command exits successfully; display captured errors otherwise.
- Add a confirmation dialog before reboot, shutdown, sleep, deletion, or other disruptive actions.
- Use an icon-theme name or an absolute existing PNG/SVG path in `Icon=`.
- Do not rewrite GNOME favorites with `gsettings` unless the user explicitly asks to pin or reorder icons.
- Ask for approval before writing outside the active workspace when permissions require it.

## Desktop Entry

Use this minimal shape:

```ini
[Desktop Entry]
Type=Application
Name=Control Menu
Comment=Run maintenance actions
Icon=utilities-system-monitor
Exec=/absolute/path/to/control-menu.sh
Terminal=false
Categories=Utility;
```

## Existing Launcher Overrides

When adapting an installed application launcher, preserve the system entry and create a per-user override:

```bash
mkdir -p ~/.local/share/applications
cp /usr/share/applications/<application-id>.desktop ~/.local/share/applications/<application-id>.desktop
```

Edit only the user copy. Use absolute paths in `Exec=`. For aliases or shell functions, invoke the intended interactive shell explicitly, for example:

```ini
Exec=/usr/bin/zsh -lic "sg libvirt -c /usr/bin/virt-manager"
```

Desktop-entry quoting uses double quotes for grouped arguments; shell single-quote syntax is not interpreted by the desktop-entry parser. After editing, validate the user copy and refresh its application database. If GNOME continues using a cached old launcher, unpin the old dock icon and pin the refreshed application entry.

## Verification

Run:

```bash
bash -n /absolute/path/to/control-menu.sh
desktop-file-validate ~/.local/share/applications/control-menu.desktop
update-desktop-database ~/.local/share/applications
```

If `desktop-file-validate` is unavailable, inspect the required desktop-entry fields manually. If GNOME retains an old icon, remove and re-add the favorite after refreshing the database.
