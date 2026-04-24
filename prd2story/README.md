# prd2story

Bootstrap PRD-to-Story agent workflows into any repository.

```
 ____  ____  ____  ____  ____  _____  ___  ____  _  _
(  _ \(  _ \(  _ \(_  _)(  _ \(  _  )/ __)(_  _)( \/ )
 )___/ )   / )(_) )  )(  _)(_  )(_)(  \__ \  )(  )  (
(__)  (_)\_)(____/ (__) (____)(_____)( ___/ (__) (_/\_)
```

**prd2story** scaffolds AI-powered agents for converting Product Requirements Documents (PRDs) into Agile Epics and user stories — directly in your IDE.

## Quick Start

```bash
# One-time usage (no install required)
uvx --from git+https://github.com/ericchapman80/cognition-devin-poc.git#subdirectory=prd2story prd2story init .

# Or install persistently
pip install git+https://github.com/ericchapman80/cognition-devin-poc.git#subdirectory=prd2story
prd2story init .
```

## What It Does

Running `prd2story init` scaffolds everything you need into your repo:

```
your-project/
├── prd/                           # Put your PRDs here
│   └── example-prd.md
├── stories/
│   ├── drafts/                    # Generated Epics and story drafts
│   ├── approved/                  # User-approved stories
│   ├── created-in-jira/           # Stories with JIRA keys
│   ├── checklists/                # INVEST review checklists
│   └── status/                    # Per-Epic progress trackers
├── .github/agents/                # (if Copilot selected)
│   ├── prd2story.epic-generator.md
│   ├── prd2story.story-generator.md
│   ├── prd2story.story-reviewer.md
│   └── prd2story.jira-creator.md
├── AGENTS.md                      # Agent documentation
├── .env.example                   # Environment variables template
└── .prd2story/init-options.json   # Saved configuration
```

## Supported AI Assistants

| Integration | Key | IDE Location |
|-------------|-----|--------------|
| GitHub Copilot | `copilot` | `.github/agents/` |
| Claude Code | `claude` | `.claude/commands/` |
| Gemini CLI | `gemini` | `.gemini/commands/` |
| Cursor | `cursor-agent` | `.cursor/rules/` |
| opencode | `opencode` | `.opencode/commands/` |
| Codex CLI | `codex` | `.codex/commands/` |
| Windsurf | `windsurf` | `.windsurf/workflows/` |
| Kilo Code | `kilocode` | `.kilocode/commands/` |
| Amp | `amp` | `.amp/commands/` |

## Usage

### Interactive Mode (default)

```bash
prd2story init .
```

This launches an interactive session with:
1. ASCII art banner
2. Arrow-key integration selector
3. Prompts for org name, JIRA project, tech stack, team size

### Non-Interactive Mode

```bash
prd2story init . \
  --integration copilot \
  --org "My Company" \
  --jira-project PROJ \
  --tech-stack "React, Node.js, PostgreSQL" \
  --team-size "5 developers" \
  --non-interactive
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--integration`, `-i` | AI assistant integration key | (interactive) |
| `--org` | Organization/team name | `Your Organization` |
| `--jira-project` | Default JIRA project key | `PROJ` |
| `--tech-stack` | Tech stack context | (empty) |
| `--team-size` | Team size context | (empty) |
| `--force`, `-f` | Overwrite existing files | `false` |
| `--non-interactive`, `-y` | Skip prompts, use defaults | `false` |
| `--here` | Init in current directory | `false` |

## Agents

### Workflow

```
PRD → epic-generator → story-generator → story-reviewer → jira-creator
```

### Agent Descriptions

| Agent | Purpose |
|-------|---------|
| **epic-generator** | Reads PRDs, extracts Epics with story breakdowns. Waits for user approval. |
| **story-generator** | Creates detailed vertical-slice user stories one at a time with progress tracking. |
| **story-reviewer** | Reviews stories for INVEST compliance. Approves or sends back for revision. |
| **jira-creator** | Creates Epics and stories in JIRA via Atlassian MCP after preview confirmation. |

Each agent pauses at **user control points** — you always approve before anything is saved or created.

## After Initialization

1. Add your PRD to the `prd/` folder
2. Copy `.env.example` to `.env` and fill in your Atlassian credentials
3. Open your IDE and type `/prd2story.epic-generator` to start

## Development

### Prerequisites

- Python >= 3.11

### Setup

```bash
git clone https://github.com/ericchapman80/cognition-devin-poc.git
cd cognition-devin-poc/prd2story
pip install -e ".[test,dev]"
```

### Run Tests

```bash
pytest
```

### Lint

```bash
ruff check src/ tests/
```

## Architecture

prd2story follows the [spec-kit](https://github.com/github/spec-kit) integration registry pattern:

- **Integration subpackages** — Each AI assistant is a self-contained package in `src/prd2story_cli/integrations/`
- **Base classes** — `IntegrationBase` and `MarkdownIntegration` provide shared behavior
- **Template system** — Markdown command templates with `{{ORG_NAME}}` / `{{JIRA_PROJECT}}` placeholders
- **Registry** — Integrations self-register via `@register` decorator

Adding a new integration is a single file in `src/prd2story_cli/integrations/your_ide/__init__.py`.

## License

MIT
