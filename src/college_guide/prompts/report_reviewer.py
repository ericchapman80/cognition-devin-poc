"""Prompt templates for the Report Reviewer agent."""

SYSTEM_PROMPT = """You are a meticulous report reviewer and quality assurance expert \
for college planning guides targeted at H-4/immigrant STEM families.

Your job is to review compiled reports for:
1. **Completeness** - All required sections present and thorough
2. **Accuracy** - Financial figures reasonable, visa rules correct, rankings plausible
3. **Consistency** - No contradictions between sections
4. **Actionability** - Clear, specific next steps with timelines
5. **H-4/Visa Compliance** - Correct treatment of federal aid ineligibility, in-state rules
6. **Disclaimers** - Financial and immigration disclaimers included

ALWAYS respond in valid JSON format:
{
    "status": "approved" or "needs_revision",
    "comments": "Overall assessment of report quality",
    "completeness_score": 1-10,
    "accuracy_score": 1-10,
    "consistency_score": 1-10,
    "actionability_score": 1-10,
    "visa_compliance_score": 1-10,
    "sections_needing_revision": ["list of section names that need improvement"],
    "specific_issues": ["list of specific issues found"],
    "strengths": ["list of report strengths"]
}

Approve the report (status: "approved") if ALL scores are 7 or above.
Request revision (status: "needs_revision") if ANY score is below 7."""


def build_review_prompt(report_content: str, student_profile: dict) -> str:
    """Build the review prompt."""
    name = student_profile.get("name", "Unknown")
    state = student_profile.get("state", "Unknown")
    visa = student_profile.get("visa_info", {})
    student_visa = visa.get("student_visa", "Unknown")
    majors = ", ".join(student_profile.get("intended_majors", []))

    return f"""Review the following college planning report for quality and completeness.

## Student Context (for verification)
- **Name:** {name}
- **State:** {state}
- **Student Visa:** {student_visa}
- **Intended Majors:** {majors}

## Report to Review
{report_content}

## Review Checklist

### Completeness
- [ ] Executive Summary present (3-5 sentences)
- [ ] Student Profile Summary
- [ ] In-State College Recommendations with comparison tables
- [ ] Out-of-State College Recommendations (top 10)
- [ ] Side-by-Side Comparison table
- [ ] Financial Analysis with cost breakdowns
- [ ] Career Safety Analysis for visa holders
- [ ] Master's Degree Strategy
- [ ] Immigration Pathway Analysis
- [ ] Action Plan with grade-appropriate timeline
- [ ] What Matters Most section
- [ ] Risks section
- [ ] Opportunities section
- [ ] Final Recommendation Summary
- [ ] Decision Matrix

### Accuracy
- [ ] Cost figures are reasonable for the schools listed
- [ ] In-state tuition eligibility for H-4 in {state} correctly stated
- [ ] Federal aid ineligibility for H-4 clearly stated
- [ ] Program rankings are plausible
- [ ] Salary figures are reasonable for the majors listed

### Visa Compliance
- [ ] Never assumes H-4 qualifies for FAFSA
- [ ] Distinguishes in-state tuition, institutional merit, and federal aid
- [ ] Includes financial disclaimer
- [ ] Includes immigration disclaimer
- [ ] Correctly describes OPT/STEM OPT/H-1B timeline

Provide your assessment in the specified JSON format."""
