---
description: Create comprehensive implementation plan with architecture analysis, optionally linked to a GitHub issue
argument-hint: [#issue-number | issue URL | feature description]
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
  - TodoWrite
---

# Implementation Planning

Create a comprehensive implementation plan with architecture analysis and documentation.

**Input:** $ARGUMENTS

---

## Phase 1: Understanding Requirements

### Parse Arguments

Determine the input type from `$ARGUMENTS`:

1. **Issue reference**: If argument matches `#\d+`, `^\d+$`, or contains `github.com/.*/issues/\d+`:
   - Extract issue number
   - Fetch issue details: `gh issue view <number> --json title,body,labels,url`
   - Store issue URL for linking in plan document
   - Extract problem description and requirements from issue body

2. **Feature description**: Otherwise treat as free-form feature description
   - Proceed without issue linkage

### Gather Requirements

If working from an issue:
- Summarize the issue content
- Identify any gaps or ambiguities in the issue
- Ask clarifying questions if needed

If working standalone:
- Ask the user to describe the feature or change
- Gather context: What problem does this solve? Who is affected?
- Identify constraints and requirements

Create a todo list tracking all phases.

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns

### Launch Exploration Agents

Use the Task tool to launch 2-3 `code-explorer` agents in parallel. Each agent should target a different aspect:

**Example agent prompts:**
- "Find features similar to [feature] and trace through their implementation comprehensively"
- "Map the architecture and abstractions for [feature area], tracing through the code"
- "Analyze integration points and dependencies relevant to [feature]"

Each agent should return:
- Entry points and key files (5-10 files)
- Execution flow and patterns
- Architecture insights
- Relevant abstractions

### Synthesize Findings

Once agents return:
1. Read all files identified by agents
2. Compile comprehensive summary of patterns discovered
3. Note conventions that must be followed
4. Identify potential integration challenges

Present findings to user before proceeding.

---

## Phase 3: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

### Launch Architecture Agents

Use the Task tool to launch 2-3 `code-architect` agents in parallel with different focuses:

1. **Minimal changes**: Smallest change that solves the problem, maximum reuse of existing code
2. **Clean architecture**: Focus on maintainability, elegant abstractions, long-term health
3. **Pragmatic balance**: Balance between speed and quality, practical trade-offs

Each agent should return:
- Approach description
- Files to create/modify
- Component design
- Trade-offs and risks

### Compare Approaches

Review all approaches and:
1. Summarize each approach concisely
2. Create trade-offs comparison table
3. Form your opinion on which fits best
4. Present recommendation with reasoning

**Ask user which approach they prefer** before proceeding.

---

## Phase 4: Alternatives Documentation

Document all explored alternatives for the plan file:

For each alternative:
- **Approach name**: Descriptive label
- **Description**: What this approach involves
- **Pros**: Benefits and advantages
- **Cons**: Drawbacks and limitations
- **Complexity**: Small / Medium / Large

Document the chosen approach with detailed justification:
- Why this approach over others
- What trade-offs were accepted
- What assumptions were made

---

## Phase 5: Implementation Planning

### Break Down Implementation

Create concrete implementation steps:
- Number steps sequentially
- Group by phase or component
- Note dependencies between steps
- Include testing steps

### Create Verification Plan

Define how the implementation will be verified:

**Automated Tests:**
- Unit tests for new components
- Integration tests for interactions
- Edge case coverage

**Manual Testing:**
- User experience scenarios
- Visual verification needs
- Edge cases difficult to automate

**Acceptance Criteria:**
- Map each criterion to verification method
- Ensure all criteria are testable

---

## Phase 6: Document Generation

### Determine Output Path

Check for configuration at `.claude/feature-dev.local.md`:
- Look for `plan_output_dir` setting
- Default to `docs/plans/` if not configured

Generate slug from:
- Issue title (if linked): lowercase, hyphens, no special chars
- Feature description: extract key words

### Create Plan Document

Write the plan file to `<output_dir>/<slug>.md`:

```markdown
# <Feature Title>

**Issue:** [#<number>](<url>) (if linked, otherwise omit)
**Created:** <YYYY-MM-DD>
**Status:** Planning

## Motivation

<Problem statement from issue or discussion>

<Impact and why this matters>

## Alternatives Considered

### Option 1: <Name>
**Approach:** <Description>
**Pros:** <List>
**Cons:** <List>
**Complexity:** <Small/Medium/Large>

### Option 2: <Name>
...

### Option 3: <Name>
...

## Chosen Approach

**Selected:** Option <N> - <Name>

**Justification:**
<Detailed reasoning for why this approach was chosen>

## Implementation Plan

### Phase 1: <Name>
- [ ] Step 1
- [ ] Step 2

### Phase 2: <Name>
- [ ] Step 3
- [ ] Step 4

## Verification Plan

### Automated Tests
- [ ] Unit tests for <component>
- [ ] Integration tests for <flow>

### Manual Testing
- [ ] <Scenario 1>
- [ ] <Scenario 2>

### Acceptance Criteria
- [ ] <Criterion 1>
- [ ] <Criterion 2>

## Dependencies

- <Dependency 1>
- <Dependency 2>

## Related Issues

- #<related-issue-1>
- #<related-issue-2>
```

### Complete

Present summary to user:
- Path to created plan file
- Brief summary of the plan
- Suggested next steps (implementation or review)

Mark all todos complete.

---

## Error Handling

- If `gh` CLI is not available for issue fetching, ask user to provide issue details manually
- If codebase exploration returns insufficient results, ask user for guidance on where to look
- If output directory doesn't exist, create it
- If plan file already exists, ask user whether to overwrite or use a new name
