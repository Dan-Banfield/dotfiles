# Blue Night SDDM theme

Designed for the installed SDDM 0.21 Qt 5 greeter. The theme uses Qt Quick
2.15 and Qt Quick Controls 2.15, supplied by `qt5-declarative` and
`qt5-quickcontrols2`. Both are already installed on this laptop. The font is
`JetBrainsMono Nerd Font` (`ttf-jetbrains-mono-nerd`), also already installed.

The wallpaper, navy card, rounded password field, pastel blue gradients,
12-hour clock, and date match Hyprlock. The card fades and slides in, popups
animate, buttons respond to hover/press, and an unsuccessful login gently
shakes the password field. Caps Lock highlights the outline in pale gold.
OpenGL rendering blurs the wallpaper with two static Gaussian passes. Software
rendering falls back to the dimmed wallpaper, with the same login controls.
Icons are drawn with Qt Quick Canvas and need no SVG or effects package.

The theme uses SDDM's real user/session models, keyboard layout selection,
authentication signals, and power capabilities. It remembers SDDM's last
selected user/session, and the username can be edited for an unlisted account.
Enter submits the password; Tab moves between controls. Restart and Power Off
require confirmation. Authentication continues through SDDM's existing PAM
configuration.

## Preview

From your running desktop, as your normal user:

```bash
~/dotfiles/sddm/install.sh --preview
```

This runs `sddm-greeter --test-mode`; it does not authenticate or execute power
actions. Close the preview to return to the desktop. Some controls may be
unavailable in SDDM's test mode. `preview.png` is a rendered example with mock
session/power data; the real greeter uses SDDM's own models.

## Install or update

```bash
~/dotfiles/sddm/install.sh
```

The script requests sudo in your terminal, installs the theme under
`/usr/share/sddm/themes/blue-night`, and selects it through
`/etc/sddm.conf.d/99-blue-night.conf`. The wallpaper link is dereferenced when
copied, so the SDDM account never needs access to your home folder. Files are
root-owned and world-readable. The same config selects the installed macOS
cursor at size 24.

Any existing Blue Night theme or matching config fragment is backed up under
`/var/backups/dotfiles-sddm/` before replacement. Other themes and SDDM settings
are retained. SDDM is not restarted by the installer; the theme appears when
the login screen is next shown, including after logging out or rebooting.

SDDM is a system service, so this directory is installed separately from the
home-directory Stow packages. Pulling changes or changing the bundled wallpaper
requires running the installer again. For local SDDM-only options, a
`theme.conf.user` file in the installed theme can override `Background` or
`Font` without changing the tracked defaults.

## Return to the default theme

```bash
sudo rm /etc/sddm.conf.d/99-blue-night.conf
```

If this file replaced a previous config fragment, restore its saved copy from
the backup directory instead. The theme files can remain installed without
being selected.
