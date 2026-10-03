-- Display layout: https://wiki.hypr.land/configuring/core/monitors/

-- Use automatic settings for other connected displays
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})

-- Built-in laptop display
hl.monitor({
    output   = "eDP-1",
    mode     = "1920x1080@60",
    position = "0x0",
    scale    = 1.00,
})
