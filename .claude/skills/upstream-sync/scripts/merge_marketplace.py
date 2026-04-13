#!/usr/bin/env python3
"""
Deterministic marketplace.json merger for fork sync.

Takes upstream's marketplace.json as the authoritative base and overlays
fork-specific entries. Prevents the duplicate entries that git's text-based
merge produces.

Usage:
    python3 merge_marketplace.py                    # Merge and stage
    python3 merge_marketplace.py --dry-run          # Preview without writing
    python3 merge_marketplace.py --exclude name1,name2  # Drop stale entries
"""

import json
import subprocess
import sys
from collections import Counter

MARKETPLACE_PATH = ".claude-plugin/marketplace.json"


def git_show(ref, path):
    """Read a file from a git ref."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error reading {ref}:{path}: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_args(argv):
    dry_run = "--dry-run" in argv
    exclude = set()
    for i, arg in enumerate(argv):
        if arg == "--exclude" and i + 1 < len(argv):
            exclude = {name.strip() for name in argv[i + 1].split(",")}
    return dry_run, exclude


def main():
    dry_run, exclude = parse_args(sys.argv)

    # Load both versions from git (not the working tree, which has conflict markers)
    upstream = json.loads(git_show("upstream/main", MARKETPLACE_PATH))
    ours = json.loads(git_show("HEAD", MARKETPLACE_PATH))

    upstream_names = {p["name"] for p in upstream["plugins"]}

    # Find fork-specific entries, deduplicated (first occurrence wins)
    seen = set()
    fork_entries = []
    for p in ours["plugins"]:
        name = p["name"]
        if name not in upstream_names and name not in seen and name not in exclude:
            fork_entries.append(p)
            seen.add(name)

    # Report
    print(f"Upstream:       {len(upstream['plugins'])} plugins")
    print(f"Fork-specific:  {len(fork_entries)} entries")

    if fork_entries:
        for entry in fork_entries:
            source = entry.get("source", {})
            url = source.get("url", source) if isinstance(source, dict) else source
            print(f"  + {entry['name']}: {url}")

    if exclude:
        print(f"Excluded:       {', '.join(sorted(exclude))}")

    # Build merged result: upstream base + fork entries, sorted
    all_plugins = upstream["plugins"] + fork_entries
    all_plugins.sort(key=lambda p: p["name"].lower())

    data = {k: v for k, v in upstream.items() if k != "plugins"}
    data["plugins"] = all_plugins

    # Validate
    names = [p["name"] for p in all_plugins]
    dupes = {n: c for n, c in Counter(names).items() if c > 1}

    if dupes:
        print(f"\nERROR: Duplicates found: {dupes}", file=sys.stderr)
        sys.exit(1)

    print(f"\nResult:         {len(all_plugins)} plugins, no duplicates")

    if dry_run:
        print(f"\n[dry-run] Would write to {MARKETPLACE_PATH}")
    else:
        with open(MARKETPLACE_PATH, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

        subprocess.run(["git", "add", MARKETPLACE_PATH], check=True)
        print(f"\nWritten and staged: {MARKETPLACE_PATH}")


if __name__ == "__main__":
    main()
