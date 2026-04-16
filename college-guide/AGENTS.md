# AGENTS.md — College Guide Multi-Agent Workflow

## Project Overview
This is a multi-agent orchestration workflow for generating comprehensive college planning reports tailored to **H-4/immigrant STEM students** in the United States. It demonstrates a chain of specialized agents:

**Profile Analyzer → College Researcher → Financial Analyst → Career Pathway Advisor → Report Compiler → Report Reviewer**

The orchestrator (`college-guide`) chains all six agents automatically, with a review loop that sends the report back for revision if the reviewer finds issues.

## Domain Context
- **Target audience:** H-1B/H-4 visa families planning undergraduate STEM education
- **Sample student profile:** John Doe — Grade 10, H-4 visa, 4.32 weighted GPA, AP STEM track, Illinois resident (test data — replace with real student)
- **Key concerns:** In-state tuition eligibility for H-4, merit scholarship availability, STEM career placement, H-1B sponsorship pipeline, immigration pathway planning

## Repository Structure
```
college-guide/
  .github/
    agents/
      profile-analyzer.agent.md       📊 Analyzes student academic profile
      college-researcher.agent.md      🏫 Recommends in-state and out-of-state colleges
      financial-analyst.agent.md       💰 Analyzes costs, aid, and ROI
      career-pathway.agent.md          🛤️ Plans career and immigration pathways
      report-compiler.agent.md         📝 Compiles all outputs into unified report
      report-reviewer.agent.md         🔍 Reviews report quality and completeness
      college-guide.agent.md           🎯 Orchestrator — chains all six automatically
  profiles/                            📁 Student profile folders (input)
    {Student-Name}/
      profile.md                       📄 Structured student profile data
      transcript.pdf                   📄 High school transcript (PDF)
      test-scores.pdf                  📄 SAT/ACT/PSAT scores (PDF)
      resume.pdf                       📄 Activities resume (PDF)
      awards.pdf                       📄 Awards and certificates (PDF)
  output/                              📂 Generated reports saved here
  AGENTS.md                            📋 This file — conventions used by all agents
  README.md                            📖 Usage instructions
```

## Input: Student Profiles
- Place each student's data in `profiles/{Student-Name}/` (use hyphens, no spaces)
- Each folder MUST have a `profile.md` with structured data (GPA, courses, visa status, intended major, etc.)
- Drop supporting PDFs (transcript, test scores, resume, awards) into the same folder
- The Profile Analyzer reads `profile.md` and all PDFs to build a complete picture
- The more documents you provide, the more accurate the analysis will be

## Output Conventions
- All generated reports are saved to the `output/` folder as markdown files
- File naming: `{StudentName}-College-Guide.md` (e.g., `John-Doe-College-Guide.md`)
- Reports must be comprehensive markdown with clear sections, tables, and actionable advice
- Write like a **practical admissions + immigration strategist** speaking to a parent

## Data Accuracy Rules
- **Never assume** H-4 visa holders qualify for FAFSA or federal financial aid
- **Always distinguish** between in-state tuition eligibility, institutional/merit scholarships, and federal aid
- **Always include disclaimers** for legal/immigration advice
- Use major-specific rankings, salary data, and placement rates (not university-wide averages)
- Apply 3% annual inflation to project 4-year and 5-year cost totals
- Cite sources when using web search data

## Required Disclaimers
Every report must include:
> "This is not legal advice. Please verify residency classification with the university's residency office and consult a qualified immigration attorney if needed."

> "This is not legal or immigration advice. Immigration laws change frequently. Consult a qualified immigration attorney for pathway planning specific to your family's situation, country of birth, and visa status."

## Commands
| Task | Command |
|------|---------|
| Generate report from profile folder | `@college-guide Generate a report for the student in profiles/{Student-Name}/` |
| Generate report (inline profile) | `@college-guide <student profile details>` |
| Analyze profile only | `@profile-analyzer <student details>` |
| Research colleges only | `@college-researcher <profile + analysis>` |
| Financial analysis only | `@financial-analyst <profile + colleges>` |
| Career pathway only | `@career-pathway <profile + colleges + financials>` |
