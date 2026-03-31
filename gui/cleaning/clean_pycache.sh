#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "-n" || "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Cleaning Python cache under: ${ROOT_DIR}"

if [[ ${DRY_RUN} -eq 1 ]]; then
  echo "[DRY RUN] Targets:"
  find "${ROOT_DIR}" -type d -name '__pycache__' -print
  find "${ROOT_DIR}" -type f -name '*.pyc' -print
  echo "Dry-run complete. No files were deleted."
  exit 0
fi

find "${ROOT_DIR}" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "${ROOT_DIR}" -type f -name '*.pyc' -delete

echo "Cache cleanup complete."
