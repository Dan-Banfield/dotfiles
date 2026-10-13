#!/usr/bin/env python3
"""Resident DNS menu; privileged work is confined to the installed helper."""

from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")
from pathlib import Path
import json
import shutil
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, Gio, GLib, Gtk
from gi.repository import Gtk4LayerShell as LayerShell
from model import MODES, MODE_LABELS, PRESETS, split_values, validate_settings

CONFIG_DIR = Path(__file__).resolve().parent
HELPER = Path("/usr/lib/dotfiles-dns/apply")
STATE = Path("/etc/dotfiles-dns/settings.json")
PROVIDERS = tuple(PRESETS) + ("Custom",)


def label(text, style, **options):
    widget = Gtk.Label(label=text, **options)
    widget.add_css_class(style)
    return widget


class DNSMenu(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="dev.dotfiles.DNSMenu",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        for name, description in (("background", "Warm the menu"), ("quit", "Stop the menu")):
            self.add_main_option(name, 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE, description, None)
        self.window = None
        self.busy = False
        self.closing = 0
        self.opening = 0
        self.populating = False

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.hold()
        self.build_window()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        if options.contains("quit"):
            self.quit()
        elif not options.contains("background"):
            self.activate()
        return 0

    def do_activate(self):
        if self.busy:
            return
        if self.window.get_visible() and not self.closing:
            self.dismiss()
        else:
            self.show_menu()

    def build_window(self):
        css = Gtk.CssProvider()
        css.load_from_path(str(CONFIG_DIR / "style.css"))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window = Gtk.ApplicationWindow(application=self, title="Change DNS")
        self.window.add_css_class("dns-window")
        self.window.set_decorated(False)
        self.window.connect("close-request", lambda _w: self.dismiss() or True)
        LayerShell.init_for_window(self.window)
        LayerShell.set_namespace(self.window, "dns-menu")
        LayerShell.set_layer(self.window, LayerShell.Layer.OVERLAY)
        LayerShell.set_keyboard_mode(self.window, LayerShell.KeyboardMode.EXCLUSIVE)
        LayerShell.set_exclusive_zone(self.window, -1)
        for edge in (LayerShell.Edge.TOP, LayerShell.Edge.BOTTOM, LayerShell.Edge.LEFT, LayerShell.Edge.RIGHT):
            LayerShell.set_anchor(self.window, edge, True)

        stage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        for setter in (stage.set_margin_top, stage.set_margin_bottom, stage.set_margin_start, stage.set_margin_end):
            setter(24)
        self.window.set_child(stage)
        self.revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_UP, transition_duration=230)
        stage.append(self.revealer)
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.panel.set_size_request(540, -1)
        self.panel.add_css_class("dns-panel")
        self.revealer.set_child(self.panel)

        header = Gtk.Box(spacing=12)
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, hexpand=True)
        titles.append(label("Change DNS", "heading", xalign=0))
        self.current = label("", "current", xalign=0)
        titles.append(self.current)
        header.append(titles)
        self.close_button = Gtk.Button(icon_name="window-close-symbolic", valign=Gtk.Align.START)
        self.close_button.add_css_class("close-button")
        self.close_button.set_tooltip_text("Close menu")
        self.close_button.connect("clicked", lambda _b: self.dismiss())
        header.append(self.close_button)
        self.panel.append(header)

        self.form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.panel.append(self.form)
        self.form.append(label("Connection type", "field-label", xalign=0))
        self.mode = Gtk.DropDown.new_from_strings(MODE_LABELS)
        self.mode.connect("notify::selected", self.mode_changed)
        self.form.append(self.mode)

        self.provider_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.provider_box.append(label("Provider", "field-label", xalign=0))
        self.provider = Gtk.DropDown.new_from_strings(PROVIDERS)
        self.provider.connect("notify::selected", self.provider_changed)
        self.provider_box.append(self.provider)
        self.form.append(self.provider_box)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE,
                               transition_duration=180, interpolate_size=True,
                               vhomogeneous=False)
        self.form.append(self.stack)
        self.editors = {}
        automatic = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        automatic.append(label("Use the DNS supplied by your current network.", "hint", xalign=0, wrap=True))
        self.stack.add_named(automatic, "automatic")
        fields = {
            "plain": ("DNS server IP addresses", "One IPv4 or IPv6 address per line."),
            "dot": ("TLS servers", "One hostname per line, optionally with :port. Default port: 853."),
            "doh": ("HTTPS endpoints", "One full https:// DNS endpoint per line."),
        }
        for mode, (title, hint) in fields.items():
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.append(label(title, "field-label", xalign=0))
            editor = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR, accepts_tab=False)
            editor.add_css_class("server-editor")
            editor.get_buffer().connect("changed", self.text_changed)
            scroll = Gtk.ScrolledWindow(min_content_height=72, max_content_height=100,
                                       propagate_natural_height=True, hscrollbar_policy=Gtk.PolicyType.NEVER)
            scroll.add_css_class("server-box")
            scroll.set_child(editor)
            box.append(scroll)
            box.append(label(hint, "hint", xalign=0, wrap=True))
            self.editors[mode] = editor
            self.stack.add_named(box, mode)

        self.bootstrap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.bootstrap_box.append(label("Bootstrap DNS IPs", "field-label", xalign=0))
        self.bootstrap = Gtk.Entry(placeholder_text="1.1.1.1, 1.0.0.1")
        self.bootstrap.connect("changed", self.text_changed)
        self.bootstrap_box.append(self.bootstrap)
        self.bootstrap_box.append(label("Used only to find the encrypted server's IP address.", "hint", xalign=0, wrap=True))
        self.form.append(self.bootstrap_box)

        self.note = label("Applies to system DNS. Use Automatic for VPN or private-network DNS.", "hint", xalign=0, wrap=True)
        self.note.set_max_width_chars(62)
        self.panel.append(self.note)
        self.message = label("", "message", xalign=0, wrap=True)
        self.message.set_max_width_chars(62)
        self.panel.append(self.message)

        footer = Gtk.Box(spacing=12)
        self.setup_button = Gtk.Button(label="Install DNS support")
        self.setup_button.add_css_class("secondary-button")
        self.setup_button.connect("clicked", self.install_backend)
        footer.append(self.setup_button)
        spacer = Gtk.Box(hexpand=True)
        footer.append(spacer)
        self.spinner = Gtk.Spinner()
        footer.append(self.spinner)
        self.apply_button = Gtk.Button(label="Apply DNS")
        self.apply_button.add_css_class("primary-button")
        self.apply_button.connect("clicked", self.apply_clicked)
        footer.append(self.apply_button)
        self.panel.append(footer)

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self.on_key)
        self.window.add_controller(keys)
        outside = Gtk.GestureClick()
        outside.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        outside.connect("released", self.outside_clicked)
        self.window.add_controller(outside)
        self.mode_changed()

    def mode_changed(self, *_args):
        mode = MODES[self.mode.get_selected()]
        self.stack.set_visible_child_name(mode)
        self.provider_box.set_visible(mode != "automatic")
        self.bootstrap_box.set_visible(mode in ("dot", "doh"))
        if not self.populating:
            self.provider_changed()

    def provider_changed(self, *_args):
        mode = MODES[self.mode.get_selected()]
        provider = PROVIDERS[self.provider.get_selected()]
        if self.populating or mode == "automatic" or provider == "Custom":
            return
        self.populating = True
        preset = PRESETS[provider]
        self.editors[mode].get_buffer().set_text("\n".join(preset[mode]))
        self.bootstrap.set_text(", ".join(preset["bootstrap"]))
        self.populating = False

    def text_changed(self, *_args):
        if not self.populating:
            self.provider.set_selected(len(PROVIDERS) - 1)

    def backend_ready(self):
        return HELPER.is_file() and shutil.which("dnsproxy") is not None

    def refresh_backend(self):
        ready = self.backend_ready()
        self.setup_button.set_visible(not ready)
        self.apply_button.set_sensitive(ready and not self.busy)
        return GLib.SOURCE_CONTINUE if self.window.get_visible() and not ready else GLib.SOURCE_REMOVE

    def show_menu(self):
        if self.closing:
            GLib.source_remove(self.closing)
            self.closing = 0
        self.message.remove_css_class("success")
        self.message.set_text("")
        settings = {"mode": "automatic", "servers": [], "bootstrap": []}
        try:
            if STATE.exists():
                settings = validate_settings(json.loads(STATE.read_text()))
        except (OSError, ValueError):
            self.message.set_text("The saved DNS settings could not be read.")
        mode = settings["mode"]
        self.populating = True
        self.mode.set_selected(MODES.index(mode))
        provider = next((name for name, preset in PRESETS.items()
                         if mode != "automatic" and validate_settings({"mode": mode,
                             "servers": preset[mode], "bootstrap": preset["bootstrap"]}) == settings), "Custom")
        self.provider.set_selected(PROVIDERS.index(provider))
        if mode != "automatic":
            self.editors[mode].get_buffer().set_text("\n".join(settings["servers"]))
            self.bootstrap.set_text(", ".join(settings["bootstrap"]))
        else:
            self.provider.set_selected(0)
        self.populating = False
        self.mode_changed()
        self.current.set_text("Current · " + MODE_LABELS[MODES.index(mode)].split(" · ")[0])
        self.window.present()
        self.refresh_backend()
        if not self.backend_ready():
            self.message.set_text("One-time setup is needed before you can apply DNS settings.")
        self.close_button.grab_focus()
        if not self.opening:
            self.opening = GLib.idle_add(self.reveal)

    def reveal(self):
        self.opening = 0
        self.window.add_css_class("dns-open")
        self.revealer.set_reveal_child(True)
        return GLib.SOURCE_REMOVE

    def dismiss(self):
        if self.busy or self.closing:
            return
        if self.opening:
            GLib.source_remove(self.opening)
            self.opening = 0
        self.window.remove_css_class("dns-open")
        self.revealer.set_reveal_child(False)
        self.closing = GLib.timeout_add(250, self.finish_close)

    def finish_close(self):
        self.window.set_visible(False)
        self.closing = 0
        return GLib.SOURCE_REMOVE

    def install_backend(self, _button):
        installer = CONFIG_DIR.parents[1] / "install.sh"
        if not installer.is_file() or not shutil.which("kitty"):
            self.message.set_text("Run sudo pacman -S --needed dnsproxy, then the dotfiles dns-menu/install.sh script.")
            return
        self.dismiss()
        def launch():
            try:
                Gio.Subprocess.new(["kitty", "--hold", "--title", "DNS setup", "bash", "-c",
                                    'sudo pacman -S --needed dnsproxy && bash "$1"', "dns-setup", str(installer)],
                                   Gio.SubprocessFlags.NONE)
            except GLib.Error as error:
                self.show_menu()
                self.message.set_text(str(error))
            return GLib.SOURCE_REMOVE
        GLib.timeout_add(270, launch)

    def apply_clicked(self, _button):
        mode = MODES[self.mode.get_selected()]
        buffer = self.editors[mode].get_buffer() if mode != "automatic" else None
        values = split_values(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)) if buffer else []
        try:
            settings = validate_settings({"mode": mode, "servers": values,
                                          "bootstrap": split_values(self.bootstrap.get_text())})
            process = Gio.Subprocess.new(["/usr/bin/pkexec", "--disable-internal-agent", str(HELPER), "--apply"],
                                         Gio.SubprocessFlags.STDIN_PIPE | Gio.SubprocessFlags.STDOUT_PIPE |
                                         Gio.SubprocessFlags.STDERR_PIPE)
        except (ValueError, GLib.Error) as error:
            self.message.set_text(str(error))
            return
        self.busy = True
        self.form.set_sensitive(False)
        self.apply_button.set_sensitive(False)
        self.close_button.set_sensitive(False)
        self.spinner.start()
        self.message.remove_css_class("success")
        self.message.set_text("Authenticate to apply your DNS settings…")
        # Release the overlay's keyboard grab so the system authentication
        # dialog is visible and can receive the password.
        self.window.remove_css_class("dns-open")
        self.revealer.set_reveal_child(False)
        self.window.set_visible(False)
        process.communicate_utf8_async(json.dumps(settings), None, self.applied)

    def applied(self, process, result):
        self.busy = False
        self.form.set_sensitive(True)
        self.close_button.set_sensitive(True)
        self.spinner.stop()
        self.refresh_backend()
        self.window.present()
        self.opening = GLib.idle_add(self.reveal)
        try:
            _ok, output, error = process.communicate_utf8_finish(result)
            if not process.get_successful():
                if process.get_exit_status() in (126, 127):
                    self.message.set_text("Authentication was cancelled or unavailable. DNS was not changed.")
                else:
                    self.message.set_text((error or "The DNS change could not be applied.").strip()[:800])
                return
            settings = json.loads(output)["settings"]
            self.current.set_text("Current · " + MODE_LABELS[MODES.index(settings["mode"])].split(" · ")[0])
            self.message.add_css_class("success")
            self.message.set_text("Network DNS restored." if settings["mode"] == "automatic" else "DNS updated and tested.")
        except (GLib.Error, ValueError, KeyError) as error:
            self.message.set_text(str(error))

    def on_key(self, _controller, keyval, _code, _modifiers):
        if keyval == Gdk.KEY_Escape:
            self.dismiss()
            return True
        return False

    def outside_clicked(self, _gesture, _count, x, y):
        widget = self.window.pick(x, y, Gtk.PickFlags.DEFAULT)
        while widget:
            if widget == self.panel:
                return
            widget = widget.get_parent()
        self.dismiss()


def main():
    if sys.argv[1:] == ["--check"]:
        css = Gtk.CssProvider()
        errors = []
        css.connect("parsing-error", lambda _p, _s, error: errors.append(str(error)))
        css.load_from_path(str(CONFIG_DIR / "style.css"))
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("DNS menu: GTK4 layer-shell and stylesheet ready.")
        print("DNS backend: " + ("installed" if HELPER.is_file() else "run dns-menu/install.sh"))
        return 0
    return DNSMenu().run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
