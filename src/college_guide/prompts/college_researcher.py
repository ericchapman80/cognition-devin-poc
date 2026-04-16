"""Prompt templates for the College Researcher agent."""

SYSTEM_PROMPT = """You are an expert college admissions researcher specializing in \
STEM programs for H-4/immigrant families in the United States. You have deep knowledge of:
- University rankings for specific STEM majors (especially CS, Data Science, Engineering)
- In-state vs out-of-state tuition policies for visa holders
- H-4 dependent in-state tuition eligibility by state
- Merit scholarship availability for non-resident aliens
- Career placement rates and outcomes by program

Always respond in valid JSON format with the following structure:
{
    "executive_summary": "3-5 sentence overview of top recommendation and key factors",
    "in_state_colleges": [
        {
            "name": "University Name",
            "state": "XX",
            "program_name": "BS Computer Science",
            "program_rank": 8,
            "annual_tuition": 16500,
            "annual_room_board": 12000,
            "annual_other_costs": 3000,
            "four_year_total_cost": 66000,
            "acceptance_rate": 0.46,
            "median_gpa_range": "3.9-4.0",
            "sat_range": "1460-1570",
            "h4_in_state_eligible": true,
            "merit_aid_available": true,
            "merit_aid_details": "Description of available merit aid",
            "career_placement_rate": 0.95,
            "median_starting_salary": 125000,
            "has_bs_ms_program": true,
            "classification": "match",
            "key_strengths": "Why this school is good for this student",
            "concerns": "Any risks or downsides"
        }
    ],
    "out_of_state_colleges": [
        // Same structure as above, top 10 recommendations
    ],
    "comparison_summary": "Side-by-side comparison of best in-state vs best out-of-state"
}"""


def build_prompt(student_profile: dict, profile_analysis: str) -> str:
    """Build the college research prompt."""
    name = student_profile.get("name", "Unknown")
    state = student_profile.get("state", "Unknown")
    grade = student_profile.get("current_grade", "Unknown")
    majors = ", ".join(student_profile.get("intended_majors", []))

    academic = student_profile.get("academic_record", {})
    w_gpa = academic.get("weighted_gpa", "N/A")
    sat = academic.get("sat_score", "Not yet taken")
    sat_target = academic.get("sat_target")

    visa = student_profile.get("visa_info", {})
    student_visa = visa.get("student_visa", "Unknown")

    budget = student_profile.get("budget_per_year")
    budget_str = f"${budget:,}/year" if budget else "Not specified (optimize for value)"

    return f"""Research and recommend colleges for the following student:

## Student Summary
- **Name:** {name}
- **Grade:** {grade}
- **State of Residence:** {state}
- **Student Visa:** {student_visa}
- **Intended Majors:** {majors}
- **Weighted GPA:** {w_gpa}
- **SAT Score:** {sat or f'Target: {sat_target}'}
- **Annual Budget:** {budget_str}

## Profile Analysis (from prior assessment)
{profile_analysis}

## Requirements
1. **In-State Options First:** Present ALL strong in-state options in {state} before any \
out-of-state schools. Include state flagship, other strong public universities, and any \
private in-state universities worth considering for merit aid.

2. **Out-of-State Options (Top 10):** After in-state analysis, present the top 10 \
out-of-state colleges best-fit for the student's declared major. Include a mix of:
   - Top public universities with strong programs in {majors}
   - Private universities with generous merit scholarships to non-resident aliens
   - Schools with co-op, internship, or career pipelines

3. **For EACH college, provide:**
   - Program name and national ranking for the specific major
   - Full cost breakdown (tuition, room & board, other costs, 4-year total)
   - H-4 in-state tuition eligibility (cite state policy)
   - Merit aid availability for non-resident aliens
   - Career placement rate and median starting salary for the major
   - BS/MS accelerated program availability
   - Classification: reach, match, or safety for this student

4. **Side-by-side comparison** of best in-state vs best out-of-state options.

5. **H-4 Visa Considerations:**
   - Never assume H-4 holders qualify for FAFSA or federal aid
   - Clearly distinguish in-state tuition eligibility, institutional merit, and federal aid
   - Note which schools meet 100% demonstrated need for H-4 students

Optimize for the best long-term outcome at the lowest reasonable financial risk."""
