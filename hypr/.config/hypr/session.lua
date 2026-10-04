-- Keep the session menu ready without displaying it at login.
hl.on("hyprland.start", function()
  hl.exec_cmd('"$HOME/.local/bin/session-menu" --background')
end)

-- The fullscreen backdrop fades; GTK animates the central panel and cards.
hl.layer_rule({
  name = "session-menu",
  match = { namespace = "^session-menu$" },
  animation = "fade",
})
