#!/usr/bin/env python3
"""A resident GTK4 layer-shell session menu, activated through GApplication."""

# Layer-shell must be loaded before GTK's Wayland client, per its Python API.
from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")

from pathlib import Path
import shutil
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, Gio, GLib, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from actions import ACTIONS, BY_KEY, available, command_for

CONFIG_DIR = Path(__file__).resolve().parent
APP_ID = "dev.dotfiles.SessionMenu"


def label(text, style, **kwargs):
    widget = Gtk.Label(label=text, **kwargs)
    widget.add_css_class(style)
    return widget


def icon(name, size=30):
    local_icon = CONFIG_DIR / "icons" / f"{name}.svg"
    if local_icon.is_file():
        image = Gtk.Image.new_from_gicon(
            Gio.FileIcon.new(Gio.File.new_for_path(str(local_icon))))
    else:
        image = Gtk.Image.new_from_icon_name(name)
    image.set_pixel_size(size)
    return image


class SessionMenu(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.add_main_option("background", 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Warm the menu without opening it", None)
        self.add_main_option("quit", 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Stop the resident menu", None)
        self.window = None
        self.closing = 0
        self.opening = 0
        self.pending_action = None
        self.selected_action = None

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
        if self.pending_action:
            return
        if self.window.get_visible() and not self.closing:
            self.dismiss()
        else:
            self.show_menu()

    def build_window(self):
        provider = Gtk.CssProvider()
        provider.load_from_path(str(CONFIG_DIR / "style.css"))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.window = Gtk.ApplicationWindow(application=self, title="Power Menu")
        self.window.add_css_class("session-menu-window")
        self.window.set_decorated(False)
        self.window.connect("close-request", self.on_close_request)
        LayerShell.init_for_window(self.window)
        LayerShell.set_namespace(self.window, "session-menu")
        LayerShell.set_layer(self.window, LayerShell.Layer.OVERLAY)
        LayerShell.set_keyboard_mode(self.window, LayerShell.KeyboardMode.EXCLUSIVE)
        LayerShell.set_exclusive_zone(self.window, -1)
        for edge in (LayerShell.Edge.TOP, LayerShell.Edge.BOTTOM,
                     LayerShell.Edge.LEFT, LayerShell.Edge.RIGHT):
            LayerShell.set_anchor(self.window, edge, True)

        stage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        stage.set_halign(Gtk.Align.CENTER)
        stage.set_valign(Gtk.Align.CENTER)
        for setter in (stage.set_margin_start, stage.set_margin_end,
                       stage.set_margin_top, stage.set_margin_bottom):
            setter(32)
        self.window.set_child(stage)

        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.revealer.set_transition_duration(240)
        stage.append(self.revealer)

        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.panel.add_css_class("session-panel")
        self.revealer.set_child(self.panel)

        header = Gtk.Box(spacing=12)
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        titles.set_hexpand(True)
        titles.append(label("Power Menu", "heading", xalign=0))
        header.append(titles)
        self.close_button = Gtk.Button()
        self.close_button.add_css_class("close-button")
        self.close_button.set_valign(Gtk.Align.START)
        self.close_button.set_child(icon("window-close-symbolic", 18))
        self.close_button.set_tooltip_text("Close menu")
        self.close_button.connect("clicked", lambda _button: self.dismiss())
        header.append(self.close_button)
        self.panel.append(header)

        self.stack = Gtk.Stack()
        self.stack.set_hhomogeneous(True)
        self.stack.set_vhomogeneous(False)
        self.stack.set_interpolate_size(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        self.panel.append(self.stack)
        self.build_actions()
        self.build_confirmation()
        self.build_error()

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self.on_key)
        self.window.add_controller(keys)
        outside = Gtk.GestureClick()
        outside.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        outside.connect("released", self.on_pointer_release)
        self.window.add_controller(outside)

    def build_actions(self):
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.buttons = {}
        for index, action in enumerate(ACTIONS):
            button = Gtk.Button()
            button.add_css_class("action-card")
            button.add_css_class(f"card-{index + 1}")
            button.connect("clicked", lambda _button, key=action.key: self.choose(key))
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
            top = Gtk.Box()
            image = icon(action.icon)
            image.add_css_class("action-icon")
            image.set_hexpand(True)
            image.set_halign(Gtk.Align.START)
            top.append(image)
            content.append(top)
            content.append(label(action.label, "action-title", xalign=0))
            button.set_child(content)
            grid.attach(button, index % 3, index // 3, 1, 1)
            self.buttons[action.key] = button
        self.stack.add_named(grid, "actions")

    def build_confirmation(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.add_css_class("confirmation")
        self.confirm_icon = icon("system-shutdown-symbolic", 42)
        self.confirm_icon.add_css_class("confirm-icon")
        box.append(self.confirm_icon)
        self.confirm_title = label("", "confirm-title")
        box.append(self.confirm_title)
        self.confirm_description = label("", "confirm-description", wrap=True)
        self.confirm_description.set_max_width_chars(48)
        box.append(self.confirm_description)
        row = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER)
        self.back_button = Gtk.Button(label="Go Back")
        self.back_button.add_css_class("secondary-button")
        self.back_button.connect("clicked", lambda _button: self.back())
        row.append(self.back_button)
        self.confirm_button = Gtk.Button()
        self.confirm_button.add_css_class("primary-button")
        self.confirm_button.connect("clicked", lambda _button: self.confirm())
        row.append(self.confirm_button)
        box.append(row)
        self.stack.add_named(box, "confirm")

    def build_error(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.add_css_class("confirmation")
        box.append(icon("dialog-information-symbolic", 36))
        box.append(label("That action couldn’t be completed", "confirm-title"))
        self.error_description = label("", "confirm-description", wrap=True)
        self.error_description.set_max_width_chars(58)
        box.append(self.error_description)
        back = Gtk.Button(label="Go Back", halign=Gtk.Align.CENTER)
        back.add_css_class("secondary-button")
        back.connect("clicked", lambda _button: self.back())
        box.append(back)
        self.stack.add_named(box, "error")

    def refresh_actions(self):
        for action in ACTIONS:
            button = self.buttons[action.key]
            enabled = available(action.key)
            button.set_sensitive(enabled)

    def show_menu(self, error=None):
        if self.closing:
            GLib.source_remove(self.closing)
            self.closing = 0
        self.refresh_actions()
        self.selected_action = None
        self.confirm_button.set_sensitive(True)
        self.stack.set_visible_child_name("error" if error else "actions")
        if error:
            self.error_description.set_text(error[:400])
        self.window.present()
        self.close_button.grab_focus()
        if not self.opening:
            self.opening = GLib.idle_add(self.reveal)

    def reveal(self):
        self.opening = 0
        self.window.add_css_class("session-open")
        self.revealer.set_reveal_child(True)
        return GLib.SOURCE_REMOVE

    def dismiss(self, action=None):
        if self.closing:
            return
        if self.opening:
            GLib.source_remove(self.opening)
            self.opening = 0
        self.pending_action = action
        self.window.remove_css_class("session-open")
        self.revealer.set_reveal_child(False)
        self.closing = GLib.timeout_add(260, self.finish_close)

    def finish_close(self):
        self.closing = 0
        self.window.set_visible(False)
        action, self.pending_action = self.pending_action, None
        if action:
            self.run_action(action)
        return GLib.SOURCE_REMOVE

    def choose(self, key):
        if self.closing or not available(key):
            return
        action = BY_KEY[key]
        if action.confirm:
            self.selected_action = key
            self.confirm_icon.set_from_icon_name(action.icon)
            self.confirm_title.set_text(f"{action.label}?")
            self.confirm_description.set_text(action.confirm)
            self.confirm_button.set_label(action.label)
            self.confirm_button.set_sensitive(True)
            self.stack.set_visible_child_name("confirm")
            self.back_button.grab_focus()
        else:
            self.dismiss(key)

    def confirm(self):
        if self.selected_action and not self.closing:
            self.confirm_button.set_sensitive(False)
            self.dismiss(self.selected_action)

    def back(self):
        if self.closing:
            return
        self.selected_action = None
        self.stack.set_visible_child_name("actions")
        self.close_button.grab_focus()

    def run_action(self, key):
        # An installed UWSM binary does not imply it manages this login.
        if key == "logout" and (uwsm := shutil.which("uwsm")):
            try:
                check = Gio.Subprocess.new([uwsm, "check", "is-active"],
                                           Gio.SubprocessFlags.STDOUT_SILENCE |
                                           Gio.SubprocessFlags.STDERR_SILENCE)
                check.wait_async(None, self.session_checked)
            except GLib.Error:
                self.spawn_action(key, uwsm_active=False)
            return
        self.spawn_action(key)

    def session_checked(self, process, result):
        try:
            process.wait_finish(result)
            active = process.get_successful()
        except GLib.Error:
            active = False
        self.spawn_action("logout", uwsm_active=active)

    def spawn_action(self, key, uwsm_active=True):
        try:
            process = Gio.Subprocess.new(command_for(key, uwsm_active=uwsm_active),
                                         Gio.SubprocessFlags.STDOUT_SILENCE |
                                         Gio.SubprocessFlags.STDERR_PIPE)
            process.communicate_utf8_async(None, None, self.action_finished, key)
        except (GLib.Error, RuntimeError) as error:
            self.show_menu(str(error))

    def action_finished(self, process, result, key):
        try:
            _ok, _stdout, stderr = process.communicate_utf8_finish(result)
            if not process.get_successful():
                message = (stderr or "").strip() or f"{BY_KEY[key].label} was declined by the system."
                print(f"session-menu: {message}", file=sys.stderr)
                self.show_menu(message)
        except GLib.Error as error:
            self.show_menu(str(error))

    def on_key(self, _controller, keyval, _keycode, _modifiers):
        if keyval == Gdk.KEY_Escape:
            if self.stack.get_visible_child_name() == "actions":
                self.dismiss()
            else:
                self.back()
            return True
        if self.stack.get_visible_child_name() == "actions" and Gdk.KEY_1 <= keyval <= Gdk.KEY_6:
            self.choose(ACTIONS[keyval - Gdk.KEY_1].key)
            return True
        return False

    def on_pointer_release(self, _gesture, _count, x, y):
        widget = self.window.pick(x, y, Gtk.PickFlags.DEFAULT)
        while widget is not None:
            if widget == self.panel:
                return
            widget = widget.get_parent()
        self.dismiss()

    def on_close_request(self, _window):
        self.dismiss()
        return True


def main():
    if sys.argv[1:] == ["--check"]:
        provider = Gtk.CssProvider()
        errors = []
        provider.connect("parsing-error", lambda _p, _s, error: errors.append(str(error)))
        provider.load_from_path(str(CONFIG_DIR / "style.css"))
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("GTK4 layer-shell and stylesheet are ready.")
        for action in ACTIONS:
            print(f"{action.label}: {'available' if available(action.key) else 'not installed'}")
        return 0
    return SessionMenu().run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
