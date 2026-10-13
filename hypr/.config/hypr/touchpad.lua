-- Fn+F6 emits XF86TouchpadToggle on this ASUS keyboard.
-- Use `hyprctl devices` to change this name on another laptop.
local name = "asup1200:00-093a:200a-touchpad"
local enabled = true

hl.device({ name = name, enabled = enabled })

local function set_enabled(value)
    enabled = value
    hl.device({ name = name, enabled = enabled })
    hl.notification.create({
        text = enabled and "Touchpad enabled" or "Touchpad disabled",
        timeout = 2000,
        icon = "ok",
    })
end

hl.bind("XF86TouchpadToggle", function() set_enabled(not enabled) end,
    { description = "Toggle touchpad", locked = true })
hl.bind("XF86TouchpadOn", function() set_enabled(true) end,
    { description = "Enable touchpad", locked = true })
hl.bind("XF86TouchpadOff", function() set_enabled(false) end,
    { description = "Disable touchpad", locked = true })
