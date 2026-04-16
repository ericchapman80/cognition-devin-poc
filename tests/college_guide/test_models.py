"""Tests for college guide data models - TDD: tests written first."""

import pytest

from college_guide.models import (
    AcademicRecord,
    AgentOutput,
    CollegeRecommendation,
    CourseEntry,
    FinalReport,
    ReviewFeedback,
    ReviewStatus,
    StudentProfile,
    VisaInfo,
)


class TestVisaInfo:
    def test_create_visa_info(self):
        visa = VisaInfo(
            parent_visa="H-1B",
            student_visa="H-4",
            country_of_birth="India",
        )
        assert visa.parent_visa == "H-1B"
        assert visa.student_visa == "H-4"
        assert visa.country_of_birth == "India"

    def test_visa_info_defaults(self):
        visa = VisaInfo(parent_visa="H-1B", student_visa="H-4")
        assert visa.country_of_birth is None

    def test_visa_info_is_h4(self):
        visa = VisaInfo(parent_visa="H-1B", student_visa="H-4")
        assert visa.is_h4_dependent is True

    def test_visa_info_not_h4(self):
        visa = VisaInfo(parent_visa="L-1", student_visa="L-2")
        assert visa.is_h4_dependent is False


class TestCourseEntry:
    def test_create_course(self):
        course = CourseEntry(
            name="AP Computer Science A",
            grade="A",
            course_type="AP",
            subject_area="STEM",
        )
        assert course.name == "AP Computer Science A"
        assert course.grade == "A"
        assert course.course_type == "AP"
        assert course.subject_area == "STEM"

    def test_course_is_ap(self):
        course = CourseEntry(name="AP Physics 1", grade="A", course_type="AP", subject_area="STEM")
        assert course.is_ap is True

    def test_course_is_not_ap(self):
        course = CourseEntry(
            name="Chemistry", grade="A", course_type="Honors", subject_area="STEM"
        )
        assert course.is_ap is False

    def test_course_is_stem(self):
        course = CourseEntry(
            name="AP Computer Science A",
            grade="A",
            course_type="AP",
            subject_area="STEM",
        )
        assert course.is_stem is True


class TestAcademicRecord:
    def test_create_academic_record(self):
        record = AcademicRecord(
            weighted_gpa=4.32,
            unweighted_gpa=3.96,
            courses=[
                CourseEntry(
                    name="AP Computer Science A",
                    grade="A",
                    course_type="AP",
                    subject_area="STEM",
                ),
            ],
        )
        assert record.weighted_gpa == 4.32
        assert record.unweighted_gpa == 3.96
        assert len(record.courses) == 1

    def test_ap_course_count(self):
        record = AcademicRecord(
            weighted_gpa=4.32,
            unweighted_gpa=3.96,
            courses=[
                CourseEntry(name="AP CS A", grade="A", course_type="AP", subject_area="STEM"),
                CourseEntry(name="AP Physics", grade="A", course_type="AP", subject_area="STEM"),
                CourseEntry(name="Chem", grade="A", course_type="Regular", subject_area="STEM"),
            ],
        )
        assert record.ap_course_count == 2

    def test_stem_course_count(self):
        record = AcademicRecord(
            weighted_gpa=4.32,
            unweighted_gpa=3.96,
            courses=[
                CourseEntry(name="AP CS A", grade="A", course_type="AP", subject_area="STEM"),
                CourseEntry(
                    name="AP Gov", grade="A", course_type="AP", subject_area="Humanities"
                ),
                CourseEntry(name="Chem", grade="A", course_type="Regular", subject_area="STEM"),
            ],
        )
        assert record.stem_course_count == 2

    def test_test_scores_optional(self):
        record = AcademicRecord(weighted_gpa=4.0, unweighted_gpa=3.8, courses=[])
        assert record.sat_score is None
        assert record.act_score is None
        assert record.sat_target is None
        assert record.act_target is None


class TestStudentProfile:
    def test_create_student_profile(self, sample_student_profile):
        profile = sample_student_profile
        assert profile.name == "Divija Mondal"
        assert profile.current_grade == 10
        assert profile.state == "IL"
        assert profile.visa_info.student_visa == "H-4"
        assert "Computer Science" in profile.intended_majors

    def test_profile_serialization(self, sample_student_profile):
        profile = sample_student_profile
        data = profile.model_dump()
        assert isinstance(data, dict)
        assert data["name"] == "Divija Mondal"
        restored = StudentProfile.model_validate(data)
        assert restored.name == profile.name
        assert restored.current_grade == profile.current_grade

    def test_profile_json_roundtrip(self, sample_student_profile):
        profile = sample_student_profile
        json_str = profile.model_dump_json()
        restored = StudentProfile.model_validate_json(json_str)
        assert restored.name == profile.name
        assert restored.visa_info.parent_visa == "H-1B"

    def test_profile_validation_grade_range(self):
        with pytest.raises(Exception):
            StudentProfile(
                name="Test",
                current_grade=15,
                graduation_year=2028,
                school_name="Test School",
                city="Test",
                state="IL",
                visa_info=VisaInfo(parent_visa="H-1B", student_visa="H-4"),
                intended_majors=["CS"],
                academic_record=AcademicRecord(
                    weighted_gpa=4.0, unweighted_gpa=3.8, courses=[]
                ),
            )

    def test_profile_is_immigrant_family(self, sample_student_profile):
        assert sample_student_profile.is_immigrant_family is True


class TestCollegeRecommendation:
    def test_create_recommendation(self):
        rec = CollegeRecommendation(
            name="University of Illinois Urbana-Champaign",
            state="IL",
            is_in_state=True,
            program_name="BS Computer Science",
            program_rank=8,
            annual_tuition=16500,
            annual_room_board=12000,
            annual_other_costs=3000,
            four_year_total_cost=66000,
            acceptance_rate=0.46,
            median_gpa_range="3.9-4.0",
            sat_range="1460-1570",
            h4_in_state_eligible=True,
            merit_aid_available=True,
            merit_aid_details="Illinois Scholarship up to $10K/yr",
            career_placement_rate=0.95,
            median_starting_salary=125000,
            has_bs_ms_program=True,
            classification="match",
        )
        assert rec.name == "University of Illinois Urbana-Champaign"
        assert rec.total_annual_cost == 31500
        assert rec.is_in_state is True
        assert rec.classification == "match"

    def test_total_annual_cost_calculation(self):
        rec = CollegeRecommendation(
            name="Test University",
            state="TX",
            is_in_state=False,
            program_name="BS CS",
            annual_tuition=31600,
            annual_room_board=12000,
            annual_other_costs=3000,
            four_year_total_cost=126400,
            classification="match",
        )
        assert rec.total_annual_cost == 46600

    def test_classification_values(self):
        for classification in ["reach", "match", "safety"]:
            rec = CollegeRecommendation(
                name="Test",
                state="IL",
                is_in_state=True,
                program_name="BS CS",
                annual_tuition=16500,
                four_year_total_cost=66000,
                classification=classification,
            )
            assert rec.classification == classification

    def test_invalid_classification_rejected(self):
        with pytest.raises(Exception):
            CollegeRecommendation(
                name="Test",
                state="IL",
                is_in_state=True,
                program_name="BS CS",
                annual_tuition=16500,
                four_year_total_cost=66000,
                classification="invalid_tier",
            )


class TestAgentOutput:
    def test_create_agent_output(self):
        output = AgentOutput(
            agent_name="profile_analyzer",
            content="Student has a strong STEM profile.",
            structured_data={"gpa_assessment": "excellent"},
        )
        assert output.agent_name == "profile_analyzer"
        assert "strong STEM profile" in output.content
        assert output.structured_data["gpa_assessment"] == "excellent"

    def test_agent_output_without_structured_data(self):
        output = AgentOutput(
            agent_name="college_researcher",
            content="Top recommendation: UIUC",
        )
        assert output.structured_data is None


class TestReviewFeedback:
    def test_approved_feedback(self):
        feedback = ReviewFeedback(
            status=ReviewStatus.APPROVED,
            comments="Report is comprehensive and accurate.",
            sections_needing_revision=[],
        )
        assert feedback.status == ReviewStatus.APPROVED
        assert feedback.is_approved is True

    def test_needs_revision_feedback(self):
        feedback = ReviewFeedback(
            status=ReviewStatus.NEEDS_REVISION,
            comments="Financial section needs more detail on H-4 aid.",
            sections_needing_revision=["financial_analysis"],
        )
        assert feedback.status == ReviewStatus.NEEDS_REVISION
        assert feedback.is_approved is False
        assert "financial_analysis" in feedback.sections_needing_revision


class TestFinalReport:
    def test_create_final_report(self, sample_student_profile):
        report = FinalReport(
            student_name="Divija Mondal",
            report_date="2026-04-08",
            sections={
                "executive_summary": "Strong STEM candidate...",
                "in_state_colleges": "UIUC is the top choice...",
                "out_of_state_colleges": "Top 10 OOS options...",
                "financial_analysis": "Cost breakdown...",
                "career_pathway": "CS is the safest path...",
                "action_plan": "Timeline of next steps...",
            },
            review_status=ReviewStatus.APPROVED,
            review_iterations=1,
            markdown_content="# Full Report\n...",
        )
        assert report.student_name == "Divija Mondal"
        assert report.review_status == ReviewStatus.APPROVED
        assert report.is_finalized is True
        assert len(report.sections) == 6

    def test_report_not_finalized_when_pending(self):
        report = FinalReport(
            student_name="Test",
            report_date="2026-04-08",
            sections={},
            review_status=ReviewStatus.NEEDS_REVISION,
            review_iterations=0,
            markdown_content="",
        )
        assert report.is_finalized is False
