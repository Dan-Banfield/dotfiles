hl.config({ animations = { enabled = true } })

-- 1.0 = normal; 0.8 = quicker; 1.2 = slower.
local duration_scale = 1

hl.curve("macOpen", {
  type = "bezier", points = { { 0.16, 1.0 }, { 0.30, 1.0 } },
})

hl.curve("macWindowOpen", {
  type = "bezier", points = { { 0.30, 0.0 }, { 0.25, 1.0 } },
})
hl.curve("macClose", {
  type = "bezier", points = { { 0.40, 0.0 }, { 1.0, 1.0 } },
})
hl.curve("macMove", {
  type = "bezier", points = { { 0.25, 0.10 }, { 0.25, 1.0 } },
})
hl.curve("macSpaces", {
  type = "bezier", points = { { 0.42, 0.0 }, { 0.58, 1.0 } },
})
hl.curve("macFade", {
  type = "bezier", points = { { 0.25, 0.0 }, { 0.30, 1.0 } },
})

local function animate(leaf, ms, curve, style)
  hl.animation({
    leaf = leaf, enabled = true,
    speed = ms / 100 * duration_scale,
    bezier = curve, style = style,
  })
end

animate("global",      250, "macMove")
animate("windows",     260, "macMove",  "popin 95%")
animate("windowsIn",   450, "macWindowOpen", "popin 94%")
animate("windowsOut",  180, "macClose", "popin 96%")
animate("windowsMove", 300, "macMove")

animate("fade",        180, "macFade")
animate("fadeIn",      350, "macWindowOpen")
animate("fadeOut",     150, "macClose")
animate("fadeShadow",  180, "macFade")
animate("fadeDim",     180, "macFade")
hl.animation({ leaf = "fadeSwitch", enabled = false })

animate("layers",        220, "macOpen",  "popin 98%")
animate("layersIn",      220, "macOpen",  "popin 98%")
animate("layersOut",     140, "macClose", "popin 98%")
animate("fadeLayers",    160, "macFade")
animate("fadeLayersIn",  160, "macFade")
animate("fadeLayersOut", 120, "macClose")
animate("fadePopups",    150, "macFade")
animate("fadePopupsIn",  150, "macFade")
animate("fadePopupsOut", 100, "macClose")

for _, leaf in ipairs({
  "workspaces", "workspacesIn", "workspacesOut",
  "specialWorkspace", "specialWorkspaceIn", "specialWorkspaceOut",
}) do
  animate(leaf, 550, "macSpaces", "slide")
end

animate("border",     180, "macFade")
animate("zoomFactor", 300, "macMove")
animate("fadeDpms",   250, "macFade")
hl.animation({ leaf = "borderangle", enabled = false })
hl.animation({ leaf = "monitorAdded", enabled = false })
