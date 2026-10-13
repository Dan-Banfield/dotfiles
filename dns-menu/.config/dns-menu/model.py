"""Validated DNS settings shared by the UI and its installed privileged helper."""

import ipaddress
import json
import re
from urllib.parse import urlsplit, urlunsplit

MODES = ("automatic", "plain", "dot", "doh")
MODE_LABELS = ("Automatic · network DNS", "Standard DNS", "DNS over TLS", "DNS over HTTPS")
PRESETS = {
    "Cloudflare": {
        "plain": ["1.1.1.1", "1.0.0.1"],
        "dot": ["tls://one.one.one.one:853"],
        "doh": ["https://cloudflare-dns.com/dns-query"],
        "bootstrap": ["1.1.1.1", "1.0.0.1"],
    },
    "Quad9": {
        "plain": ["9.9.9.9", "149.112.112.112"],
        "dot": ["tls://dns.quad9.net:853"],
        "doh": ["https://dns.quad9.net/dns-query"],
        "bootstrap": ["9.9.9.9", "149.112.112.112"],
    },
    "Google": {
        "plain": ["8.8.8.8", "8.8.4.4"],
        "dot": ["tls://dns.google:853"],
        "doh": ["https://dns.google/dns-query"],
        "bootstrap": ["8.8.8.8", "8.8.4.4"],
    },
}


def split_values(text):
    return [item for item in re.split(r"[\s,;]+", text.strip()) if item]


def server_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise ValueError("DNS addresses must be IPv4 or IPv6 addresses.") from None
    if ip.is_loopback or ip.is_unspecified or ip.is_multicast:
        raise ValueError("Use an upstream IP address, not localhost or a multicast address.")
    return str(ip)


def host_name(value):
    try:
        return server_ip(value)
    except ValueError:
        pass
    try:
        host = value.encode("idna").decode("ascii").lower()
    except (UnicodeError, AttributeError):
        raise ValueError("Enter a valid DNS server hostname.") from None
    if len(host) > 253 or not all(
        re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
        for part in host.rstrip(".").split(".")
    ):
        raise ValueError("Enter a valid DNS server hostname.")
    # Reject malformed numeric addresses and localhost hostnames as well.
    if re.fullmatch(r"[0-9.]+", host) or host.rstrip(".") == "localhost":
        raise ValueError("Enter an upstream server hostname or valid IP address.")
    return host


def endpoint(value, mode):
    if not isinstance(value, str) or len(value) > 1024 or any(c.isspace() for c in value):
        raise ValueError("Each server must be a single address or URL.")
    if mode == "plain":
        return server_ip(value)
    if mode == "dot" and "://" not in value:
        value = "tls://" + value
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError:
        raise ValueError("The server URL or port is invalid.") from None
    expected = "tls" if mode == "dot" else "https"
    if url.scheme != expected or not url.hostname:
        raise ValueError("Use a TLS hostname or tls:// URL." if mode == "dot" else
                         "DNS over HTTPS requires a full https:// URL.")
    if url.username is not None or url.password is not None or url.fragment or url.query:
        raise ValueError("Server URLs must not contain login details, queries, or fragments.")
    host = host_name(url.hostname)
    if port == 0:
        raise ValueError("The port must be between 1 and 65535.")
    if mode == "dot" and url.path not in ("", "/"):
        raise ValueError("A TLS server has a hostname and port, not a URL path.")
    address = f"[{host}]" if ":" in host else host
    address += f":{port or 853}" if mode == "dot" else (f":{port}" if port else "")
    return urlunsplit((expected, address, "" if mode == "dot" else (url.path or "/dns-query"), "", ""))


def validate_settings(data):
    if not isinstance(data, dict) or set(data) - {"mode", "servers", "bootstrap"}:
        raise ValueError("Unrecognized DNS settings.")
    mode = data.get("mode")
    if mode not in MODES:
        raise ValueError("Choose a DNS mode.")
    if mode == "automatic":
        return {"mode": mode, "servers": [], "bootstrap": []}
    servers = data.get("servers")
    if not isinstance(servers, list) or not 1 <= len(servers) <= 8:
        raise ValueError("Enter between one and eight DNS servers.")
    normalized = list(dict.fromkeys(endpoint(value, mode) for value in servers))
    bootstrap = data.get("bootstrap", [])
    if not isinstance(bootstrap, list) or len(bootstrap) > 8 or not all(isinstance(x, str) for x in bootstrap):
        raise ValueError("Enter up to eight bootstrap IP addresses.")
    bootstrap = list(dict.fromkeys(server_ip(value) for value in bootstrap)) if mode != "plain" else []
    if mode != "plain" and not bootstrap:
        raise ValueError("Enter a bootstrap IP to resolve your encrypted DNS server's hostname.")
    return {"mode": mode, "servers": normalized, "bootstrap": bootstrap}


def proxy_config(settings):
    upstream = settings["servers"]
    if settings["mode"] == "plain":
        upstream = [f"[{ip}]:53" if ":" in ip else f"{ip}:53" for ip in upstream]
    config = {
        "listen-addrs": ["127.0.0.1"], "listen-ports": [53],
        "upstream": upstream, "cache": True, "cache-size": 262144,
        "timeout": "8s", "insecure": False, "hosts-file-enabled": True,
    }
    if settings["bootstrap"]:
        config["bootstrap"] = [f"[{ip}]:53" if ":" in ip else f"{ip}:53"
                               for ip in settings["bootstrap"]]
    # JSON is also valid YAML; no interpolated YAML or shell commands.
    return (json.dumps(config, indent=2) + "\n").encode()
