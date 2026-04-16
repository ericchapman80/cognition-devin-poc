"""Data models for the college guide multi-agent workflow."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class VisaInfo(BaseModel):
    """Immigration/visa information for the student's family."""

    parent_visa: str
    student_visa: str
    country_of_birth: str | None = None

    @property
    def is_h4_dependent(self) -> bool:
        return self.student_visa.upper() == "H-4"


class CourseEntry(BaseModel):
    """A single course on the student's transcript."""

    name: str
    grade: str
    course_type: str = "Regular"  # AP, Honors, Accelerated, Regular
    subject_area: str = "General"  # STEM, Humanities, Arts, General

    @property
    def is_ap(self) -> bool:
        return self.course_type.upper() == "AP"

    @property
    def is_stem(self) -> bool:
        return self.subject_area.upper() == "STEM"


class AcademicRecord(BaseModel):
    """Student's academic record including GPA, courses, and test scores."""

    weighted_gpa: float
    unweighted_gpa: float
    courses: list[CourseEntry] = Field(default_factory=list)
    sat_score: int | None = None
    act_score: int | None = None
    sat_target: int | None = None
    act_target: int | None = None

    @property
    def ap_course_count(self) -> int:
        return sum(1 for c in self.courses if c.is_ap)

    @property
    def stem_course_count(self) -> int:
        return sum(1 for c in self.courses if c.is_stem)


class StudentProfile(BaseModel):
    """Complete student profile for college planning."""

    name: str
    current_grade: int = Field(ge=9, le=12)
    graduation_year: int
    school_name: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    visa_info: VisaInfo
    intended_majors: list[str] = Field(min_length=1)
    academic_record: AcademicRecord
    budget_per_year: int | None = None
    preferences: dict = Field(default_factory=dict)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        return v.upper()

    @property
    def is_immigrant_family(self) -> bool:
        return self.visa_info.parent_visa in ("H-1B", "L-1", "O-1", "E-2")


class CollegeRecommendation(BaseModel):
    """A single college recommendation with detailed comparison data."""

    name: str
    state: str = ""
    is_in_state: bool = False
    program_name: str = ""
    program_rank: int | None = None
    annual_tuition: float = 0
    annual_room_board: float = 0
    annual_other_costs: float = 0
    four_year_total_cost: float = 0
    acceptance_rate: float | None = None
    median_gpa_range: str = ""
    sat_range: str = ""
    h4_in_state_eligible: bool | None = None
    merit_aid_available: bool | None = None
    merit_aid_details: str = ""
    career_placement_rate: float | None = None
    median_starting_salary: int | None = None
    has_bs_ms_program: bool | None = None
    classification: str = "match"

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        allowed = {"reach", "match", "safety"}
        if v.lower() not in allowed:
            raise ValueError(f"classification must be one of {allowed}, got '{v}'")
        return v.lower()

    @property
    def total_annual_cost(self) -> float:
        return self.annual_tuition + self.annual_room_board + self.annual_other_costs


class AgentOutput(BaseModel):
    """Output from a sub-agent."""

    agent_name: str
    content: str
    structured_data: dict | None = None


class ReviewStatus(str, Enum):
    """Status of report review."""

    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"


class ReviewFeedback(BaseModel):
    """Feedback from the report reviewer agent."""

    status: ReviewStatus
    comments: str = ""
    sections_needing_revision: list[str] = Field(default_factory=list)

    @property
    def is_approved(self) -> bool:
        return self.status == ReviewStatus.APPROVED


class FinalReport(BaseModel):
    """The finalized college planning report."""

    student_name: str
    report_date: str
    sections: dict[str, str] = Field(default_factory=dict)
    review_status: ReviewStatus
    review_iterations: int = 0
    markdown_content: str = ""

    @property
    def is_finalized(self) -> bool:
        return self.review_status == ReviewStatus.APPROVED
