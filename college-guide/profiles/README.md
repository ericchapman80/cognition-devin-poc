# Student Profiles

Place each student's documents in a subfolder named after the student.

## Folder Structure

```
profiles/
├── {Student-Name}/
│   ├── profile.md          ← Required: structured student profile
│   ├── transcript.pdf      ← Recommended: high school transcript
│   ├── test-scores.pdf     ← Optional: PSAT/SAT/ACT score reports
│   ├── resume.pdf          ← Optional: activities resume / brag sheet
│   ├── awards.pdf          ← Optional: awards and certificates
│   └── ...                 ← Any other supporting documents
├── {Another-Student}/
│   └── ...
└── README.md               ← This file
```

## How to Add a New Student

1. Create a folder: `profiles/{FirstName-LastName}/` (use hyphens, no spaces)
2. Copy the `profile.md` template from `profiles/Divija-Mondal/profile.md`
3. Fill in all sections with the student's information
4. Drop any supporting PDFs (transcript, test scores, resume, awards) into the same folder
5. Run the orchestrator: `@college-guide Generate a report for the student in profiles/{FirstName-LastName}/`

## What the Agents Read

- **Profile Analyzer** reads `profile.md` and any PDFs in the student folder to assess academics
- **College Researcher** uses the profile analysis to research best-fit colleges
- **Financial Analyst** uses the profile and college list to analyze costs
- **Career Pathway** uses all prior outputs to plan career and immigration pathways
- **Report Compiler** compiles everything into `output/{StudentName}-College-Guide.md`

## Supported File Types

| File Type | What It's Used For |
|-----------|-------------------|
| `profile.md` | Primary structured data — GPA, courses, test scores, visa status, intended major |
| `transcript.pdf` | Verify course history, GPA, class rank, school info |
| `test-scores.pdf` | Verify SAT/ACT/PSAT/AP scores |
| `resume.pdf` | Extracurriculars, leadership, community service, work experience |
| `awards.pdf` | Academic honors, competition results, certifications |
| Other PDFs/docs | Any additional context (IEP, recommendation letters, essays, etc.) |

## Tips

- The more information you provide, the more tailored the recommendations will be
- PDF transcripts help the agents verify course names, grades, and GPA calculations
- If test scores aren't available yet, note "planned" dates in `profile.md` — the agents will project target score ranges
- For H-4/immigrant families, always include visa status and country of birth — these critically affect financial aid and immigration pathway analysis
