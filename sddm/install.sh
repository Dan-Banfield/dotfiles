#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
theme_source="$script_dir/themes/blue-night"
theme_target=/usr/share/sddm/themes/blue-night
config_target=/etc/sddm.conf.d/99-blue-night.conf

if [[ ${1:-} == --preview && $# == 1 ]]; then
    # Test mode cannot authenticate or execute power actions.
    exec env QT_QPA_PLATFORMTHEME= QT_STYLE_OVERRIDE= QT_QUICK_CONTROLS_STYLE=Default \
        sddm-greeter --test-mode --theme "$theme_source"
fi
if [[ $# -gt 0 ]]; then
    printf 'Usage: %s [--preview]\n' "$0" >&2
    exit 2
fi

for file in Main.qml Choice.qml ActionButton.qml Icon.qml SoftBlur.qml metadata.desktop theme.conf wallpaper.jpeg; do
    if [[ ! -r "$theme_source/$file" ]]; then
        printf 'Theme file missing: %s\n' "$theme_source/$file" >&2
        exit 1
    fi
done

if (( EUID != 0 )); then
    exec sudo bash "$script_dir/install.sh"
fi

# Preserve replaced files outside Git. Do not restart the display manager.
backup_dir="/var/backups/dotfiles-sddm/$(date +%Y%m%d-%H%M%S)-$$"
if [[ -e "$theme_target" || -e "$config_target" ]]; then
    install -d -m 0700 "$backup_dir"
    [[ ! -e "$theme_target" ]] || cp -a -- "$theme_target" "$backup_dir/blue-night"
    [[ ! -e "$config_target" ]] || cp -a -- "$config_target" "$backup_dir/99-blue-night.conf"
    printf 'Previous files saved to %s\n' "$backup_dir"
fi

install -d -m 0755 "$theme_target" /etc/sddm.conf.d
for file in Main.qml Choice.qml ActionButton.qml Icon.qml SoftBlur.qml metadata.desktop theme.conf wallpaper.jpeg; do
    install -m 0644 -- "$theme_source/$file" "$theme_target/$file"
done
install -m 0644 -- "$script_dir/99-blue-night.conf" "$config_target"
printf 'Blue Night installed. It will appear the next time SDDM shows the login screen.\n'
