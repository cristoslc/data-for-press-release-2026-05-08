#!/usr/bin/env bash
set -euo pipefail
# Rebuild the public branch from .public-allowlist and push to GitHub.
# Only committed files from main are included — never untracked local files.
# The 11ty site is built fresh each time from site/ sources.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"
git checkout main

echo "Building 11ty site..."
cd "$ROOT/site"
npm install --quiet 2>/dev/null
npx @11ty/eleventy 2>&1
cd "$ROOT"

echo "Encrypting site..."
source "$ROOT/.env"
export PATH_PREFIX="/data-for-press-release-2026-05-08/"
node "$ROOT/site/encrypt-site.js" "$SITE_PASSPHRASE"

git branch -D public 2>/dev/null || true
git checkout --orphan public
git rm -rf --cached . 2>/dev/null || true

while IFS= read -r pattern; do
  [[ -z "$pattern" || "$pattern" =~ ^# ]] && continue
  for f in $(git ls-tree -r main --name-only); do
    [[ "$f" == $pattern ]] && git checkout main -- "$f" && break
  done
done < .public-allowlist

echo "Copying built site into public branch..."
cp -r "$ROOT/_site/"* ./
git add -A
git commit --quiet -m "public: whitelisted files + built site" 2>/dev/null || true
git checkout main
echo "Public branch ready. Push: git push github public:main --force"