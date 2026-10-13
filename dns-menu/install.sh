#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if (( $# )); then
    printf 'Usage: %s\n' "$0" >&2
    exit 2
fi
if [[ ! -x /usr/bin/dnsproxy ]]; then
    printf 'First install the DNS backend: sudo pacman -S --needed dnsproxy\n' >&2
    exit 1
fi
if (( EUID != 0 )); then
    exec sudo bash "$script_dir/install.sh"
fi

install -d -m 0755 /usr/lib/dotfiles-dns /etc/dotfiles-dns
install -m 0755 "$script_dir/system/apply" /usr/lib/dotfiles-dns/apply
install -m 0644 "$script_dir/.config/dns-menu/model.py" /usr/lib/dotfiles-dns/model.py
install -m 0644 "$script_dir/system/dotfiles-dns.service" /etc/systemd/system/dotfiles-dns.service
install -m 0644 "$script_dir/system/dev.dotfiles.dns.policy" /usr/share/polkit-1/actions/dev.dotfiles.dns.policy
systemctl daemon-reload
printf 'Change DNS backend installed. DNS stays unchanged until you click Apply in the menu.\n'
