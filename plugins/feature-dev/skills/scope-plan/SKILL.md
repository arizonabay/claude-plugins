---
name: scope-plan
description: This skill should be used when the user asks to "plan this implementation", "design the solution", "document the approach", "create a plan for", "write implementation plan", "explore alternatives", "justify this approach", or discusses solution design and architecture planning. Provides methodology for exploring alternatives and creating comprehensive implementation plans.
version: 1.0.0
---

# Implementation Planning Methodology

Guidance for exploring solution alternatives and creating comprehensive implementation plans.

## Solution Exploration

### Proposing Alternatives

Always explore 2-3 distinct approaches before committing to a solution. Each alternative should represent a genuinely different strategy, not minor variations.

**For each alternative, document:**
- **Approach**: High-level description of the strategy
- **Pros**: Benefits and advantages
- **Cons**: Drawbacks and limitations
- **Complexity**: Small / Medium / Large
- **Risks**: Potential issues or unknowns

### Evaluating Trade-offs

Consider these dimensions when comparing approaches:

**Technical factors:**
- Implementation complexity
- Maintenance burden
- Performance characteristics
- Scalability implications
- Testing difficulty

**Practical factors:**
- Time to implement
- Familiarity with patterns
- Reuse of existing code
- Integration with current architecture
- Future flexibility

### Complexity Estimation

**Small**: Isolated change, touches 1-2 files, clear implementation path
**Medium**: Cross-cutting change, touches 3-7 files, some design decisions
**Large**: Architectural change, touches 8+ files, significant design work

## Proposed Solution Structure

Once an approach is chosen, document it clearly:

```markdown
## Proposed Solution

[High-level description of the chosen approach]

### Approach Details

[Specific implementation notes, patterns to use, key decisions]

### Alternatives Considered

- **Option A**: [Description] - [Why not chosen]
- **Option B**: [Description] - [Why not chosen]

### Justification

[Why this approach was selected over the alternatives]
```

## Implementation Steps

Break work into concrete, actionable tasks. Each step should be completable independently when possible.

**Guidelines:**
- Number steps sequentially
- Keep steps small enough to complete in a single session
- Note dependencies between steps
- Include testing and documentation steps
- Group related changes together

**Example:**
```markdown
## Implementation Steps

1. Add data model for export configuration
2. Create export service with format handlers
3. Add API endpoint for triggering exports
4. Build UI component for export options
5. Write unit tests for export service
6. Add integration tests for export flow
7. Update API documentation
```

## Acceptance Criteria

Define verifiable conditions for completion. Good criteria are:
- Specific and measurable
- Testable (automated or manual)
- Focused on outcomes, not implementation

**Format:**
```markdown
## Acceptance Criteria

- [ ] User can trigger export from dashboard
- [ ] Export supports CSV and JSON formats
- [ ] Large exports (>10k rows) complete within 30 seconds
- [ ] Export respects current filters and date range
- [ ] Errors display user-friendly message
```

## Plan Document Structure

For comprehensive planning, use this structure:

```markdown
# <Feature Title>

**Issue:** #<number> (if linked)
**Created:** <date>
**Status:** Planning

## Motivation

[Problem statement explaining why this work matters]

[Impact on users, business, or technical health]

## Alternatives Considered

### Option 1: <Name>
**Approach:** <Description>
**Pros:** <List>
**Cons:** <List>
**Complexity:** <Small/Medium/Large>

### Option 2: <Name>
...

## Chosen Approach

**Selected:** Option <N> - <Name>

**Justification:**
[Detailed reasoning for why this approach was chosen]

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
```

## Architecture Decision Documentation

When making significant architectural choices, document:

### Decision Context
- What problem prompted this decision?
- What constraints exist?
- What options were considered?

### Decision
- What was decided?
- What are the consequences?
- What trade-offs were accepted?

### Rationale
- Why was this option chosen?
- What evidence supports this choice?
- What would change this decision?

## Verification Planning

### Test Strategy

Identify testing needs at multiple levels:

**Unit tests**: Individual functions and components
**Integration tests**: Component interactions
**End-to-end tests**: Full user workflows
**Performance tests**: Load and response time (if applicable)

### Manual Testing Scenarios

Document scenarios that require human verification:
- User experience flows
- Edge cases difficult to automate
- Visual/design verification
- Accessibility testing

### Acceptance Verification

Map acceptance criteria to verification methods:

| Criterion | Verification Method |
|-----------|-------------------|
| Export completes in <30s | Performance test |
| Error message displays | Unit test + manual |
| Filters are respected | Integration test |

## Anti-Patterns to Avoid

### Over-Specification

Don't prescribe implementation details unnecessarily:
- Describe the desired outcome, not every code change
- Allow flexibility for the implementer
- Focus on "what" and "why", be lighter on "how"

### Missing Justification

Plans without reasoning become confusing later:
- Always explain "why" for significant choices
- Document rejected alternatives
- Note assumptions that could change

### Incomplete Verification

Don't skip the testing plan:
- Every acceptance criterion needs a verification method
- Include both automated and manual testing
- Consider edge cases and error conditions
