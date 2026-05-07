#!/usr/bin/env python3
"""
Deterministic marketplace.json regenerator.

Builds marketplace.json from two inputs:
  - upstream/main:.claude-plugin/marketplace.json  (authoritative base)
  - .claude-plugin/fork-additions.json             (arizonabay's additions)

Concatenates the plugin lists, sorts by name (case-insensitive), and writes
the result. No heuristics, no diffing — what's in fork-additions.json is what
gets added on top of upstream.

Usage:
    python3 merge_marketplace.py            # Regenerate and stage
    python3 merge_marketplace.py --dry-run  # Preview without writing
"""

import json
import subprocess
import sys
from collections import Counter

MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
MANIFEST_PATH = ".claude-plugin/fork-additions.json"


def merge_plugins(upstream, manifest):
    """Concatenate upstream + manifest entries, sorted by name (case-insensitive).

    Raises ValueError if any name appears more than once in the merged result.
    """
    merged = list(upstream) + list(manifest)
    names = [p["name"] for p in merged]
    dupes = sorted(n for n, c in Counter(names).items() if c > 1)
    if dupes:
        raise ValueError(f"Duplicate plugin names: {dupes}")
    merged.sort(key=lambda p: p["name"].lower())
    return merged


def git_show(ref, path):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error reading {ref}:{path}: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def main():
    dry_run = "--dry-run" in sys.argv

    upstream = json.loads(git_show("upstream/main", MARKETPLACE_PATH))
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    merged_plugins = merge_plugins(upstream["plugins"], manifest["plugins"])

    print(f"Upstream:    {len(upstream['plugins'])} plugins")
    print(f"Manifest:    {len(manifest['plugins'])} plugins")
    for p in manifest["plugins"]:
        source = p.get("source", "")
        url = source.get("url", source) if isinstance(source, dict) else source
        print(f"  + {p['name']}: {url}")
    print(f"Result:      {len(merged_plugins)} plugins")

    data = {k: v for k, v in upstream.items() if k != "plugins"}
    data["plugins"] = merged_plugins

    if dry_run:
        print(f"\n[dry-run] Would write to {MARKETPLACE_PATH}")
        return

    with open(MARKETPLACE_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    subprocess.run(["git", "add", MARKETPLACE_PATH], check=True)
    print(f"\nWritten and staged: {MARKETPLACE_PATH}")


if __name__ == "__main__":
    main()
