"""Prompt templates for the Profile Analyzer agent."""

SYSTEM_PROMPT = """You are an expert academic profile analyzer specializing in evaluating \
high school students for college admissions, particularly for H-4/immigrant STEM students \
in the United States.

Your role is to assess the student's academic strengths, identify areas for improvement, \
and determine their competitiveness for various college tiers.

Always respond in valid JSON format with the following structure:
{
    "profile_assessment": "Overall assessment of the student's profile",
    "strengths": ["list of key academic strengths"],
    "areas_for_improvement": ["list of areas to improve"],
    "competitiveness": "highly_competitive|competitive|moderately_competitive|developing",
    "recommended_target_schools_tier": "one of: top_10, top_20, top_50, top_100",
    "gpa_analysis": "Analysis of GPA trajectory and rigor",
    "course_rigor_assessment": "Assessment of AP/Honors course load",
    "stem_readiness": "Assessment of STEM preparation",
    "testing_strategy": "Recommendations for standardized testing",
    "extracurricular_recommendations": ["list of recommended activities"]
}"""


def build_prompt(student_profile: dict) -> str:
    """Build the analysis prompt from a student profile."""
    name = student_profile.get("name", "Unknown")
    grade = student_profile.get("current_grade", "Unknown")
    state = student_profile.get("state", "Unknown")
    school = student_profile.get("school_name", "Unknown")

    academic = student_profile.get("academic_record", {})
    w_gpa = academic.get("weighted_gpa", "N/A")
    uw_gpa = academic.get("unweighted_gpa", "N/A")
    courses = academic.get("courses", [])
    sat = academic.get("sat_score", "Not yet taken")
    act = academic.get("act_score", "Not yet taken")
    sat_target = academic.get("sat_target")
    act_target = academic.get("act_target")

    visa = student_profile.get("visa_info", {})
    parent_visa = visa.get("parent_visa", "Unknown")
    student_visa = visa.get("student_visa", "Unknown")
    country = visa.get("country_of_birth", "Unknown")

    majors = ", ".join(student_profile.get("intended_majors", []))

    course_list = ""
    for c in courses:
        course_list += f"  - {c.get('name', 'Unknown')}: Grade {c.get('grade', 'N/A')}"
        course_list += f" ({c.get('course_type', 'Regular')}, {c.get('subject_area', 'General')})\n"

    return f"""Analyze the following student's academic profile for college admissions:

## Student Information
- **Name:** {name}
- **Current Grade:** {grade}
- **School:** {school}
- **State:** {state}
- **Parent Visa:** {parent_visa}
- **Student Visa:** {student_visa}
- **Country of Birth:** {country}
- **Intended Majors:** {majors}

## Academic Record
- **Weighted GPA:** {w_gpa}
- **Unweighted GPA:** {uw_gpa}
- **SAT Score:** {sat}
- **ACT Score:** {act}
- **SAT Target:** {sat_target or 'Not set'}
- **ACT Target:** {act_target or 'Not set'}

## Courses
{course_list}

Provide a comprehensive assessment of this student's profile, including:
1. Overall competitiveness for top STEM programs
2. Strength of course rigor (AP/Honors load)
3. GPA trajectory analysis
4. Testing strategy recommendations
5. Areas where the student should focus to strengthen their application
6. Extracurricular recommendations for STEM-focused applicants

Consider the student's H-4 visa status and its implications for admissions strategy."""
