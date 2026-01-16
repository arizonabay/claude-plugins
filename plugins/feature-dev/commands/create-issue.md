---
description: Create a GitHub issue from a problem description with optional codebase context
argument-hint: <problem description>
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

# Create Issue

Create a well-scoped GitHub issue from a problem description.

**Initial problem:** $ARGUMENTS

---

## Phase 1: Problem Understanding

Start by acknowledging the problem description provided. If `$ARGUMENTS` is empty, ask the user to describe the problem they want to solve.

### Gather Context

Ask adaptive clarifying questions based on the problem type. Use `AskUserQuestion` to gather structured input. Ask 2-3 questions at a time, not all at once.

**Questions to consider:**
- What is the current behavior vs. expected behavior?
- Who is affected and how severely?
- What is the scope and boundaries of this work?
- Are there dependencies or blockers?

Keep this phase focused - gather enough context to write a clear issue, but don't over-explore.

---

## Phase 2: Codebase Analysis (Optional)

Check if this appears to be a technical issue that would benefit from codebase analysis:

1. Check if the current directory is a git repository with code
2. Ask the user:

```
"Would codebase analysis help scope this issue? I can explore relevant code patterns and architecture."
```

If the user agrees, use the Task tool to invoke a single `code-explorer` agent:
- Focus on understanding the affected area
- Keep analysis brief - just enough to inform the issue
- Ask the agent to identify key files and patterns

If the user declines or this isn't a technical issue, skip to Phase 3.

---

## Phase 3: Issue Composition

Based on gathered information, compose the issue:

### Title

Create a clear, actionable title:
- Start with action verb (Add, Fix, Update, Remove, Implement)
- Be specific enough to distinguish from similar issues
- Keep under 60 characters when possible

### Issue Body

Write a comprehensive issue body with:

```markdown
## Problem

[Description of current state and why it's problematic]

**Impact:** [Who is affected and how severely]

## Proposed Solution

[High-level description of the recommended approach]

## Acceptance Criteria

- [ ] [Verifiable condition 1]
- [ ] [Verifiable condition 2]
- [ ] [Verifiable condition 3]

## Dependencies

- [Any blockers or prerequisites, or "None"]
```

### Configuration & Labels

Check for configuration file at `.claude/feature-dev.local.md`. If it exists, read it to get:
- Available labels (by category)
- Active milestones
- Available projects

Based on the issue content and available options, suggest appropriate:
- **Labels**: Match to the issue type, priority, and area
- **Milestone**: If the work fits an active milestone
- **Project**: If a project board is configured

---

## Phase 4: Create Issue

Present the complete issue for review:

```markdown
## Issue Preview

**Title:** [proposed title]

**Labels:** [label1, label2, ...]
**Milestone:** [milestone or "none"]
**Project:** [project or "none"]

---

[Full issue body]

---
```

Ask: "Does this issue look correct? Should I create it?"

### Create with GitHub CLI

Once approved, use the GitHub CLI to create the issue:

```bash
gh issue create \
  --title "Issue title" \
  --body "Issue body" \
  --label "label1,label2" \
  --milestone "milestone-name" \
  --project "project-name"
```

Notes:
- Only include `--milestone` if one was selected
- Only include `--project` if one was selected
- Use `--label` with comma-separated values

After creation, display:
- Issue URL
- Issue number
- Brief summary of what was created

---

## Error Handling

- If `gh` CLI is not installed, inform the user and provide installation instructions
- If `gh` is not authenticated, guide user to run `gh auth login`
- If labels/milestone/project don't exist, warn before creation and offer to proceed without them
- If issue creation fails, show the error and offer to retry or save the content locally
