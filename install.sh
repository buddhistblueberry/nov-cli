#!/usr/bin/env bash
# One-line install for Termux / Linux.
# Usage: bash install.sh
set -euo pipefail

echo "==> Installing system packages (python, fzf, less)…"
if command -v pkg >/dev/null 2>&1; then
  pkg install -y python fzf less
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update && sudo apt-get install -y python3 python3-pip fzf less
fi

echo "==> Installing nov-cli (editable)…"
pip install .

echo "==> Done. Try: nov-cli \"pride and prejudice\""
