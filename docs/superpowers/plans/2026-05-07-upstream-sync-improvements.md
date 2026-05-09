# Upstream Sync Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate manual cleanup during upstream syncs by replacing the marketplace.json merge heuristic with a manifest-driven regenerator, and stop the upstream-sync workflow from creating duplicate drift issues.

**Architecture:** Introduce `.claude-plugin/fork-additions.json` as the source of truth for arizonabay-added marketplace entries. Rewrite `merge_marketplace.py` to deterministically build `marketplace.json` from `upstream/main`'s copy plus the manifest — no diffing, no `--exclude` flag, no false positives. Modify the GitHub Actions workflow to upsert a single open drift issue and auto-close it on sync (triggered by both the weekly cron and pushes to `main`). Update SKILL.md and CLAUDE.md to document the new flow.

**Tech Stack:** Python 3 (stdlib only), GitHub Actions, `actions/github-script@v7`, Markdown.

**Tracking:** GitHub issue #23.

---

## File Structure

**Create:**
- `.claude-plugin/fork-additions.json` — manifest of arizonabay-added marketplace entries (1 entry today: `toolbelt`)
- `.claude/skills/upstream-sync/scripts/test_merge_marketplace.py` — stdlib `unittest` tests for the pure merge function

**Modify:**
- `.claude-plugin/marketplace.json` — regenerated; net content unchanged (toolbelt still present, sourced from manifest)
- `.claude/skills/upstream-sync/scripts/merge_marketplace.py` — full rewrite: split into pure `merge_plugins(upstream, manifest)` function + I/O wrapper; drop `--exclude` and the diff heuristic
- `.claude/skills/upstream-sync/SKILL.md` — replace step 4 ("Resolve marketplace.json conflicts") with the new regenerator flow; add a "Adding a fork-specific plugin" section
- `.github/workflows/upstream-sync-check.yml` — search for existing open drift issue and update/create/close as appropriate; add `push: branches: [main]` trigger
- `CLAUDE.md` — add a short "Adding a fork-specific plugin" subsection under "Development"

---

## Task 1: Create the manifest file

**Files:**
- Create: `.claude-plugin/fork-additions.json`

- [ ] **Step 1: Verify the current toolbelt entry**

Run:
```bash
python3 -c "
import json
d = json.load(open('.claude-plugin/marketplace.json'))
print(json.dumps([p for p in d['plugins'] if p['name'] == 'toolbelt'], indent=2))
"
```

Expected output:
```json
[
  {
    "name": "toolbelt",
    "description": "Developer productivity toolkit with steve/abel commands for complete issue-to-PR workflows",
    "category": "development",
    "source": {
      "source": "url",
      "url": "https://github.com/arizonabay/toolbelt.git"
    },
    "homepage": "https://github.com/arizonabay/toolbelt"
  }
]
```

If the entry differs (e.g., upstream has changed something), use whatever `marketplace.json` currently contains verbatim.

- [ ] **Step 2: Create `.claude-plugin/fork-additions.json`**

Content:
```json
{
  "plugins": [
    {
      "name": "toolbelt",
      "description": "Developer productivity toolkit with steve/abel commands for complete issue-to-PR workflows",
      "category": "development",
      "source": {
        "source": "url",
        "url": "https://github.com/arizonabay/toolbelt.git"
      },
      "homepage": "https://github.com/arizonabay/toolbelt"
    }
  ]
}
```

- [ ] **Step 3: Validate JSON**

Run:
```bash
python3 -c "import json; d = json.load(open('.claude-plugin/fork-additions.json')); assert len(d['plugins']) == 1 and d['plugins'][0]['name'] == 'toolbelt'; print('ok')"
```
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/fork-additions.json
git commit -m "Add fork-additions.json manifest with toolbelt entry

Source of truth for arizonabay-added marketplace entries. Used by
merge_marketplace.py to regenerate marketplace.json deterministically
during upstream syncs.

Refs #23"
```

---

## Task 2: Write failing tests for the new merge function

**Files:**
- Create: `.claude/skills/upstream-sync/scripts/test_merge_marketplace.py`

- [ ] **Step 1: Write the test file**

Create `.claude/skills/upstream-sync/scripts/test_merge_marketplace.py`:

```python
"""Tests for merge_marketplace.merge_plugins."""
import unittest

from merge_marketplace import merge_plugins


def _entry(name):
    return {"name": name, "source": f"url://{name}"}


class MergePluginsTests(unittest.TestCase):
    def test_concatenates_and_sorts_alphabetically(self):
        upstream = [_entry("apple"), _entry("cherry")]
        manifest = [_entry("banana")]
        result = merge_plugins(upstream, manifest)
        self.assertEqual([p["name"] for p in result], ["apple", "banana", "cherry"])

    def test_sort_is_case_insensitive(self):
        upstream = [_entry("Apple"), _entry("banana")]
        manifest = [_entry("Avocado")]
        result = merge_plugins(upstream, manifest)
        self.assertEqual([p["name"] for p in result], ["Apple", "Avocado", "banana"])

    def test_empty_manifest_returns_upstream_sorted(self):
        upstream = [_entry("zeta"), _entry("alpha")]
        result = merge_plugins(upstream, [])
        self.assertEqual([p["name"] for p in result], ["alpha", "zeta"])

    def test_duplicate_name_raises(self):
        upstream = [_entry("toolbelt")]
        manifest = [_entry("toolbelt")]
        with self.assertRaises(ValueError) as ctx:
            merge_plugins(upstream, manifest)
        self.assertIn("toolbelt", str(ctx.exception))

    def test_preserves_entry_fields_verbatim(self):
        upstream = [{"name": "a", "source": "x", "extra": 1}]
        manifest = [{"name": "b", "source": "y", "homepage": "h"}]
        result = merge_plugins(upstream, manifest)
        self.assertEqual(result[0], {"name": "a", "source": "x", "extra": 1})
        self.assertEqual(result[1], {"name": "b", "source": "y", "homepage": "h"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd .claude/skills/upstream-sync/scripts && python3 -m unittest test_merge_marketplace.py -v
```
Expected: tests fail with `ImportError` or `AttributeError` because `merge_plugins` does not yet exist as a separate function in `merge_marketplace.py`.

---

## Task 3: Rewrite `merge_marketplace.py`

**Files:**
- Modify: `.claude/skills/upstream-sync/scripts/merge_marketplace.py` (full rewrite)

- [ ] **Step 1: Replace the script content**

Overwrite `.claude/skills/upstream-sync/scripts/merge_marketplace.py` with:

```python
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
```

- [ ] **Step 2: Run the tests to verify they pass**

Run:
```bash
cd .claude/skills/upstream-sync/scripts && python3 -m unittest test_merge_marketplace.py -v
```
Expected: all 5 tests pass.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/upstream-sync/scripts/merge_marketplace.py .claude/skills/upstream-sync/scripts/test_merge_marketplace.py
git commit -m "Rewrite merge_marketplace.py as deterministic regenerator

Replaces the diff-against-upstream heuristic with a manifest-driven build:
marketplace.json = upstream/main + fork-additions.json, sorted. Drops the
--exclude flag and the false-positive cleanup that came with the old
approach.

Adds unit tests covering sort order, case-insensitivity, duplicate
detection, and field preservation. Tests use stdlib unittest only.

Refs #23"
```

---

## Task 4: Regenerate marketplace.json from new sources

**Files:**
- Modify: `.claude-plugin/marketplace.json` (regenerated; toolbelt entry now sourced from manifest)

- [ ] **Step 1: Capture pre-regeneration state**

Run:
```bash
python3 -c "
import json
d = json.load(open('.claude-plugin/marketplace.json'))
print(f'plugins: {len(d[\"plugins\"])}')
print(f'toolbelt present: {any(p[\"name\"] == \"toolbelt\" for p in d[\"plugins\"])}')
" > /tmp/marketplace-before.txt
cat /tmp/marketplace-before.txt
```
Expected: `plugins: 173`, `toolbelt present: True`

- [ ] **Step 2: Fetch upstream**

```bash
git fetch upstream
```

- [ ] **Step 3: Dry-run the regenerator**

```bash
python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py --dry-run
```
Expected: reports `Upstream: 172 plugins`, `Manifest: 1 plugins`, `+ toolbelt: ...`, `Result: 173 plugins`. No file write.

- [ ] **Step 4: Run for real**

```bash
python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py
```
Expected: same report; `marketplace.json` updated and staged.

- [ ] **Step 5: Verify content is unchanged in semantic terms**

Run:
```bash
python3 -c "
import json
from collections import Counter
d = json.load(open('.claude-plugin/marketplace.json'))
names = [p['name'] for p in d['plugins']]
dupes = {n: c for n, c in Counter(names).items() if c > 1}
assert not dupes, f'Duplicates: {dupes}'
assert 'toolbelt' in names, 'toolbelt missing'
assert len(names) == 173, f'expected 173, got {len(names)}'
print('ok')
"
```
Expected: `ok`

- [ ] **Step 6: Inspect the diff**

```bash
git diff --cached .claude-plugin/marketplace.json
```
Expected: either no diff (regenerated content matches existing) or only whitespace/ordering differences. If there are content changes to plugins other than `toolbelt`, STOP and investigate — the regenerator should produce semantically identical output.

- [ ] **Step 7: Commit (only if there are changes to commit)**

```bash
git diff --cached --quiet .claude-plugin/marketplace.json && echo "no changes — skip commit" || git commit -m "Regenerate marketplace.json from manifest

No semantic change. Toolbelt entry now sourced from fork-additions.json
via merge_marketplace.py instead of being maintained in marketplace.json
directly.

Refs #23"
```

---

## Task 5: Update the upstream-sync workflow

**Files:**
- Modify: `.github/workflows/upstream-sync-check.yml`

The workflow today: runs weekly, creates a new issue every time drift exists. New behavior: search for an open `Upstream Changes Detected` issue; if found update its body, else create. If no drift and an open issue exists, close it. Add `push: branches: [main]` trigger so post-sync close fires immediately.

- [ ] **Step 1: Replace the workflow file**

Overwrite `.github/workflows/upstream-sync-check.yml` with:

```yaml
name: Check Upstream Sync

on:
  schedule:
    # Every Monday at 9:00 AM UTC
    - cron: '0 9 * * 1'
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  check-upstream:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Add upstream remote and fetch
        run: |
          git remote add upstream https://github.com/anthropics/claude-plugins-official.git 2>/dev/null || true
          git fetch upstream main

      - name: Check for new commits
        id: check-commits
        run: |
          NEW_COMMITS=$(git log --oneline origin/main..upstream/main)

          if [ -z "$NEW_COMMITS" ]; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
            echo "No new commits found in upstream"
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
            echo "New commits found:"
            echo "$NEW_COMMITS"
            echo "$NEW_COMMITS" > /tmp/commits.txt
          fi

      - name: Upsert drift issue when changes exist
        if: steps.check-commits.outputs.has_changes == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const commits = fs.readFileSync('/tmp/commits.txt', 'utf8').trim();

            const issueBody = [
              '## Upstream Changes Detected',
              '',
              'New commits from anthropics/claude-plugins-official:',
              '',
              '```',
              commits,
              '```',
              '',
              '**Action Required**: Review changes and sync if needed.',
              '',
              `_Last updated: ${new Date().toISOString()}_`
            ].join('\n');

            const title = 'Upstream Changes Detected';
            const { data: existing } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              creator: 'app/github-actions',
              per_page: 100,
            });
            const open = existing.find(i => i.title === title);

            if (open) {
              await github.rest.issues.update({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: open.number,
                body: issueBody,
              });
              console.log(`Updated existing issue #${open.number}`);
            } else {
              const { data: created } = await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title,
                body: issueBody,
                assignees: ['circuitfive'],
              });
              console.log(`Created issue #${created.number}`);
            }

      - name: Close drift issue when no changes
        if: steps.check-commits.outputs.has_changes == 'false'
        uses: actions/github-script@v7
        with:
          script: |
            const title = 'Upstream Changes Detected';
            const { data: existing } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              creator: 'app/github-actions',
              per_page: 100,
            });
            const open = existing.filter(i => i.title === title);

            for (const issue of open) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                body: 'Synced — drift cleared. Auto-closing.',
              });
              await github.rest.issues.update({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                state: 'closed',
              });
              console.log(`Closed issue #${issue.number}`);
            }

      - name: Create error issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const runUrl = `https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`;

            const issueBody = [
              '## Upstream Sync Check Failed',
              '',
              'The automated upstream sync check workflow encountered an error.',
              '',
              `**Workflow Run:** [View logs](${runUrl})`,
              '',
              'Please review the workflow logs to identify and fix the issue.'
            ].join('\n');

            try {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: 'Upstream Sync Check Failed',
                body: issueBody,
                assignees: ['circuitfive']
              });
            } catch (error) {
              console.error('Failed to create error issue:', error);
            }
```

- [ ] **Step 2: Validate YAML**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/upstream-sync-check.yml')); print('ok')"
```
Expected: `ok`

If `yaml` isn't available, fall back to:
```bash
python3 -c "
import json, subprocess
out = subprocess.check_output(['python3', '-c', '''
import sys
content = open(\".github/workflows/upstream-sync-check.yml\").read()
# simple sanity: structure must contain known keys
for k in [\"on:\", \"jobs:\", \"upsert drift issue\", \"Close drift issue\", \"push:\", \"branches: [main]\"]:
    assert k.lower() in content.lower(), k
print(\"ok\")
'''])
print(out.decode())
"
```

- [ ] **Step 3: Sanity-check the new triggers and steps are present**

```bash
grep -n "push:\|branches: \[main\]\|Upsert drift issue\|Close drift issue" .github/workflows/upstream-sync-check.yml
```
Expected: shows the `push:` trigger, the `branches: [main]` line, the upsert step name, and the close step name.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/upstream-sync-check.yml
git commit -m "Upsert drift issue and auto-close on sync

Workflow no longer creates a new 'Upstream Changes Detected' issue every
week. Instead it searches for an existing open one and updates its body,
or creates one if none exists. When drift is gone (post-sync), it
auto-closes any open drift issues with a comment.

Adds 'push: branches: [main]' trigger so auto-close fires immediately
after a sync lands rather than waiting up to a week for the cron.

Refs #23"
```

---

## Task 6: Update the sync skill (SKILL.md)

**Files:**
- Modify: `.claude/skills/upstream-sync/SKILL.md`

- [ ] **Step 1: Replace section 4 ("Resolve marketplace.json conflicts")**

Open `.claude/skills/upstream-sync/SKILL.md`. Find the section starting with `### 4. Resolve marketplace.json conflicts` and ending just before `### 5. Verify`. Replace it with:

```markdown
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
```

- [ ] **Step 2: Update the "What we maintain on top" list**

Find the bullet line `- **Custom marketplace.json entries** — plugins we've added (e.g., `toolbelt`). The merge script identifies these automatically by diffing against upstream.` and replace it with:

```markdown
- **Fork-specific marketplace entries** in `.claude-plugin/fork-additions.json`
  (e.g., `toolbelt`). The merge script overlays these onto upstream's
  marketplace.json each sync.
```

- [ ] **Step 3: Verify the document still reads cleanly**

```bash
grep -c "merge_marketplace.py" .claude/skills/upstream-sync/SKILL.md
```
Expected: at least 2 (one in step 4, possibly one in adding-a-plugin section).

```bash
grep -n "\-\-exclude\|fork-specific entries" .claude/skills/upstream-sync/SKILL.md
```
Expected: no `--exclude` references; "fork-specific" mentions are present in the new wording.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/upstream-sync/SKILL.md
git commit -m "Update upstream-sync skill for manifest-driven flow

Replaces the conflict-resolution section with a single regeneration step.
Adds an 'Adding a fork-specific plugin' subsection pointing at
fork-additions.json. Drops references to the removed --exclude flag.

Refs #23"
```

---

## Task 7: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add a subsection under Development**

Open `CLAUDE.md`. Find the `## Development` heading. Just before `### Testing a Plugin Locally`, insert:

```markdown
### Adding a Fork-Specific Plugin

arizonabay-added marketplace entries live in `.claude-plugin/fork-additions.json`
— never edit `marketplace.json` directly. To add a plugin:

1. Append the entry to `.claude-plugin/fork-additions.json`
2. Run `python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py`
3. Commit both files

`marketplace.json` is regenerated on every upstream sync from
`upstream/main` + the manifest, so any direct edits there are overwritten.

```

- [ ] **Step 2: Verify**

```bash
grep -n "fork-additions.json\|Adding a Fork-Specific Plugin" CLAUDE.md
```
Expected: lines for both the heading and the file reference appear.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Document fork-additions.json workflow in CLAUDE.md

Tells future contributors to add fork plugins via the manifest, not by
editing marketplace.json directly.

Refs #23"
```

---

## Task 8: End-to-end verification

**Files:** none (verification only)

- [ ] **Step 1: Run the full unit test suite**

```bash
cd .claude/skills/upstream-sync/scripts && python3 -m unittest test_merge_marketplace.py -v
```
Expected: 5 tests pass.

- [ ] **Step 2: Dry-run the regenerator and confirm output is consistent with HEAD**

```bash
python3 .claude/skills/upstream-sync/scripts/merge_marketplace.py --dry-run
```
Expected: `Result: 173 plugins` (or whatever the current count is), `+ toolbelt: ...`. No errors.

- [ ] **Step 3: Confirm marketplace.json validity**

```bash
python3 -c "
import json
from collections import Counter
d = json.load(open('.claude-plugin/marketplace.json'))
names = [p['name'] for p in d['plugins']]
dupes = {n: c for n, c in Counter(names).items() if c > 1}
assert not dupes, f'Duplicates: {dupes}'
assert 'toolbelt' in names
print(f'{len(names)} plugins, no duplicates, toolbelt present')
"
```

- [ ] **Step 4: Lint the workflow YAML one more time**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/upstream-sync-check.yml'))"
```
Expected: no exception.

- [ ] **Step 5: Confirm git status is clean**

```bash
git status
```
Expected: `nothing to commit, working tree clean`.

- [ ] **Step 6: Push and let the workflow run via `push` trigger**

```bash
git push origin <branch-name>
```

After push lands on `main` (via merge or directly):
- The new `push: branches: [main]` trigger should fire the workflow
- Drift check should report `has_changes=false` (we just synced earlier this session)
- If issues #20–#22 were closed manually, no open drift issues remain — the close step is a no-op
- Verify the workflow run on GitHub: https://github.com/arizonabay/claude-plugins/actions

Note: if working on a feature branch, the `push` trigger only fires on `main`. To exercise the workflow before merge, use `gh workflow run upstream-sync-check.yml`.

- [ ] **Step 7: Reference the issue in the PR**

When opening the PR, include `Closes #23` in the description so the issue auto-closes on merge.

---

## Out of scope (do NOT implement)

- CI check that validates `marketplace.json` matches `regenerate(upstream/main, fork-additions.json)`
- Changes to issue title or body format beyond adding the "Last updated" line
- Replacing the issue-based notification with a status check
- Touching the failure-issue path
- README.md changes
