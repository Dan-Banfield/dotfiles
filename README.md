# Dotfiles

Personal configuration managed with Git and GNU Stow.

## Layout

Each top-level application directory is a Stow package. Its contents mirror
paths relative to your home directory:

```text
hypr/.config/hypr/hyprland.lua -> ~/.config/hypr/hyprland.lua
```

The Hyprland package uses Lua configuration. `hyprland.lua` loads `keybinds.lua`,
which contains all shortcuts. Application and dependency installation is manual.
Use a Hyprland version that supports this configuration format.

## Hyprland shortcuts

`Super` is the Windows key. Workspace number shortcuts use physical number-row
keycodes, with 0 selecting workspace 10.

| Shortcut | Action |
| --- | --- |
| Super + Q / W | Close the focused window |
| Super + arrows | Focus a window |
| Super + Alt + arrows | Move a window |
| Super + Shift + arrows | Swap windows |
| Super + 1–0 | Switch workspace |
| Super + Shift + 1–0 | Move window and follow |
| Super + Alt + 1–0 | Move window without following |
| Super + Alt + Shift + 1–0 | Alternate silent move shortcut |
| Super + Tab / Shift + Tab / Ctrl + Tab | Next / previous / former workspace |
| Super + S / Alt + S | Show scratchpad / send window to scratchpad |
| Super + Alt + Shift + arrows | Move workspace to another monitor |
| Alt + Tab / Shift + Tab | Cycle windows and raise the focused window |
| Ctrl + Alt + Tab / Shift + Tab | Cycle monitors |
| Super + F / Alt + F | Fullscreen / maximize |
| Super + V / J / P | Toggle floating / split / pseudo tiling |
| Super + - / = | Resize horizontally by 100 pixels |
| Super + Shift + - / = | Resize vertically by 100 pixels |
| Add Alt / Ctrl to resize shortcuts | Use 25 / 300 pixel increments |
| Super + left / right mouse drag | Move / resize window |
| Super + mouse wheel | Cycle workspaces |
| Super + G / Alt + G | Toggle grouping / remove window from group |
| Super + Alt + Tab / Alt + Shift + Tab | Cycle grouped windows |
| Super + Ctrl + left / right | Cycle grouped windows |
| Super + Alt + mouse wheel | Cycle grouped windows |
| Super + Ctrl + Z / Alt + Ctrl + Z | Increase / reset cursor zoom |
| Super + T / Return | Open the configured terminal |
| Tap Super / Super + R | Open Walker |
| Ctrl + Alt + Delete | Open the session menu |
| Super + E / R / M | File manager / launcher / log out |

Native window and workspace shortcuts were migrated from the configuration
backup with personal overrides applied. Alt+number is reserved for silent
workspace moves, replacing the old group-index bindings. Terminal launch uses
Super+T rather than the starter config's Super+Q, which now closes windows.
Media shortcuts retain the current commands and require `wpctl`,
`brightnessctl`, and `playerctl`. App commands remain in `hyprland.lua`.

Menu, screenshot, theme, panel, application, and window-management shortcuts
that required Omarchy scripts were not imported. Universal clipboard shortcuts
that depended on Omarchy terminal tags were also omitted.

## Install

Install Git, GNU Stow, Hyprland, Hyprpaper (0.8 or newer), Waybar, Python,
JetBrains Mono Nerd Font, and the applications
your configuration uses. The wallpaper helper also uses Bash, coreutils,
util-linux (`flock`), and `file`, normally available on an Arch installation.
Clone this repository into `~/dotfiles`, then:

```bash
cd ~/dotfiles
stow --simulate --verbose --no-folding --target="$HOME" hypr wallpapers scripts waybar walker session-menu
stow --verbose --no-folding --target="$HOME" hypr wallpapers scripts waybar walker session-menu
```

If the preview reports existing files that conflict, back them up outside this
repository and move them aside before applying. Keep unrelated configuration
files in place.

## Bar

The `waybar` package supplies the floating blue pill bar. The clock uses
12-hour time with AM/PM. The centre pill shows the focused window's title,
truncated to 50 characters with the full title available on hover. Title changes
crossfade over 220 ms while the pill smoothly resizes. It fades and contracts on
empty workspaces, then fades and expands when a window is present. Scroll over
the brightness pill to adjust the display backlight with Waybar's native control;
no additional brightness helper is needed.

Start the bar with `~/.local/bin/waybar-start` (also used by Hyprland autostart).
It builds `waybar/.config/waybar/cffi/window-title.c` once and rebuilds when the
source changes, using `gcc`, `pkgconf`, and `gtk3`. The compiled library stays
outside the repository at `~/.local/lib/dotfiles/waybar/window-title.so`, so each
machine builds its own copy. To only build it, use `waybar-start --build-only`.
The widget reuses the native `hyprland/window` module's updates, with no polling
or additional Hyprland IPC. GTK Stack provides the text crossfade and width
interpolation; GTK Revealer and CSS handle hiding and showing the entire pill.
If the extension cannot load, the standard title module remains available.

The native `ext/workspaces` module shows existing workspaces in numeric order.
Click a pill to activate its workspace through the Wayland workspace protocol,
supported by the installed Hyprland and Waybar versions. The active pill expands
with the original 250 ms transition and animated blue gradient. No permanent
workspace placeholders or custom workspace helpers are used.

## Session menu

Press **Ctrl+Alt+Delete** for a dark blue menu with Lock, Sleep, Processes,
Log Out, Restart, and Power Off. The panel slides and fades in, cards appear in a
short stagger, and confirmation pages crossfade. Select with the mouse or keys
1–6; Tab/arrows move focus. Escape and clicking outside close it. Log Out,
Restart, and Power Off open a confirmation page with Go Back focused first.

The `session-menu` Stow package contains the GTK4 app and editable CSS.
It uses `python-gobject`, `gtk4`, and `gtk4-layer-shell`, already required by the
installed launcher. Hyprland warms it at login; `~/.local/bin/session-menu`
activates the resident app through D-Bus, with a normal startup fallback.
Logout uses `uwsm stop` in a managed session and the native Hyprland exit otherwise.
Processes opens `htop` in Kitty. Sleep uses the system suspend action.

After stowing the new package, reload the shortcut and open the menu:

```bash
hyprctl reload
~/.local/bin/session-menu
```

Lock is disabled until `hyprlock` is installed. A matching configuration is
provided at `hypr/.config/hypr/hyprlock.conf`, with the shared wallpaper, blue
password field, and 12-hour clock. To enable it on Arch:

```bash
sudo pacman -S --needed hyprlock
```

After editing the menu's Python or CSS, run `~/.local/bin/session-menu --quit`
and open it again. `~/.local/bin/session-menu --check` validates its dependencies
and stylesheet without opening the menu or executing any session action.

## App launcher

The `walker` package supplies the `blue-night` theme and the Walker/Elephant user
services. The panel uses the bar's navy and blue palette, rounded corners, a blue
selection gradient, and the existing short Hyprland layer animations.

Install Walker, Elephant, and its app provider together from the AUR:

```bash
yay -S --needed walker elephant elephant-desktopapplications elephant-providerlist
```

The theme targets Walker 1.x or newer with the Elephant backend. Only installed
apps are queried by default, with 12 results and no previews. App icons use GTK's
native icon lookup. Walker's service stays resident between opens; this avoids
loading the GTK frontend afresh on every invocation. First-use icon loading and
actual frame timings still depend on the installed apps, icon theme, and hardware.

The app list is configured in
`walker/.config/elephant/desktopapplications.toml`. It hides Avahi's browsers,
the advanced network editor, and hardware diagnostic/test utilities, and prefers
apps you have used when the search is empty. To hide another entry, add its
desktop filename without `.desktop` to the blacklist regexes and restart the
launcher services. Other installed apps remain discoverable automatically.

The user desktop entry in
`walker/.local/share/applications/code-oss.desktop` overrides the packaged name
with **Visual Studio Code (OSS)**. It preserves the `code-oss` command and icon;
searching `code`, `vscode`, or `vs code` also selects it through Elephant aliases.

After stowing the packages, start the services in your graphical session:

```bash
"$HOME/.local/bin/launcher-start"
hyprctl reload
pkill -USR2 -x waybar
```

Hyprland starts the services at subsequent logins through `launcher.lua`.
`launcher-start` imports the current display/session environment into D-Bus and
systemd before starting the two user services. No separate service-enabling step
is required. If you use `elephant service enable`, it may try to rewrite the
Stow-managed unit; use `launcher-start` instead.

The bar, keybindings, and autostart use explicit helper paths, so they also work
when the graphical session's PATH does not include `~/.local/bin`.

Tap and release either Super key, press Super+R, or click the bar's Apps pill.
The release bindings use Hyprland's native shortcut shadowing, so the configured
Super combinations do not also open the launcher. Arrow keys/Tab navigate,
Enter or a single click launches an app, and Escape closes the panel. The
`app-launcher` helper connects directly to the resident Walker's documented
activation socket. If Walker is stopped, it starts both services with the current
display environment and waits for the socket before opening the panel.
Passing options to `app-launcher` also uses the normal Walker command.

After changing the launcher configuration or layout, restart it with:

```bash
"$HOME/.local/bin/launcher-start" --restart
```

For troubleshooting:

```bash
systemctl --user status elephant.service walker.service
journalctl --user -u elephant.service -u walker.service -b
```

Upstream references: [Walker setup and theming](https://github.com/abenz1267/walker#usage),
[Elephant installation](https://github.com/abenz1267/elephant#installation), and
[Hyprland release bindings](https://wiki.hypr.land/Configuring/Basics/Binds/#bind-flags).

## Package picker

The `scripts` package installs `~/.local/bin/pkg-install`, a standalone
adaptation of the previous Omarchy package pickers. Install its dependencies:

```bash
sudo pacman -S --needed fzf
# AUR mode also requires yay, installed separately.
```

Run as your normal user:

```bash
pkg-install              # Official repositories
pkg-install --aur       # AUR
pkg-install browser     # Start with a search term
pkg-install --aur cursor
```

Type to fuzzy filter the package names, use the arrow keys to navigate, press
Tab to select multiple packages, then Enter to install. Esc or Ctrl+C cancels
without installing. Alt+P toggles details, Alt+J/K scrolls the preview, and
Alt+D/U scrolls by half a page. In AUR mode, Alt+B shows the PKGBUILD and
Alt+Shift+B restores package details. The AUR list is fetched when opened;
network access is required. Repository packages come from your local pacman
sync databases; keep those current through normal system upgrades.

Installation uses pacman or yay with their normal confirmation and build
prompts, skipping already installed packages. No Omarchy services or scripts
are required. Add `~/.local/bin` to your PATH, or invoke the command by its
full path.

## Wallpapers

The `wallpapers` package links the bundled collection into
`~/.local/share/wallpapers/`. `default.jpeg` is the default for every display,
using cover mode. `wallpaper.lua` starts Hyprpaper and restores your choice at
login and after a Hyprland config reload. It reuses an existing daemon.

The `scripts` package installs `~/.local/bin/wallpaper-set`. Run it inside your
Hyprland session:

```bash
~/.local/bin/wallpaper-set --default
~/.local/bin/wallpaper-set ~/Pictures/Wallpapers/example.jpg
~/.local/bin/wallpaper-set another-bundled-image.jpg
```

With no argument, or with `--restore`, it restores the saved selection. If that
image has been removed, it uses the bundled default. Selections are saved in
`${XDG_STATE_HOME:-~/.local/state}/dotfiles/wallpaper`, outside Git. Hyprpaper's
startup log (`hyprpaper.log`) and restore log (`wallpaper-set.log`) are in the
same directory. File paths containing spaces are supported;
quote them in the shell. Commas and newlines are not supported by the IPC syntax.

After installing into a running session, run `hyprctl reload` or
`~/.local/bin/wallpaper-set --default`. Check the result with
`hyprctl hyprpaper listactive`. Add `~/.local/bin` to your shell's PATH to use
the shorter `wallpaper-set` command.

## Edit and sync

Edit either the files in this repository or their symlinks in your home directory.
Review your changes, then commit and push:

```bash
cd ~/dotfiles
git diff
git add hypr
git commit -m "Update Hyprland configuration"
git push
```

Once a remote repository is configured, update another device with:

```bash
cd ~/dotfiles
git pull --ff-only
stow --restow --no-folding --target="$HOME" hypr wallpapers scripts waybar walker session-menu
```

Commit or otherwise preserve local edits before pulling.

## Add another application

Create a new package directory mirroring the application's home-relative paths.
For example, a terminal config at `~/.config/kitty/kitty.conf` belongs at
`kitty/.config/kitty/kitty.conf` in this repository. Back up the existing file,
move it into that package, then preview and apply `stow` with `kitty` in place
of `hypr`.

Add only selected configuration files. Keep credentials, caches, generated state,
and personal browser profiles out of the repository. Inspect changes before
committing, especially before publishing the repository.

## Unlink

```bash
cd ~/dotfiles
stow --delete --target="$HOME" hypr wallpapers scripts waybar walker session-menu
```

This removes the managed symlinks; the configuration files remain in the repository.
