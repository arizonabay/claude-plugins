# issue-planner

Transform problem descriptions into well-scoped, detailed GitHub issues through a guided planning workflow.

## Features

- **Guided Discovery**: Asks adaptive clarifying questions to thoroughly understand the problem
- **Solution Exploration**: Proposes and evaluates different approaches before committing
- **Codebase-Aware** (optional): Leverages feature-dev's code-explorer and code-architect agents when analyzing technical issues
- **Structured Output**: Creates GitHub issues with title, body, labels, milestone, and project
- **Approval Flow**: Presents the plan for your approval before creating the issue

## Usage

```
/issue-planner:plan <problem description>
```

### Example

```
/issue-planner:plan Users are reporting slow page loads on the dashboard
```

The command will:
1. Ask clarifying questions to understand the problem deeply
2. Optionally analyze relevant code (if codebase context helps)
3. Propose solution strategies
4. Present a detailed plan for approval
5. Create the GitHub issue with appropriate labels

## Configuration

Create `.claude/issue-planner.local.md` in your project to configure labels, milestones, and projects:

```yaml
---
labels:
  type:
    - bug
    - feature
    - chore
    - docs
  priority:
    - critical
    - high
    - medium
    - low
  area:
    - frontend
    - backend
    - api
    - infrastructure

milestones:
  - v1.0
  - v1.1
  - backlog

projects:
  - "Project Board Name"
---

## Additional Context

Any markdown content here will be included as context when planning issues.
You can describe your team's conventions, preferred issue structure, etc.
```

## Requirements

- **GitHub CLI (`gh`)**: Must be installed and authenticated
- **feature-dev plugin** (optional): For codebase analysis features

## Components

| Component | Description |
|-----------|-------------|
| `/issue-planner:plan` | Main command - guided issue planning workflow |
| `issue-scoping` skill | Auto-loads during planning discussions |

## How It Works

1. **Discovery**: You describe the problem, Claude asks targeted questions
2. **Analysis**: If relevant, analyzes codebase using feature-dev agents
3. **Strategy**: Proposes approaches with trade-offs
4. **Planning**: Breaks down the chosen approach into detailed steps
5. **Review**: Presents the complete issue for your approval
6. **Creation**: Creates the GitHub issue with all metadata
