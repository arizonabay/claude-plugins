---
description: Plan and create a well-scoped GitHub issue from a problem description
argument-hint: <problem description>
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
  - TodoWrite
---

# Issue Planning Workflow

Guide the user through transforming a problem description into a well-scoped GitHub issue.

**Initial problem:** $ARGUMENTS

---

## Phase 1: Understanding the Problem

Start by acknowledging the problem description provided. If `$ARGUMENTS` is empty, ask the user to describe the problem they want to solve.

### Gather Context

Ask adaptive clarifying questions based on the problem type. Consider:
- What is the current behavior vs. expected behavior?
- Who is affected and how severely?
- What is the scope and boundaries of this work?
- Are there dependencies or blockers?
- What does success look like?

Use `AskUserQuestion` to gather structured input. Ask 2-3 questions at a time, not all at once.

---

## Phase 2: Codebase Analysis (Optional)

Check if this appears to be a technical issue that would benefit from codebase analysis:

1. Check if the current directory is a git repository with code
2. If the problem involves existing code, ask the user:

```
"Would codebase analysis help scope this issue? I can explore relevant code patterns and architecture."
```

If the user agrees and feature-dev plugin is available, use the Task tool to invoke:
- `feature-dev:code-explorer` - To understand existing implementation
- `feature-dev:code-architect` - To evaluate architectural approaches

---

## Phase 3: Solution Exploration

Based on gathered information, propose 2-3 solution strategies. For each strategy:
- Describe the approach
- List pros and cons
- Estimate relative complexity (small/medium/large)
- Note any risks or unknowns

Present these options and get user input on preferred direction.

---

## Phase 4: Detailed Planning

Once a direction is chosen, break it down into concrete steps:

1. Create a clear, actionable title
2. Write a comprehensive issue body with:
   - **Problem Statement**: Clear description of what needs to be solved
   - **Context**: Background information gathered
   - **Proposed Solution**: The chosen approach
   - **Implementation Steps**: Numbered, actionable tasks
   - **Acceptance Criteria**: How to verify the work is complete
   - **Dependencies**: Any blockers or related work

---

## Phase 5: Configuration & Labels

### Read Settings

Check for configuration file:
```
.claude/issue-planner.local.md
```

If it exists, read it to get:
- Available labels (by category)
- Active milestones
- Available projects

### Select Metadata

Based on the issue content and available options from settings, suggest:
- **Labels**: Match to the issue type, priority, and area
- **Milestone**: If the work fits an active milestone
- **Project**: If a project board is configured

Present selections to user for approval.

---

## Phase 6: Review & Approval

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

---

## Phase 7: Create Issue

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

---

## Tips

- Keep questions focused and avoid overwhelming the user
- For complex issues, use TodoWrite to track planning progress
- If the user seems uncertain about scope, suggest starting smaller
- Reference existing issues or PRs if relevant to the discussion
