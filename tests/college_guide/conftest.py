"""Shared fixtures for college guide tests."""

import pytest

from college_guide.models import (
    AcademicRecord,
    CourseEntry,
    StudentProfile,
    VisaInfo,
)


@pytest.fixture
def sample_student_profile() -> StudentProfile:
    """Create a sample student profile based on Divija Mondal."""
    return StudentProfile(
        name="Divija Mondal",
        current_grade=10,
        graduation_year=2028,
        school_name="Adlai E. Stevenson High School",
        city="Deerfield",
        state="IL",
        visa_info=VisaInfo(
            parent_visa="H-1B",
            student_visa="H-4",
            country_of_birth="India",
        ),
        intended_majors=["Computer Science", "Data Science", "Software Engineering"],
        academic_record=AcademicRecord(
            weighted_gpa=4.32,
            unweighted_gpa=3.96,
            courses=[
                CourseEntry(
                    name="AP Computer Science A",
                    grade="A",
                    course_type="AP",
                    subject_area="STEM",
                ),
                CourseEntry(
                    name="AP Physics 1",
                    grade="A",
                    course_type="AP",
                    subject_area="STEM",
                ),
                CourseEntry(
                    name="AP Precalculus",
                    grade="A",
                    course_type="AP",
                    subject_area="STEM",
                ),
                CourseEntry(
                    name="AP Comparative Gov & Politics",
                    grade="A",
                    course_type="AP",
                    subject_area="Humanities",
                ),
                CourseEntry(
                    name="Computer Programming 1",
                    grade="A",
                    course_type="Regular",
                    subject_area="STEM",
                ),
                CourseEntry(
                    name="Computer Programming 2",
                    grade="A",
                    course_type="Regular",
                    subject_area="STEM",
                ),
            ],
            sat_score=None,
            act_score=None,
            sat_target=1500,
            act_target=34,
        ),
        budget_per_year=None,
        preferences={"campus_environment": "traditional", "region": "Midwest preferred"},
    )


@pytest.fixture
def mock_llm_response():
    """Factory fixture for creating mock LLM responses."""

    def _make_response(content: str) -> str:
        return content

    return _make_response


class MockLLMProvider:
    """Mock LLM provider for testing agents without real LLM calls."""

    def __init__(self, responses: list[str] | None = None):
        self.responses = responses or []
        self.call_count = 0
        self.prompts: list[str] = []
        self.system_prompts: list[str] = []

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        self.prompts.append(prompt)
        self.system_prompts.append(system_prompt)
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        self.call_count += 1
        return '{"summary": "Mock response", "signal": "neutral", "confidence": 50}'

    def is_available(self) -> bool:
        return True
