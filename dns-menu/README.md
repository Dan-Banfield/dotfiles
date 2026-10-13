# Change DNS

A resident GTK4 menu matching the power menu's navy card, pastel blue accents,
rounded fields, fade/slide entrance, and animated input changes. Find **Change
DNS** in Walker. Choose Automatic, Standard DNS, DNS over TLS, or DNS over HTTPS,
then Cloudflare, Quad9, Google, or Custom. Editing a preset selects Custom.

TLS inputs accept hostnames with an optional port (853 by default), or `tls://`
URLs. HTTPS inputs accept full `https://` DNS endpoints. Enter one server per
line, up to eight. Standard DNS accepts IPv4/IPv6 addresses. Bootstrap inputs
accept comma-separated IPv4/IPv6 addresses; these resolve the encrypted server's
hostname before the encrypted connection is established. TLS certificates are
verified, and encrypted modes have no fallback to unencrypted query servers.

## Install

The UI requires `python-gobject`, `gtk4`, `gtk4-layer-shell`, and a graphical
Polkit authentication agent. This system already has the KDE Polkit agent; the
launcher reuses an existing agent or starts it. The backend uses the Arch
`dnsproxy` package and NetworkManager's default DNS backend.

```bash
cd ~/dotfiles
stow --no-folding --ignore='__pycache__|\.bak$' hypr dns-menu scripts walker
sudo pacman -S --needed dnsproxy
~/dotfiles/dns-menu/install.sh
hyprctl reload
~/.local/bin/launcher-start --restart
~/.local/bin/change-dns --background
```

The menu also has **Install DNS support**, which opens these package/backend
installation steps in Kitty. Installation does not change DNS. The system
installer places a root-owned helper, its validated settings module, a dedicated
systemd unit, and a Polkit action under `/usr/lib`, `/etc`, and `/usr/share`.
Run the installer again after pulling backend changes. Stow only installs the
home-directory `.config` contents of this package.

## Apply and restore

**Apply DNS** asks for administrator authentication. The helper validates the
request again, starts a resolver listening only on `127.0.0.1:53`, and verifies a
DNS answer for `example.com` before directing NetworkManager to it. If the
change fails, the previous files and service state are restored. Changes are
serialized so two requests cannot overwrite one another. The backend does not
change Wi-Fi profiles, saved passwords, or reconnect your network.

The managed NetworkManager file is
`/etc/NetworkManager/conf.d/90-dotfiles-dns.conf`. It overrides network DNS
globally. This includes DNS supplied by VPNs and private networks, so select
**Automatic** when you need their private DNS or a captive portal. Browser apps
with their own Secure DNS setting may continue to use their selected resolver.
Automatic removes this tool's override, reloads NetworkManager's DNS settings,
and disables its proxy. Existing per-network DNS preferences return.

Saved DNS choices are in `/etc/dotfiles-dns/settings.json`; they are not tracked
in Git. The resolver's generated configuration is `/etc/dotfiles-dns/proxy.yaml`.

Checks:

```bash
~/.local/bin/change-dns --check
systemctl status dotfiles-dns.service
journalctl -u dotfiles-dns.service -n 30
```

For terminal recovery, or before removing the backend:

```bash
sudo rm -f /etc/NetworkManager/conf.d/90-dotfiles-dns.conf
sudo nmcli general reload conf,dns-full
sudo systemctl disable --now dotfiles-dns.service
```

To update the UI after editing Python or CSS:

```bash
~/.local/bin/change-dns --quit
~/.local/bin/change-dns --background
```

Run the validation, transaction, and installed `nmcli` parser tests without root
access or networking. The parser check uses a nonexistent D-Bus address so it
cannot reach the live NetworkManager service:

```bash
PYTHONDONTWRITEBYTECODE=1 python ~/dotfiles/dns-menu/tests/test_dns.py
```

Protocol and integration references:

- [dnsproxy documentation](https://github.com/AdguardTeam/dnsproxy/tree/v0.86.0)
- [NetworkManager global DNS configuration](https://networkmanager.dev/docs/api/latest/NetworkManager.conf.html#global-dns-domain-sections)
- [Cloudflare resolver addresses](https://developers.cloudflare.com/1.1.1.1/infrastructure/network-operators/)
- [Quad9 resolver addresses](https://docs.quad9.net/services/)
- [Google encrypted DNS](https://developers.google.com/speed/public-dns/docs/secure-transports)
