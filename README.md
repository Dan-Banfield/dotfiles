# Dotfiles

Personal configuration managed with Git and GNU Stow.

## Layout

Each top-level application directory is a Stow package. Its contents mirror
paths relative to your home directory:

```text
hypr/.config/hypr/hyprland.lua -> ~/.config/hypr/hyprland.lua
```

The initial package contains the existing Hyprland Lua configuration. Application
and dependency installation is currently manual. Use a Hyprland version that
supports this configuration format.

## Install

Install Git, GNU Stow, Hyprland, and the applications your configuration uses.
Clone this repository into `~/dotfiles`, then:

```bash
cd ~/dotfiles
stow --simulate --verbose --no-folding --target="$HOME" hypr
stow --verbose --no-folding --target="$HOME" hypr
```

If the preview reports existing files that conflict, back them up outside this
repository and move them aside before applying. Keep unrelated configuration
files in place.

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
stow --restow --no-folding --target="$HOME" hypr
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
stow --delete --target="$HOME" hypr
```

This removes the managed symlinks; the configuration files remain in the repository.
