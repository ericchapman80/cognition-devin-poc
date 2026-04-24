# {{ORG_NAME}} Story Agents

This file defines the available agents for creating and managing Agile Epics and user stories. Each agent has a specific role and can hand off to other agents.

## IDE Commands (Slash Commands)

The agents are available as **slash commands** in your IDE. Type `/prd2story.` to see all available commands.

| Command | Description | Handoffs To |
|---------|-------------|-------------|
| `/prd2story.epic-generator` | Creates Epics from PRDs | story-generator |
| `/prd2story.story-generator` | Creates detailed user stories one at a time | story-reviewer, jira-creator |
| `/prd2story.story-reviewer` | Reviews stories for INVEST compliance | story-generator, jira-creator |
| `/prd2story.jira-creator` | Creates Epics and stories in JIRA | epic-generator, story-generator |

## Recommended Workflow

```
PRD → /prd2story.epic-generator → /prd2story.story-generator → /prd2story.story-reviewer → /prd2story.jira-creator
```

Each command pauses at user control points and suggests the next step with handoff options.

## User Control Points

Every agent pauses for explicit user input before taking irreversible actions. You are always in control.

| Stage | What the Agent Asks | What You Can Do |
|-------|---------------------|-----------------|
| **Epic: story list review** | "Here is the proposed story list. Type **approved** or reply with changes." | Reorder, rename, remove, or add stories before anything is saved |
| **Story: generation confirm** | Shows progress table, asks "Proceed? (yes / skip / pick a number)" | Generate, skip, or jump to a specific story |
| **Review: user approval** | "Do you approve this story? (yes / no + notes)" | Approve → moves to `.prd2story/stories/approved/`; No → adds feedback for revision |
| **JIRA: creation preview** | Shows preview table, asks "Type **confirm** to proceed or **cancel** to abort." | Review every issue before any API call is made |

## Folder Structure

```
your-project/
├── .prd2story/
│   ├── AGENTS.md                  # This file
│   ├── init-options.json          # Saved configuration
│   ├── prd/                       # Product Requirements Documents
│   │   ├── feature-name.md        # PRD files go here
│   │   └── example-prd.md         # Example PRD template
│   └── stories/
│       ├── drafts/                # Generated Epics and story drafts
│       ├── approved/              # User-approved stories
│       ├── created-in-jira/       # Stories with JIRA keys
│       ├── checklists/            # Per-story INVEST review checklists
│       └── status/                # Per-Epic progress tracker files
└── .env.example                   # Environment variables template
```

## Quality Guidelines

### Vertical Slice Principle

Every story delivers end-to-end value across all three layers. **NEVER** create horizontal stories like "Create DB schema" or "Build API."
- **App/UI Layer** - Frontend components, user interactions
- **Service/API Layer** - Backend services, API endpoints
- **Database Layer** - Data models, queries, persistence

### Scope Constraints

- Completable by **ONE developer** in approx **8-12h** including tests
- Use T-shirt estimates: **XS** ~4h (1 pt), **S** ~8h (2 pts), **M** ~12h (3 pts)
- **Split** any story larger than M (~12h). **Merge** anything under 2 hours into a related story.

### INVEST Principles

- **I**ndependent - No blocking dependencies
- **N**egotiable - Flexible implementation details
- **V**aluable - Clear user/business value
- **E**stimable - Can be estimated by the team
- **S**mall - Right-sized for one developer, 8-12h including tests
- **T**estable - Clear, verifiable acceptance criteria

## Best Practices

- Use clear, concise, and professional language
- Each story must be a vertical slice covering all three layers
- 2-5 acceptance criteria per story in Given/When/Then format
- NEVER create horizontal stories (DB-only, API-only, UI-only)
- NEVER use vague acceptance criteria like "it works correctly"
- **Use the handoff suggestions** to move through the workflow efficiently

---

**Bootstrapped with [prd2story](https://github.com/ericchapman80/cognition-devin-poc/tree/main/prd2story)**
