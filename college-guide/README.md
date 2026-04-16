# College Guide — Multi-Agent Workflow

A multi-agent orchestration workflow for generating comprehensive college planning reports tailored to **H-4/immigrant STEM students**, built using the GitHub Copilot `.agent.md` pattern.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              college-guide (Orchestrator)            │
│                                                     │
│  1. @profile-analyzer    → Academic assessment      │
│  2. @college-researcher  → College recommendations  │
│  3. @financial-analyst   → Cost & ROI analysis      │
│  4. @career-pathway      → Career & immigration     │
│  5. @report-compiler     → Compile full report      │
│  6. @report-reviewer     → Review & approve         │
│       ↕ (revision loop, max 3 cycles)               │
│  7. Final approved report                           │
└─────────────────────────────────────────────────────┘
```

## Agent Descriptions

| Agent | File | Role |
|-------|------|------|
| **College Guide** | `college-guide.agent.md` | Orchestrator — chains all agents, manages review loop |
| **Profile Analyzer** | `profile-analyzer.agent.md` | Analyzes GPA, course rigor, test scores, extracurriculars |
| **College Researcher** | `college-researcher.agent.md` | Recommends in-state and out-of-state colleges with detailed comparison tables |
| **Financial Analyst** | `financial-analyst.agent.md` | Analyzes costs, merit aid strategy, ROI, H-4 financial aid rules |
| **Career Pathway** | `career-pathway.agent.md` | Plans career trajectory, H-1B strategy, immigration pathways, MS degree strategy |
| **Report Compiler** | `report-compiler.agent.md` | Compiles all agent outputs into a single comprehensive markdown report |
| **Report Reviewer** | `report-reviewer.agent.md` | Reviews report for completeness, accuracy, consistency; approves or requests revision |

## How to Use

### Option 1: Full Orchestrated Workflow (Recommended)

Invoke the orchestrator agent with a student profile:

```
@college-guide Generate a complete college planning guide for the following student:

Student: Divija Mondal
Grade: 10 (Class of 2028)
School: Neuqua Valley High School, Naperville, IL
Parent Visa: H-1B | Student Visa: H-4
Country of Birth: India
GPA: 4.32 weighted / 3.95 unweighted
Intended Major: Computer Science
State: Illinois
...
```

The orchestrator will automatically chain all six agents in sequence and produce a reviewed final report.

### Option 2: Individual Agent Invocation

You can invoke any agent directly for a specific task:

```
@profile-analyzer Analyze this student's academic profile: ...
@college-researcher Recommend colleges for this profile: ...
@financial-analyst Analyze costs for these colleges: ...
@career-pathway Plan career and immigration pathways for: ...
```

### Option 3: Manual Chain

Run agents manually in sequence, passing each output to the next:

1. `@profile-analyzer` → get academic assessment
2. `@college-researcher` → pass profile + assessment → get college recommendations
3. `@financial-analyst` → pass profile + colleges → get financial analysis
4. `@career-pathway` → pass profile + colleges + financials → get career/immigration pathways
5. `@report-compiler` → pass all four outputs → get compiled report
6. `@report-reviewer` → pass compiled report → get review verdict

## File Structure

```
college-guide/
├── .github/
│   └── agents/
│       ├── college-guide.agent.md        # Orchestrator
│       ├── profile-analyzer.agent.md     # Academic profile analysis
│       ├── college-researcher.agent.md   # College recommendations
│       ├── financial-analyst.agent.md    # Financial analysis
│       ├── career-pathway.agent.md       # Career & immigration pathways
│       ├── report-compiler.agent.md      # Report compilation
│       └── report-reviewer.agent.md      # Report review & approval
├── output/                               # Generated reports
├── AGENTS.md                             # Project conventions
└── README.md                             # This file
```

## Review Loop

The orchestrator includes a built-in review loop:

1. After the Report Compiler produces a draft, the Report Reviewer scores it across 5 dimensions (Completeness, Accuracy, Consistency, Actionability, Visa Compliance)
2. If any dimension scores below 7/10 or there are Critical findings, the report is sent back for revision
3. Maximum 3 revision cycles before forced finalization
4. The final report includes the reviewer's approval status

## Domain Specialization

This workflow is specialized for **H-4/immigrant STEM families** and covers:

- H-4 visa in-state tuition eligibility by state
- FAFSA ineligibility and merit-only aid strategy
- STEM CIP code verification for OPT/STEM OPT eligibility
- H-1B sponsorship rates by major and career path
- Immigration pathways (EB-1, EB-2, EB-3, NIW) with country-of-birth impact
- BS vs BS/MS comparison for visa optimization
- Grade-level appropriate action plans

## Sample Student Profile

A sample student profile (Divija Mondal) is embedded in the orchestrator agent. If no profile is provided, the orchestrator will use this sample to demonstrate the full workflow.
