#!/usr/bin/env bash
# Simple helper for pulling main and making a release tag from pyproject.toml.
# Usage:
#   ./release.sh tips
#   ./release.sh pull
#   ./release.sh release "Your tag message here"
#
# Notes:
# - Work on feature branches + PRs. Do not commit on main.
# - After merging a PR, update local with: ./release.sh pull
# - The tag comes from [project].version in pyproject.toml -> vX.Y.Z

set -euo pipefail  # stop on errors, unset vars, and broken pipes

cmd="${1:-tips}"

if [[ "$cmd" == "tips" ]]; then
  cat <<'TXT'
Flow tips:
- Do not commit on main. Use feature branches and PRs.
- After merging a PR to main, update local with: git pull --rebase origin main
- Releases are created by pushing tag vX.Y.Z (must match pyproject.toml version).

Commands:
- ./release.sh pull
    Pull main with rebase for a linear history.

- ./release.sh release "Short release message"
    Create annotated tag v<version> from pyproject.toml and push main + tag.
TXT
  exit 0
fi

if [[ "$cmd" == "pull" ]]; then
  git pull --rebase origin main
  exit 0
fi

if [[ "$cmd" == "release" ]]; then
  # Ensure we are on main and the tree is clean.
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$branch" != "main" ]]; then
    echo "Current branch is '$branch'. Switch to 'main' first." >&2
    exit 1
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working tree not clean. Commit or stash first." >&2
    exit 1
  fi

  # Read version from the [project] section in pyproject.toml.
  # awk explanation:
  # - FS="\"" splits on double quotes
  # - when inside [project], find the line with version = "X.Y.Z" and print the value
  ver="$(
    awk 'BEGIN{FS="\""}
      /^\[project\]/{p=1;next}
      /^\[/{p=0}
      p && $1 ~ /version[[:space:]]*=/ {print $2; exit}' pyproject.toml
  )"
  if [[ -z "${ver:-}" ]]; then
    echo "Version not found in pyproject.toml [project].version" >&2
    exit 1
  fi

  tag="v${ver}"
  msg="${2:-Release ${tag}}"   # pass a custom message in quotes if needed

  # Do not overwrite an existing tag.
  if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    echo "Tag ${tag} already exists." >&2
    exit 1
  fi

  # Create annotated tag and push.
  echo "Tagging ${tag} ..."
  git tag -a "${tag}" -m "${msg}"
  echo "Pushing main and ${tag} ..."
  git push origin main
  git push origin "${tag}"
  echo "Done: ${tag}"
  exit 0
fi

echo ${tag}
echo ${msg}
echo "Usage: $0 [tips|pull|release \"message\"]" >&2
exit 1
