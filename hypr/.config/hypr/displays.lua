-- Display layout: https://wiki.hypr.land/configuring/core/monitors/

-- Use automatic settings for other connected displays
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})

-- Built-in laptop display. This rule is also used when restoring the screen.
local laptop = {
    output   = "eDP-1",
    disabled = false,
    mode     = "1920x1080@60",
    position = "0x0",
    scale    = 1.00,
}
hl.monitor(laptop)

local displays = {}
local laptop_disabled = false

local function external_active(exclude)
    for _, monitor in ipairs(hl.get_monitors()) do
        local name = monitor.name
        if name ~= exclude and monitor.dpms_status
            and (name:match("^HDMI%-") or name:match("^DP%-")) then
            return true
        end
    end
    return false
end

local function notice(text, icon)
    hl.notification.create({ text = text, timeout = 3000, icon = icon or "ok" })
end

local function restore_laptop()
    laptop_disabled = false
    hl.monitor(laptop)
end

-- Called by the launcher's desktop entry through hyprctl eval.
function displays.toggle_laptop()
    local laptop_active = false
    for _, monitor in ipairs(hl.get_monitors()) do
        if monitor.name == laptop.output then
            laptop_active = true
            break
        end
    end

    if not laptop_active then
        restore_laptop()
        notice("Laptop display enabled")
    elseif external_active() then
        laptop_disabled = true
        hl.monitor({ output = laptop.output, disabled = true })
        notice("Laptop display disabled — using the external display")
    else
        notice("Connect and turn on an HDMI or DisplayPort display first", "warning")
    end
end

-- Recover automatically when the last external screen is unplugged.
-- The removed output can still be in the monitor list during this event.
hl.on("monitor.removed", function(monitor)
    if laptop_disabled and monitor.name ~= laptop.output
        and not external_active(monitor.name) then
        restore_laptop()
        notice("External display disconnected — laptop display restored")
    end
end)

return displays
