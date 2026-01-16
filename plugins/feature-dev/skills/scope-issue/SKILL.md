---
name: scope-issue
description: This skill should be used when the user asks to "scope this problem", "define the issue", "write a bug report", "create an issue for", "what should the ticket include", "describe this problem", or discusses issue creation and problem definition. Provides methodology for transforming vague problems into well-defined, actionable issues.
version: 1.0.0
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
- "Make it better" -> "Reduce load time from 5s to under 2s"
- "Improve UX" -> "Add loading indicators to async operations"
- "Fix the bug" -> "Handle null user case in checkout flow"

### Missing Context

Issues without context become confusing later:
- Always include "why" not just "what"
- Link to relevant discussions, designs, or documentation
- Note who requested this and when

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

## Labeling Strategy

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

## Quick Reference

### Issue Template

```markdown
## Problem

[What's wrong and why it matters]

**Impact:** [Severity and who is affected]

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
- [ ] Labels reflect type, priority, and area
- [ ] Related issues are linked
