"""No network or root access: validate requests and exercise apply/rollback."""

from pathlib import Path
import configparser
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / ".config/dns-menu"))
import model

loader = SourceFileLoader("dns_backend", str(PACKAGE / "system/apply"))
spec = importlib.util.spec_from_loader(loader.name, loader)
backend = importlib.util.module_from_spec(spec)
loader.exec_module(backend)


class ValidationTests(unittest.TestCase):
    def test_presets_and_revalidation(self):
        for preset in model.PRESETS.values():
            for mode in ("plain", "dot", "doh"):
                with self.subTest(mode=mode, preset=preset):
                    settings = model.validate_settings({"mode": mode, "servers": preset[mode],
                                                        "bootstrap": preset["bootstrap"]})
                    self.assertEqual(model.validate_settings(settings), settings)
                    config = json.loads(model.proxy_config(settings))
                    self.assertFalse(config["insecure"])
                    self.assertNotIn("fallback", config)
                    self.assertEqual(config["listen-addrs"], ["127.0.0.1"])

    def test_custom_tls_and_ipv6(self):
        settings = model.validate_settings({"mode": "dot", "servers": ["DNS.Example.org:8853"],
                                            "bootstrap": ["2001:4860:4860::8888"]})
        self.assertEqual(settings["servers"], ["tls://dns.example.org:8853"])
        self.assertEqual(json.loads(model.proxy_config(settings))["bootstrap"], ["[2001:4860:4860::8888]:53"])
        plain = model.validate_settings({"mode": "plain", "servers": ["2606:4700:4700::1111"]})
        self.assertEqual(json.loads(model.proxy_config(plain))["upstream"], ["[2606:4700:4700::1111]:53"])

    def test_unsafe_or_wrong_transport_requests(self):
        bad = [
            {"mode": "doh", "servers": ["http://dns.example/dns-query"], "bootstrap": ["1.1.1.1"]},
            {"mode": "doh", "servers": ["https://user:password@dns.example/dns-query"], "bootstrap": ["1.1.1.1"]},
            {"mode": "doh", "servers": ["file:///etc/passwd"], "bootstrap": ["1.1.1.1"]},
            {"mode": "doh", "servers": ["https://dns.example:70000/dns-query"], "bootstrap": ["1.1.1.1"]},
            {"mode": "doh", "servers": ["https://dns.example/dns-query"], "bootstrap": ["127.0.0.1"]},
            {"mode": "dot", "servers": ["tls://dns.example/path"], "bootstrap": ["1.1.1.1"]},
            {"mode": "dot", "servers": ["tls://dns.example"], "bootstrap": []},
            {"mode": "plain", "servers": ["0.0.0.0"]},
            {"mode": "plain", "servers": ["1.1.1.1\n; touch /tmp/no"]},
            {"mode": "plain", "servers": ["dns.example"]},
            {"mode": "plain", "servers": ["1.1.1.1"] * 9},
            {"mode": "automatic", "command": "anything"},
        ]
        for settings in bad:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                model.validate_settings(settings)


class ReloadSyntaxTests(unittest.TestCase):
    @unittest.skipUnless(Path("/usr/bin/nmcli").is_file(), "nmcli is not installed")
    def test_reload_flags_are_accepted_by_installed_nmcli(self):
        # Exercise the real argument parser without reaching NetworkManager.
        # A private, nonexistent bus address prevents any live DNS changes.
        def without_system_bus(*args, **_options):
            with tempfile.TemporaryDirectory() as directory:
                process = subprocess.run(
                    args, capture_output=True, text=True, timeout=5,
                    env={"PATH": "/usr/bin", "LANG": "C.UTF-8",
                         "DBUS_SYSTEM_BUS_ADDRESS": f"unix:path={directory}/no-bus"},
                )
            self.assertNotEqual(process.returncode, 0)
            self.assertNotIn("extra argument", process.stderr)
            self.assertIn("failed to reload", process.stderr)
            return process

        with patch.object(backend, "run", side_effect=without_system_bus):
            backend.reload_dns()


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.paths = {"STATE": root / "settings.json", "PROXY": root / "proxy.yaml",
                      "NM_CONFIG": root / "NetworkManager/90-dotfiles-dns.conf", "RESOLV": root / "resolv.conf"}
        self.patches = patch.multiple(backend, **self.paths)
        self.patches.start()
        self.addCleanup(self.patches.stop)
        self.calls = []
        self.active = False
        self.enabled = False
        self.fail_probe = False
        self.fail_reload_once = False
        self.fail_directing = False
        self.probed = False
        self.paths["RESOLV"].write_text("nameserver 192.0.2.1\n")
        self.settings = model.validate_settings({"mode": "doh", "servers": ["https://dns.example/dns-query"],
                                                 "bootstrap": ["1.1.1.1"]})
        self.run_patch = patch.object(backend, "run", side_effect=self.fake_run)
        self.run_patch.start()
        self.addCleanup(self.run_patch.stop)
        self.probe_patch = patch.object(backend, "probe", side_effect=self.probe)
        self.probe_patch.start()
        self.addCleanup(self.probe_patch.stop)

    def fake_run(self, *args, check=True):
        self.calls.append(args)
        status = 0
        output = ""
        if args[0].endswith("NetworkManager"):
            output = "[main]\ndns=default\n"
        elif args[1] == "is-active":
            status = 0 if self.active else 3
        elif args[1] == "is-enabled":
            status = 0 if self.enabled else 1
        elif args[0].endswith("systemctl"):
            if args[1] in ("enable", "disable"):
                self.enabled = args[1] == "enable"
                if "--now" in args:
                    self.active = False
            elif args[1] in ("restart", "stop"):
                self.active = args[1] == "restart"
        elif args[0].endswith("nmcli"):
            if self.fail_reload_once:
                self.fail_reload_once = False
                raise RuntimeError("NetworkManager rejected the reload")
            if self.paths["NM_CONFIG"].exists() and not self.fail_directing:
                self.paths["RESOLV"].write_text("nameserver 127.0.0.1\n")
            else:
                self.paths["RESOLV"].write_text("nameserver 192.0.2.1\n")
        return subprocess.CompletedProcess(args, status, output, "")

    def probe(self):
        self.probed = True
        # New DNS cannot be redirected before this succeeds.
        if self.fail_probe:
            raise RuntimeError("Resolver test failed")

    def snapshot(self):
        return {name: path.read_bytes() if path.exists() else None
                for name, path in self.paths.items() if name != "RESOLV"}

    def test_success_and_automatic_restore(self):
        backend.apply(self.settings)
        self.assertTrue(self.probed and self.active and self.enabled)
        self.assertEqual(json.loads(self.paths["STATE"].read_text()), self.settings)
        self.assertIn(b"servers=127.0.0.1", self.paths["NM_CONFIG"].read_bytes())
        backend.apply(model.validate_settings({"mode": "automatic"}))
        self.assertFalse(self.active or self.enabled)
        self.assertFalse(self.paths["NM_CONFIG"].exists())
        self.assertEqual(self.paths["RESOLV"].read_text(), "nameserver 192.0.2.1\n")

    def test_probe_failure_does_not_redirect_dns(self):
        before = self.snapshot()
        self.fail_probe = True
        with self.assertRaisesRegex(RuntimeError, "Previous DNS settings were restored"):
            backend.apply(self.settings)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.active or self.enabled)
        self.assertNotIn("127.0.0.1", self.paths["RESOLV"].read_text())

    def test_failed_switch_restores_existing_choice(self):
        backend.apply(self.settings)
        before = self.snapshot()
        self.fail_reload_once = True
        other = model.validate_settings({"mode": "dot", "servers": ["dns.example:853"], "bootstrap": ["9.9.9.9"]})
        with self.assertRaisesRegex(RuntimeError, "Previous DNS settings were restored"):
            backend.apply(other)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.active and self.enabled)

    def test_ignored_resolver_change_rolls_back(self):
        before = self.snapshot()
        self.fail_directing = True
        with self.assertRaisesRegex(RuntimeError, "did not switch"):
            backend.apply(self.settings)
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_configuration_is_never_overwritten(self):
        self.paths["NM_CONFIG"].parent.mkdir()
        self.paths["NM_CONFIG"].write_text("# Somebody else's settings\n")
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "another setup"):
            backend.apply(self.settings)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.active or self.enabled)

    def test_other_dns_backend_is_left_untouched(self):
        before = self.snapshot()
        def other_backend(*args, **kwargs):
            return subprocess.CompletedProcess(args, 0, "[main]\ndns=systemd-resolved\n", "")
        with patch.object(backend, "run", side_effect=other_backend):
            with self.assertRaisesRegex(RuntimeError, "default DNS backend"):
                backend.apply(self.settings)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.probed)


if __name__ == "__main__":
    unittest.main()
