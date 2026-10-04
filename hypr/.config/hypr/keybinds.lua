-- Window and workspace shortcuts use native Hyprland actions.
-- Personal overrides take precedence: Super+Q closes, Super+Alt+arrows moves,
-- and Super+Alt+number sends a window without following it.

local function bind(keys, description, action, flags)
  flags = flags or {}
  flags.description = description
  hl.bind(keys, action, flags)
end

-- Windows
bind("CTRL + ALT + Delete", "Session menu", hl.dsp.exec_cmd('"$HOME/.local/bin/session-menu"'))
bind("SUPER + Q", "Close window", hl.dsp.window.close())
bind("SUPER + W", "Close window", hl.dsp.window.close())
bind("SUPER + V", "Toggle window floating/tiling", hl.dsp.window.float({ action = "toggle" }))

bind("SUPER + J", "Toggle window split", hl.dsp.layout("togglesplit"))
bind("SUPER + P", "Pseudo window", hl.dsp.window.pseudo())
bind("SUPER + F", "Full screen", hl.dsp.window.fullscreen({ mode = "fullscreen" }))
bind("SUPER + ALT + F", "Full width", hl.dsp.window.fullscreen({ mode = "maximized" }))

-- Focus
bind("SUPER + LEFT", "Focus on left window", hl.dsp.focus({ direction = "l" }))
bind("SUPER + RIGHT", "Focus on right window", hl.dsp.focus({ direction = "r" }))
bind("SUPER + UP", "Focus on above window", hl.dsp.focus({ direction = "u" }))
bind("SUPER + DOWN", "Focus on below window", hl.dsp.focus({ direction = "d" }))

-- Workspaces: physical number-row keys (1–9, then 0).
for workspace = 1, 10 do
  local key = "code:" .. tostring(workspace + 9)
  bind("SUPER + " .. key, "Switch to workspace " .. workspace, hl.dsp.focus({ workspace = tostring(workspace) }))
  bind("SUPER + SHIFT + " .. key, "Move window to workspace " .. workspace, hl.dsp.window.move({ workspace = tostring(workspace) }))
  bind("SUPER + ALT + " .. key, "Move window silently to workspace " .. workspace, hl.dsp.window.move({ workspace = tostring(workspace), follow = false }))
  bind("SUPER + SHIFT + ALT + " .. key, "Move window silently to workspace " .. workspace, hl.dsp.window.move({ workspace = tostring(workspace), follow = false }))
end

bind("SUPER + S", "Toggle scratchpad", hl.dsp.workspace.toggle_special("scratchpad"))
bind("SUPER + ALT + S", "Move window to scratchpad", hl.dsp.window.move({ workspace = "special:scratchpad", follow = false }))

bind("SUPER + TAB", "Next workspace", hl.dsp.focus({ workspace = "e+1" }))
bind("SUPER + SHIFT + TAB", "Previous workspace", hl.dsp.focus({ workspace = "e-1" }))
bind("SUPER + CTRL + TAB", "Former workspace", hl.dsp.focus({ workspace = "previous" }))

-- Move workspaces between monitors
bind("SUPER + SHIFT + ALT + LEFT", "Move workspace to left monitor", hl.dsp.workspace.move({ monitor = "l" }))
bind("SUPER + SHIFT + ALT + RIGHT", "Move workspace to right monitor", hl.dsp.workspace.move({ monitor = "r" }))
bind("SUPER + SHIFT + ALT + UP", "Move workspace to up monitor", hl.dsp.workspace.move({ monitor = "u" }))
bind("SUPER + SHIFT + ALT + DOWN", "Move workspace to down monitor", hl.dsp.workspace.move({ monitor = "d" }))

-- Move and swap windows
for _, direction in ipairs({ { "LEFT", "l" }, { "RIGHT", "r" }, { "UP", "u" }, { "DOWN", "d" } }) do
  bind("SUPER + ALT + " .. direction[1], "Move window " .. direction[1]:lower(), hl.dsp.window.move({ direction = direction[2] }))
end

bind("SUPER + SHIFT + LEFT", "Swap window to the left", hl.dsp.window.swap({ direction = "l" }))
bind("SUPER + SHIFT + RIGHT", "Swap window to the right", hl.dsp.window.swap({ direction = "r" }))
bind("SUPER + SHIFT + UP", "Swap window up", hl.dsp.window.swap({ direction = "u" }))
bind("SUPER + SHIFT + DOWN", "Swap window down", hl.dsp.window.swap({ direction = "d" }))

-- Raise the focused window after cycling, including floating windows.
bind("ALT + TAB", "Focus on next window", function()
  hl.dispatch(hl.dsp.window.cycle_next())
  hl.dispatch(hl.dsp.window.bring_to_top())
end)
bind("ALT + SHIFT + TAB", "Focus on previous window", function()
  hl.dispatch(hl.dsp.window.cycle_next({ next = false }))
  hl.dispatch(hl.dsp.window.bring_to_top())
end)

bind("CTRL + ALT + TAB", "Focus on next monitor", hl.dsp.focus({ monitor = "+1" }))
bind("CTRL + ALT + SHIFT + TAB", "Focus on previous monitor", hl.dsp.focus({ monitor = "-1" }))

-- Resize with the physical -/= keys: normal 100px, Alt 25px, Ctrl 300px.
bind("SUPER + code:20", "Expand window left", hl.dsp.window.resize({ x = -100, y = 0, relative = true }))
bind("SUPER + code:21", "Shrink window left", hl.dsp.window.resize({ x = 100, y = 0, relative = true }))
bind("SUPER + SHIFT + code:20", "Shrink window up", hl.dsp.window.resize({ x = 0, y = -100, relative = true }))
bind("SUPER + SHIFT + code:21", "Expand window down", hl.dsp.window.resize({ x = 0, y = 100, relative = true }))

bind("SUPER + ALT + code:20", "Expand window left a little", hl.dsp.window.resize({ x = -25, y = 0, relative = true }))
bind("SUPER + ALT + code:21", "Shrink window left a little", hl.dsp.window.resize({ x = 25, y = 0, relative = true }))
bind("SUPER + SHIFT + ALT + code:20", "Shrink window up a little", hl.dsp.window.resize({ x = 0, y = -25, relative = true }))
bind("SUPER + SHIFT + ALT + code:21", "Expand window down a little", hl.dsp.window.resize({ x = 0, y = 25, relative = true }))

bind("SUPER + CTRL + code:20", "Expand window left a lot", hl.dsp.window.resize({ x = -300, y = 0, relative = true }))
bind("SUPER + CTRL + code:21", "Shrink window left a lot", hl.dsp.window.resize({ x = 300, y = 0, relative = true }))
bind("SUPER + CTRL + SHIFT + code:20", "Shrink window up a lot", hl.dsp.window.resize({ x = 0, y = -300, relative = true }))
bind("SUPER + CTRL + SHIFT + code:21", "Expand window down a lot", hl.dsp.window.resize({ x = 0, y = 300, relative = true }))

bind("SUPER + mouse_down", "Scroll active workspace forward", hl.dsp.focus({ workspace = "e+1" }))
bind("SUPER + mouse_up", "Scroll active workspace backward", hl.dsp.focus({ workspace = "e-1" }))

bind("SUPER + mouse:272", "Move window", hl.dsp.window.drag(), { mouse = true })
bind("SUPER + mouse:273", "Resize window", hl.dsp.window.resize(), { mouse = true })

-- Window groups (Alt+number stays assigned to silent workspace moves).
bind("SUPER + G", "Toggle window grouping", hl.dsp.group.toggle())
bind("SUPER + ALT + G", "Move active window out of group", hl.dsp.window.move({ out_of_group = true }))

bind("SUPER + ALT + TAB", "Next window in group", hl.dsp.group.next())
bind("SUPER + ALT + SHIFT + TAB", "Previous window in group", hl.dsp.group.prev())

bind("SUPER + CTRL + LEFT", "Move grouped window focus left", hl.dsp.group.prev())
bind("SUPER + CTRL + RIGHT", "Move grouped window focus right", hl.dsp.group.next())

bind("SUPER + ALT + mouse_down", "Next window in group", hl.dsp.group.next())
bind("SUPER + ALT + mouse_up", "Previous window in group", hl.dsp.group.prev())

-- Cursor zoom
bind("SUPER + CTRL + Z", "Zoom in", function()
  local zoom = hl.get_config("cursor.zoom_factor") or 1
  hl.config({ cursor = { zoom_factor = zoom + 1 } })
end)
bind("SUPER + CTRL + ALT + Z", "Reset zoom", function()
  hl.config({ cursor = { zoom_factor = 1 } })
end)

-- Keep the current application's commands configurable in hyprland.lua.
return function(programs)
  bind("SUPER + T", "Terminal", hl.dsp.exec_cmd(programs.terminal))
  bind("SUPER + E", "File manager", hl.dsp.exec_cmd(programs.file_manager))
  bind("SUPER + R", "App launcher", hl.dsp.exec_cmd(programs.launcher))
  -- Release bindings are shadowed when another Super shortcut is used.
  bind("SUPER + SUPER_L", "App launcher (tap left Super)", hl.dsp.exec_cmd(programs.launcher), { release = true })
  bind("SUPER + SUPER_R", "App launcher (tap right Super)", hl.dsp.exec_cmd(programs.launcher), { release = true })
  bind("SUPER + B", "Browser", hl.dsp.exec_cmd(programs.browser))
  bind("SUPER + M", "Log out", hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch 'hl.dsp.exit()'"))

  -- Existing media bindings; requires wpctl, brightnessctl, and playerctl.
  bind("XF86AudioRaiseVolume", "Volume up", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
  bind("XF86AudioLowerVolume", "Volume down", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true, repeating = true })
  bind("XF86AudioMute", "Mute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
  bind("XF86AudioMicMute", "Mute microphone", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })
  bind("XF86MonBrightnessUp", "Brightness up", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
  bind("XF86MonBrightnessDown", "Brightness down", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })
  bind("XF86AudioNext", "Next track", hl.dsp.exec_cmd("playerctl next"), { locked = true })
  bind("XF86AudioPause", "Pause/play", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
  bind("XF86AudioPlay", "Pause/play", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
  bind("XF86AudioPrev", "Previous track", hl.dsp.exec_cmd("playerctl previous"), { locked = true })
end
