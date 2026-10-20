#!/usr/bin/env bash
# Builds one zip per skill for upload to Claude.ai / Claude Desktop
# (Settings → Capabilities → Skills). Output: dist/<skill>.zip
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
dist="$root/dist"

rm -rf "$dist"
mkdir -p "$dist"

for skills in "$root"/plugins/*/skills; do
  for dir in "$skills"/*/; do
    name="$(basename "$dir")"
    if [[ ! -f "$dir/SKILL.md" ]]; then
      echo "skip $name (no SKILL.md)" >&2
      continue
    fi
    (cd "$skills" && zip -qr "$dist/$name.zip" "$name")
    echo "built dist/$name.zip"
  done
done
