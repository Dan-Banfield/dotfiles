"""Session menu actions. Commands run only after a menu selection."""

from dataclasses import dataclass
import shutil


@dataclass(frozen=True)
class Action:
    key: str
    label: str
    description: str
    icon: str
    confirm: str = ""


ACTIONS = (
    Action("lock", "Lock", "Keep your apps open", "system-lock-screen-symbolic"),
    Action("sleep", "Sleep", "Pause this device", "weather-clear-night-symbolic"),
    Action("processes", "Processes", "View running processes", "utilities-system-monitor-symbolic"),
    Action("logout", "Log Out", "End this session", "system-log-out-symbolic",
           "Your open apps will close and you will return to the login screen."),
    Action("restart", "Restart", "Reboot this device", "view-refresh-symbolic",
           "Your open apps will close and this device will restart."),
    Action("poweroff", "Power Off", "Shut down this device", "system-shutdown-symbolic",
           "Your open apps will close and this device will shut down."),
)
BY_KEY = {action.key: action for action in ACTIONS}


def command_for(key, which=None, uwsm_active=True):
    """Return an argument list, never shell text or a forced system command."""
    which = which or shutil.which

    def program(name):
        path = which(name)
        if not path:
            raise RuntimeError(f"{name} is not available")
        return path

    if key == "lock":
        return [program("hyprlock"), "--grace", "0"]
    if key == "sleep":
        return [program("systemctl"), "suspend"]
    if key == "processes":
        return [program("kitty"), "--class", "session-processes", "--title",
                "Processes", "-e", program("htop")]
    if key == "logout":
        if uwsm_active and (path := which("uwsm")):
            return [path, "stop"]
        return [program("hyprctl"), "dispatch", "hl.dsp.exit()"]
    if key in ("restart", "poweroff"):
        return [program("systemctl"), "reboot" if key == "restart" else "poweroff"]
    raise ValueError(f"Unknown session action: {key}")


def available(key):
    try:
        command_for(key)
        return True
    except RuntimeError:
        return False
