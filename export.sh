#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
GODOT="/Applications/Godot.app/Contents/MacOS/Godot"
EXPORT_PRESET="Web"
EXPORT_PATH="./export/index.html"
DEPLOY_BRANCH="gh-pages"

# Web export files served from gh-pages root
EXPORT_FILES=(
    index.html
    index.js
    index.wasm
    index.pck
    index.icon.png
    index.png
    index.apple-touch-icon.png
    index.audio.worklet.js
    index.audio.position.worklet.js
    coi-serviceworker.js
)

cd "$PROJECT_DIR"

# 1. Export
echo "==> Exporting Godot project for web..."
"$GODOT" --headless --export-release "$EXPORT_PRESET" "$EXPORT_PATH" --path "$PROJECT_DIR"
echo "==> Export done."

# 2. Switch to gh-pages
CURRENT_BRANCH="$(git branch --show-current)"
echo "==> Switching to $DEPLOY_BRANCH..."
git stash --include-untracked -q 2>/dev/null || true
git checkout "$DEPLOY_BRANCH"

# 3. Copy export files to root
echo "==> Copying export files..."
for f in "${EXPORT_FILES[@]}"; do
    if [ -f "export/$f" ]; then
        cp -f "export/$f" .
    fi
done

# 4. Commit & push
if git diff --quiet && git diff --cached --quiet; then
    echo "==> No changes to deploy."
else
    git add "${EXPORT_FILES[@]}"
    git commit -m "deploy: update web export"
    git push origin "$DEPLOY_BRANCH"
    echo "==> Deployed to $DEPLOY_BRANCH."
fi

# 5. Switch back
echo "==> Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"
git stash pop -q 2>/dev/null || true

echo "==> Done!"
