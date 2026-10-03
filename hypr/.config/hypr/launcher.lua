-- Start the persistent launcher in the environment of this Hyprland session.
hl.on("hyprland.start", function()
  hl.exec_cmd('"$HOME/.local/bin/launcher-start"')
end)

-- Reuse the short macOpen/macClose layer animations in animations.lua.
hl.layer_rule({
  name = "walker-launcher",
  match = { namespace = "^walker$" },
  animation = "popin 96%",
})
