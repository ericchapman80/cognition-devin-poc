"""Prompt templates for the Career Pathway agent."""

SYSTEM_PROMPT = """You are an expert career and immigration pathway advisor for H-4/immigrant \
STEM students in the United States. You combine deep knowledge of:
- STEM career planning and job market analysis
- H-1B visa sponsorship rates by industry and major
- OPT and STEM OPT work authorization timelines
- Immigration pathways (EB-1, EB-2, EB-3, NIW) and green card timelines
- Master's degree strategy and its impact on H-1B lottery odds
- Country-of-birth impact on immigration timelines (India/China backlogs)

Always respond in valid JSON format with the following structure:
{
    "career_safety_analysis": {
        "primary_major_assessment": "Assessment of the student's intended major for career safety",
        "h1b_sponsorship_rate": "Estimated H-1B sponsorship rate for this career path",
        "stem_opt_eligible": true,
        "job_market_depth": "Assessment of job market size and opportunity",
        "salary_meets_prevailing_wage": true,
        "career_portability": "International career transferability assessment"
    },
    "major_recommendations": {
        "tier_1_safest": ["list of safest majors for visa holders"],
        "tier_2_strong": ["list of strong but slightly riskier majors"],
        "tier_3_viable": ["list of viable but riskier majors"],
        "tier_4_avoid": ["list of majors to avoid for visa holders"]
    },
    "immigration_pathway": "Detailed F-1 -> OPT -> STEM OPT -> H-1B -> Green Card timeline",
    "immigration_pathways_comparison": "Comparison of EB-1, EB-2, EB-3, NIW paths",
    "country_of_birth_impact": "Impact of country of birth on green card timeline",
    "masters_recommendation": "BS vs BS+MS analysis with H-1B lottery odds comparison",
    "masters_financial_analysis": "Cost-benefit of MS degree",
    "bs_ms_programs": "Recommended BS/MS accelerated programs at top schools",
    "timeline": "Complete timeline from college through citizenship",
    "risks": ["list of immigration and career risks"],
    "acceleration_strategies": ["strategies to speed up immigration pathway"],
    "disclaimer": "Immigration disclaimer text"
}"""


def build_prompt(
    student_profile: dict, college_recommendations: str, financial_analysis: str
) -> str:
    """Build the career pathway analysis prompt."""
    name = student_profile.get("name", "Unknown")
    grade = student_profile.get("current_grade", "Unknown")
    majors = ", ".join(student_profile.get("intended_majors", []))

    visa = student_profile.get("visa_info", {})
    parent_visa = visa.get("parent_visa", "Unknown")
    student_visa = visa.get("student_visa", "Unknown")
    country = visa.get("country_of_birth", "Unknown")

    return f"""Provide a comprehensive career and immigration pathway analysis:

## Student Context
- **Name:** {name}
- **Current Grade:** {grade}
- **Parent Visa:** {parent_visa}
- **Student Visa:** {student_visa}
- **Country of Birth:** {country}
- **Intended Majors:** {majors}

## College Recommendations (from prior research)
{college_recommendations}

## Financial Analysis (from prior analysis)
{financial_analysis}

## Analysis Requirements

### 1. Career Safety Analysis for Visa Holders
For the student's intended major ({majors}), evaluate:
- STEM CIP Code eligibility (required for 36-month STEM OPT)
- H-1B sponsorship rate in this field
- Job market depth (number of open roles annually)
- Whether common employers require US citizenship or security clearance
- Whether starting salary meets H-1B prevailing wage thresholds
- International career portability if US immigration fails

### 2. Major Recommendations Ranked by Career Safety
Rank majors into tiers based on:
- H-1B sponsorship rate
- Job market size
- Salary levels
- STEM OPT eligibility

### 3. Complete Immigration Timeline
Present the full path: H-4 -> F-1 (college) -> OPT (12 mo) -> STEM OPT (+24 mo) -> H-1B -> GC
Include:
- Expected OPT employment rate
- H-1B lottery odds (regular vs advanced-degree cap)
- Green card timeline by EB category
- Country-of-birth impact ({country})

### 4. Master's Degree Strategy
Compare BS-only vs BS+MS:
- H-1B lottery odds improvement (65% -> 80-85%)
- Salary premium
- Additional cost and time
- Funding availability (TA/RA)
- Best BS/MS accelerated programs at recommended schools

### 5. Immigration Pathway Comparison
Compare all viable paths: EB-2, EB-2 NIW, EB-1A, EB-1B, EB-3, H-1B -> GC
For each, provide timeline to green card and citizenship, requirements, and risk level.

### 6. Fastest Path Analysis
Rank immigration pathways from fastest to slowest for this student's profile.
Factor in country of birth for backlog estimates.

Include standard immigration disclaimer."""
