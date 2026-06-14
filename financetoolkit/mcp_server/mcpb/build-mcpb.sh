#!/usr/bin/env bash
# Builds financetoolkit.mcpb and places it in dist/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/dist"

# Read version from the root pyproject.toml — single source of truth.
VERSION=$(python3 -c "
import tomllib
with open('$REPO_ROOT/pyproject.toml', 'rb') as f:
    print(tomllib.load(f)['project']['version'])
")
echo "Version: $VERSION"

OUTPUT_FILE="$OUTPUT_DIR/financetoolkit.mcpb"

# Stamp version into the bundle files.
python3 -c "
import json, pathlib
p = pathlib.Path('$BUNDLE_DIR/manifest.json')
m = json.loads(p.read_text())
m['version'] = '$VERSION'
p.write_text(json.dumps(m, indent=2) + '\n')
"
python3 -c "
import re, pathlib
p = pathlib.Path('$BUNDLE_DIR/pyproject.toml')
p.write_text(re.sub(r'(?m)^version = \".*\"', 'version = \"$VERSION\"', p.read_text()))
"

mkdir -p "$OUTPUT_DIR"

cd "$BUNDLE_DIR"
mcpb pack .
BUNDLE_FILE=$(ls "$BUNDLE_DIR"/*.mcpb 2>/dev/null | head -1)
mv "$BUNDLE_FILE" "$OUTPUT_FILE"

echo ""
echo "Bundle written to $OUTPUT_FILE"
echo ""
echo "To install: open $OUTPUT_FILE with Claude Desktop."
echo "To publish: attach $OUTPUT_FILE to a GitHub release."
