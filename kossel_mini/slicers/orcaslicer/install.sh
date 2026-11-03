#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEXTURE="$HERE/kossel_dragon_burner_bed.svg"

if [ -n "${1:-}" ]; then
  ORCA_DIR="$1"
elif [ -d "$HOME/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer" ]; then
  ORCA_DIR="$HOME/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer"
elif [ -d "$HOME/.config/OrcaSlicer" ]; then
  ORCA_DIR="$HOME/.config/OrcaSlicer"
else
  echo "Pasta de configuração do OrcaSlicer não encontrada. Passe o caminho como argumento." >&2
  exit 1
fi

USER_DIR="${ORCA_USER_DIR:-$ORCA_DIR/user/default}"
mkdir -p "$USER_DIR/machine" "$USER_DIR/process"

install_preset() {
  local source="$1" kind="$2" base_id="$3"
  local name
  name="$(basename "$source" .json)"
  python3 - "$source" "$USER_DIR/$kind/$name.json" "$TEXTURE" <<'PY'
import json, sys
source, target, texture = sys.argv[1:4]
preset = json.load(open(source, encoding="utf-8"))
if "bed_custom_texture" in preset:
    preset["bed_custom_texture"] = texture
json.dump(preset, open(target, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
PY
  printf 'sync_info = update\nuser_id = \nsetting_id = \nbase_id = %s\nupdated_time = %s\n' \
    "$base_id" "$(date +%s)" > "$USER_DIR/$kind/$name.info"
  echo "  $kind/$name"
}

echo "Instalando em $USER_DIR"
for preset in "$HERE"/machine/*.json; do install_preset "$preset" machine GM001; done
for preset in "$HERE"/process/*.json; do install_preset "$preset" process GP004; done
echo "Textura da mesa: $TEXTURE"
echo "Reinicie o OrcaSlicer para carregar os perfis."
