---
name: upstream-sync
description: >
  Deterministic workflow for syncing this fork (arizonabay/claude-plugins) with
  upstream (anthropics/claude-plugins-official). Use when the user mentions syncing
  upstream, merging upstream changes, weekly sync, fork maintenance, or when
  responding to an "Upstream Changes Detected" GitHub issue.
---

# Upstream Fork Sync

This repo is arizonabay's fork of anthropics/claude-plugins-official. Upstream
regularly adds new plugins, external plugins, skills, bug fixes, and configuration
changes. This skill guides a weekly sync that pulls all of that into our fork while
preserving our fork-specific additions.

## What the sync brings in

The merge pulls everything upstream has changed: new plugin directories under
`plugins/` and `external_plugins/`, updated skills and commands within existing
plugins, changes to `.claude-plugin/marketplace.json` (the plugin registry), bug
fixes, documentation updates — the full diff.

## What we maintain on top

This fork exists so arizonabay can extend the plugin ecosystem with our own plugins,
customizations, and tooling while staying current with Anthropic's upstream. Our
fork-specific additions include:

- **Fork-specific marketplace entries** in `.claude-plugin/fork-additions.json`
  (e.g., `toolbelt`). The merge script overlays these onto upstream's
  marketplace.json each sync.
- **This skill** (`.claude/skills/upstream-sync/`)
- **GitHub Actions** (`.github/workflows/upstream-sync-check.yml`) that creates an
  issue when upstream has new commits
- **Any other plugins, skills, or config** we add over time

These are all preserved during sync. The merge brings in upstream's changes, and
git naturally keeps our additions that don't conflict.

## Workflow

### 1. Pre-flight

Verify before starting:

```bash
git status                 # Working tree must be clean
git branch --show-current  # Must be on main
git remote -v              # Must have 'upstream' pointing to anthropics/claude-plugins-official
```

Fetch the latest upstream:

```bash
git fetch upstream
```

### 2. Analyze what's incoming

Show the user what changed before touching anything:

```bash
git log --oneline main..upstream/main | wc -l   # How many commits
git log --oneline main..upstream/main            # What changed
```

Summarize for the user: new plugins added, plugins removed or renamed, updated
external plugins, bug fixes, config changes, etc. Wait for confirmation before
proceeding.

### 3. Merge

```bash
git merge --no-commit --no-ff upstream/main
```

Check for conflicts:

```bash
git diff --name-only --diff-filter=U
```

- **No conflicts**: proceed to verification (step 5). This is the happy path — new
  plugins, skills, and external_plugins all come in cleanly via the merge.
- **marketplace.json conflicts**: resolve with the merge script (step 4). This is
  the most common conflict because both sides add entries to the same sorted JSON
  array. Do NOT manually edit conflict markers — that's how duplicates happen.
- **Other file conflicts**: resolve those normally with standard git tools.

### 4. Regenerate marketplace.json

Whether or not the merge produced a conflict in `marketplace.json`, regenerate
it from the deterministic sources. The script reads `upstream/main`'s copy
directly from the git ref and overlays our manifest — conflict markers in the
working tree are ignored.

```bash
python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py
```

The script reports:
- Upstream plugin count
- Manifest plugin count + each entry it's adding
- Final merged count

It writes `.claude-plugin/marketplace.json` and runs `git add`. If a duplicate
name appears in both upstream and the manifest, the script aborts — that means
upstream just adopted a plugin name we were also using; remove it from
`.claude-plugin/fork-additions.json` and re-run.

#### Adding a fork-specific plugin

To add a new arizonabay plugin to the marketplace:

1. Append the entry to `.claude-plugin/fork-additions.json`
2. Run `python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py`
3. Commit both files

### 5. Verify

Before committing, confirm everything is clean:

```bash
# No unresolved conflicts
git diff --name-only --diff-filter=U

# Review what the merge brings in
git diff --cached --stat

# Validate marketplace.json specifically
python3 -c "
import json
from collections import Counter
d = json.load(open('.claude-plugin/marketplace.json'))
names = [p['name'] for p in d['plugins']]
dupes = {n: c for n, c in Counter(names).items() if c > 1}
assert not dupes, f'Duplicates: {dupes}'
print(f'{len(names)} plugins, no duplicates')
"
```

### 6. Commit

Commit the merge with a message following this pattern:

```
Merge branch 'upstream/main' into main

Sync with upstream: <N> new commits bringing <brief summary of notable changes>.
<Any cleanup notes if applicable.>
```

### 7. Post-merge

- Push to origin when the user is ready
- The `upstream-sync-check` workflow runs on push to `main` and auto-closes
  any open "Upstream Changes Detected" issues once drift is gone — no manual
  `gh issue close` needed
