local function restore_wallpaper()
  hl.exec_cmd([[
    state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles"
    mkdir -p "$state_dir"
    exec "$HOME/.local/bin/wallpaper-set" --restore >"$state_dir/wallpaper-set.log" 2>&1
  ]])
end

hl.on("hyprland.start", restore_wallpaper)
hl.on("config.reloaded", restore_wallpaper)
