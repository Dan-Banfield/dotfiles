hl.on("hyprland.start", function()
    hl.exec_cmd('"$HOME/.local/bin/change-dns" --background')
end)

hl.layer_rule({
    name = "dns-menu",
    match = { namespace = "^dns-menu$" },
    animation = "fade",
})
