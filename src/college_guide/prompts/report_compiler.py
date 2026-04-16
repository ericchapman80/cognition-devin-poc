"""Prompt templates for the Report Compiler agent."""

SYSTEM_PROMPT = """You are an expert report compiler who creates comprehensive, \
well-structured college planning guides for immigrant families.

Your job is to compile analyses from multiple specialized advisors into a single, \
cohesive, parent-friendly report in markdown format.

The report MUST include ALL of the following sections in order:
1. Executive Summary (3-5 sentences)
2. Student Profile Summary
3. In-State College Recommendations (comparison tables)
4. Out-of-State College Recommendations (top 10 with comparison tables)
5. Side-by-Side Comparison (best in-state vs best out-of-state)
6. Financial Analysis & Aid Strategy
7. Major Selection & Career Safety Analysis
8. Master's Degree Strategy
9. Immigration Pathway Analysis
10. Comprehensive Action Plan (grade-appropriate timeline)
11. What Matters Most (top factors for this family)
12. Risks
13. Opportunities
14. Final Recommendation Summary
15. Weighted Decision Matrix

Use clear markdown formatting with tables, headers, bullet points, and bold text.
Write in a practical, parent-friendly tone.
Include all relevant disclaimers about financial and immigration advice.

Respond with the complete markdown report (not JSON)."""


def build_prompt(
    student_profile: dict,
    profile_analysis: str,
    college_recommendations: str,
    financial_analysis: str,
    career_pathway: str,
    revision_feedback: str | None = None,
) -> str:
    """Build the report compilation prompt."""
    name = student_profile.get("name", "Unknown")
    grade = student_profile.get("current_grade", "Unknown")
    school = student_profile.get("school_name", "Unknown")
    state = student_profile.get("state", "Unknown")
    city = student_profile.get("city", "Unknown")

    visa = student_profile.get("visa_info", {})
    parent_visa = visa.get("parent_visa", "Unknown")
    student_visa = visa.get("student_visa", "Unknown")

    revision_section = ""
    if revision_feedback:
        revision_section = f"""
## REVISION REQUIRED
The previous version of this report was reviewed and needs revision:
{revision_feedback}

Please address ALL the reviewer's feedback in this updated version.
"""

    return f"""Compile a comprehensive college planning report for the following student.
{revision_section}
## Student: {name}
- **Grade:** {grade}
- **School:** {school}, {city}, {state}
- **Parent Visa:** {parent_visa} | **Student Visa:** {student_visa}

---

## Section 1: Profile Analysis
{profile_analysis}

---

## Section 2: College Recommendations
{college_recommendations}

---

## Section 3: Financial Analysis
{financial_analysis}

---

## Section 4: Career & Immigration Pathway
{career_pathway}

---

## Instructions
Compile all the above analyses into a single, cohesive, comprehensive college planning guide.

The report should:
1. Start with "# {name}: Complete College & Career Planning Guide"
2. Include the date and student metadata at the top
3. Follow the section order specified in the system prompt
4. Use markdown tables for all comparisons
5. Be written in a practical, parent-friendly tone
6. Include specific actionable items with timelines
7. Include all financial and immigration disclaimers
8. End with a clear final recommendation summary

Make the report comprehensive enough to serve as a standalone reference document
for the family's college planning journey."""
