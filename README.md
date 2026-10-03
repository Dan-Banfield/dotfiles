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

Install Git, GNU Stow, Hyprland, Hyprpaper (0.8 or newer), and the applications
your configuration uses. The wallpaper helper also uses Bash, coreutils,
util-linux (`flock`), and `file`, normally available on an Arch installation.
Clone this repository into `~/dotfiles`, then:

```bash
cd ~/dotfiles
stow --simulate --verbose --no-folding --target="$HOME" hypr wallpapers scripts
stow --verbose --no-folding --target="$HOME" hypr wallpapers scripts
```

If the preview reports existing files that conflict, back them up outside this
repository and move them aside before applying. Keep unrelated configuration
files in place.

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
stow --restow --no-folding --target="$HOME" hypr wallpapers scripts
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
stow --delete --target="$HOME" hypr wallpapers scripts
```

This removes the managed symlinks; the configuration files remain in the repository.
