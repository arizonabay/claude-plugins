---
name: issue-scoping
description: This skill should be used when the user asks to "plan this work", "scope this feature", "create an issue for", "write an issue", "define the requirements", "break down this task", "what should the ticket include", or discusses work planning and issue definition. Provides methodology for transforming vague problems into well-defined, actionable GitHub issues.
version: 0.1.0
---

# Issue Scoping Methodology

Guidance for transforming problem descriptions into well-defined, actionable issues.

## Core Principles

### 1. Problems Before Solutions

Start with understanding the problem completely before proposing solutions. Resist the urge to jump to implementation details.

**Questions to explore:**
- What is actually happening vs. what should happen?
- Who is affected and how?
- What is the impact of not solving this?
- How was this discovered?

### 2. Scope Boundaries

Every issue needs clear boundaries. Define what is included AND what is explicitly excluded.

**Scope indicators:**
- "This issue covers X but not Y"
- "Out of scope: Z (tracked separately)"
- "Prerequisites: A must be complete first"

### 3. Measurable Completion

Define what "done" looks like before starting. Acceptance criteria should be verifiable, not subjective.

**Good criteria:**
- "Users can export data in CSV format"
- "Page loads in under 2 seconds"
- "Error message displays when validation fails"

**Avoid:**
- "Performance is improved"
- "User experience is better"
- "Code is cleaner"

## Discovery Questions

### Understanding the Problem

Ask adaptive questions based on context. Not all questions apply to every issue.

**For bugs:**
- What is the current behavior?
- What is the expected behavior?
- How to reproduce the issue?
- What is the frequency/severity?
- Are there workarounds?

**For features:**
- What problem does this solve?
- Who requested this and why?
- What alternatives were considered?
- How does this fit with existing functionality?
- What happens if we don't build this?

**For improvements:**
- What specifically needs improving?
- How will improvement be measured?
- What is the current baseline?
- What is "good enough"?

### Identifying Constraints

Surface constraints early to avoid scope creep and unrealistic expectations.

- Are there technical limitations?
- Are there dependencies on other work?
- Are there time or resource constraints?
- Are there compliance or security requirements?
- What existing patterns should be followed?

## Issue Structure

### Title

Craft titles that communicate at a glance:
- Start with action verb (Add, Fix, Update, Remove, Implement)
- Be specific enough to distinguish from similar issues
- Keep under 60 characters when possible

**Examples:**
- "Add CSV export to dashboard reports"
- "Fix timeout errors on large file uploads"
- "Update authentication to support OAuth 2.0"

### Problem Statement

The opening section should answer: "Why does this issue exist?"

**Template:**
```markdown
## Problem

[Description of current state and why it's problematic]

**Impact:** [Who is affected and how severely]

**Context:** [Background information, how this was discovered]
```

### Proposed Solution

After the problem is clear, outline the recommended approach.

**Template:**
```markdown
## Proposed Solution

[High-level description of the approach]

### Approach Details

[More specific implementation notes]

### Alternatives Considered

- **Option A**: [Description] - [Why not chosen]
- **Option B**: [Description] - [Why not chosen]
```

### Implementation Steps

Break work into concrete, actionable tasks. Each step should be completable independently when possible.

**Guidelines:**
- Number steps sequentially
- Keep steps small enough to complete in a single session
- Note dependencies between steps
- Include testing and documentation steps

**Example:**
```markdown
## Implementation Steps

1. Add CSV generation utility to `lib/exporters/`
2. Create export endpoint in reports controller
3. Add "Export CSV" button to dashboard UI
4. Write unit tests for CSV generation
5. Add E2E test for export flow
6. Update API documentation
```

### Acceptance Criteria

Define verifiable conditions for completion.

**Format:**
```markdown
## Acceptance Criteria

- [ ] User can click "Export CSV" from any dashboard view
- [ ] Exported file contains all visible columns
- [ ] Large exports (>10k rows) complete within 30 seconds
- [ ] Export respects current filters and date range
```

### Dependencies and Related Work

Surface connections to other issues and external dependencies.

```markdown
## Dependencies

- Requires #123 (new data model) to be merged first
- Blocked by vendor API upgrade (external)

## Related Issues

- Related to #456 (PDF export feature)
- May resolve #789 (export timeout complaints)
```

## Labeling Strategy

Apply labels that aid filtering and prioritization.

### Type Labels

Categorize what kind of work this is:
- `bug` - Something is broken
- `feature` - New functionality
- `enhancement` - Improvement to existing feature
- `chore` - Maintenance, refactoring, dependencies
- `docs` - Documentation changes

### Priority Labels

Indicate urgency:
- `critical` - Blocking production, immediate attention
- `high` - Important, should be addressed soon
- `medium` - Normal priority
- `low` - Nice to have, when time permits

### Area Labels

Identify which part of the system:
- Component names (`frontend`, `backend`, `api`)
- Feature areas (`auth`, `billing`, `dashboard`)
- Technical concerns (`security`, `performance`, `accessibility`)

## Anti-Patterns to Avoid

### Scope Creep Indicators

Watch for these warning signs:
- "While we're at it, we could also..."
- "It would be nice to also add..."
- Issue description keeps growing
- Original problem gets buried under additions

**Resolution:** Split into multiple issues, link them together.

### Vague Requirements

Avoid ambiguous language:
- "Make it better" → "Reduce load time from 5s to under 2s"
- "Improve UX" → "Add loading indicators to async operations"
- "Fix the bug" → "Handle null user case in checkout flow"

### Missing Context

Issues without context become confusing later:
- Always include "why" not just "what"
- Link to relevant discussions, designs, or documentation
- Note who requested this and when

### Over-Specification

Don't prescribe implementation details unnecessarily:
- Describe the desired outcome, not every code change
- Allow flexibility for the implementer
- Focus on "what" and "why", be lighter on "how"

## Working with Codebase Context

When planning issues for existing codebases, consider leveraging code analysis:

### When Code Analysis Helps

- Understanding existing patterns before proposing changes
- Identifying affected areas and dependencies
- Finding similar implementations to reference
- Estimating complexity based on current architecture

### When to Skip Code Analysis

- New projects with no existing codebase
- Non-technical issues (process, documentation)
- Issues where requirements are already clear
- When time is more valuable than additional context

## Issue Size Guidelines

### Right-Sized Issues

Good issues are:
- Completable in 1-3 days of focused work
- Reviewable in a single PR
- Testable independently
- Understandable without extensive context

### Too Large

Split issues that:
- Span multiple unrelated components
- Have more than 10 implementation steps
- Would result in PRs over 500 lines
- Mix refactoring with feature work

### Too Small

Combine issues that:
- Take less than an hour
- Are trivial and obvious
- Would create PR noise
- Have no standalone value

## Quick Reference

### Issue Template

```markdown
## Problem

[What's wrong and why it matters]

**Impact:** [Severity and who is affected]

## Proposed Solution

[Recommended approach]

## Implementation Steps

1. [Step one]
2. [Step two]
3. [Step three]

## Acceptance Criteria

- [ ] [Verifiable condition 1]
- [ ] [Verifiable condition 2]

## Dependencies

- [Any blockers or prerequisites]
```

### Checklist Before Creating

- [ ] Problem is clearly stated with impact
- [ ] Scope boundaries are defined
- [ ] Acceptance criteria are verifiable
- [ ] Steps are actionable and sized appropriately
- [ ] Labels reflect type, priority, and area
- [ ] Related issues are linked
