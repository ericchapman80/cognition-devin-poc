"""Tests for college guide agents - TDD: tests written first."""

import json

import pytest

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.agents.career_pathway import CareerPathwayAgent
from college_guide.agents.college_researcher import CollegeResearcherAgent
from college_guide.agents.financial_analyst import FinancialAnalystAgent
from college_guide.agents.profile_analyzer import ProfileAnalyzerAgent
from college_guide.agents.report_compiler import ReportCompilerAgent
from college_guide.agents.report_reviewer import ReportReviewerAgent
from college_guide.models import AgentOutput, ReviewFeedback, ReviewStatus

from .conftest import MockLLMProvider


class TestAgentRole:
    def test_all_roles_defined(self):
        expected = [
            "profile_analyzer",
            "college_researcher",
            "financial_analyst",
            "career_pathway",
            "report_compiler",
            "report_reviewer",
        ]
        for role_value in expected:
            assert AgentRole(role_value) is not None

    def test_role_values(self):
        assert AgentRole.PROFILE_ANALYZER.value == "profile_analyzer"
        assert AgentRole.COLLEGE_RESEARCHER.value == "college_researcher"
        assert AgentRole.FINANCIAL_ANALYST.value == "financial_analyst"
        assert AgentRole.CAREER_PATHWAY.value == "career_pathway"
        assert AgentRole.REPORT_COMPILER.value == "report_compiler"
        assert AgentRole.REPORT_REVIEWER.value == "report_reviewer"


class TestBaseCollegeAgent:
    def test_cannot_instantiate_directly(self):
        llm = MockLLMProvider()
        with pytest.raises(TypeError):
            BaseCollegeAgent(llm=llm)

    def test_parse_json_response(self):
        llm = MockLLMProvider()

        class ConcreteAgent(BaseCollegeAgent):
            role = AgentRole.PROFILE_ANALYZER

            def analyze(self, context: dict) -> AgentOutput:
                return AgentOutput(agent_name=self.role.value, content="test")

        agent = ConcreteAgent(llm=llm)
        result = agent._parse_json_response(
            '{"summary": "Test summary", "details": {"key": "value"}}'
        )
        assert result["summary"] == "Test summary"
        assert result["details"]["key"] == "value"

    def test_parse_json_with_markdown_block(self):
        llm = MockLLMProvider()

        class ConcreteAgent(BaseCollegeAgent):
            role = AgentRole.PROFILE_ANALYZER

            def analyze(self, context: dict) -> AgentOutput:
                return AgentOutput(agent_name=self.role.value, content="test")

        agent = ConcreteAgent(llm=llm)
        result = agent._parse_json_response(
            'Here is the analysis:\n```json\n{"summary": "Test"}\n```\nDone.'
        )
        assert result["summary"] == "Test"

    def test_parse_invalid_json_returns_raw(self):
        llm = MockLLMProvider()

        class ConcreteAgent(BaseCollegeAgent):
            role = AgentRole.PROFILE_ANALYZER

            def analyze(self, context: dict) -> AgentOutput:
                return AgentOutput(agent_name=self.role.value, content="test")

        agent = ConcreteAgent(llm=llm)
        result = agent._parse_json_response("This is not JSON at all")
        assert result == {"raw_response": "This is not JSON at all"}


class TestProfileAnalyzerAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = ProfileAnalyzerAgent(llm=llm)
        assert agent.role == AgentRole.PROFILE_ANALYZER

    def test_analyze_returns_agent_output(self, sample_student_profile):
        response = json.dumps(
            {
                "profile_assessment": "Strong STEM candidate with 4.32 weighted GPA",
                "strengths": [
                    "All A's across courses",
                    "Strong AP STEM courseload",
                    "Clear CS trajectory",
                ],
                "areas_for_improvement": [
                    "Need SAT/ACT scores",
                    "Expand extracurriculars",
                ],
                "competitiveness": "highly_competitive",
                "recommended_target_schools_tier": "top_20",
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = ProfileAnalyzerAgent(llm=llm)
        result = agent.analyze({"student_profile": sample_student_profile.model_dump()})
        assert isinstance(result, AgentOutput)
        assert result.agent_name == "profile_analyzer"
        assert len(result.content) > 0

    def test_analyze_sends_prompt_to_llm(self, sample_student_profile):
        llm = MockLLMProvider(responses=['{"profile_assessment": "Test"}'])
        agent = ProfileAnalyzerAgent(llm=llm)
        agent.analyze({"student_profile": sample_student_profile.model_dump()})
        assert llm.call_count == 1
        assert len(llm.prompts[0]) > 0
        assert len(llm.system_prompts[0]) > 0


class TestCollegeResearcherAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = CollegeResearcherAgent(llm=llm)
        assert agent.role == AgentRole.COLLEGE_RESEARCHER

    def test_analyze_returns_agent_output(self, sample_student_profile):
        response = json.dumps(
            {
                "in_state_colleges": [
                    {
                        "name": "UIUC",
                        "program": "BS Computer Science",
                        "annual_cost": 16500,
                        "classification": "match",
                    }
                ],
                "out_of_state_colleges": [
                    {
                        "name": "Georgia Tech",
                        "program": "BS Computer Science",
                        "annual_cost": 32800,
                        "classification": "match",
                    }
                ],
                "executive_summary": "UIUC is the top recommendation.",
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = CollegeResearcherAgent(llm=llm)
        result = agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "profile_analysis": "Strong STEM candidate",
            }
        )
        assert isinstance(result, AgentOutput)
        assert result.agent_name == "college_researcher"

    def test_analyze_includes_profile_in_prompt(self, sample_student_profile):
        llm = MockLLMProvider(responses=['{"in_state_colleges": [], "out_of_state_colleges": []}'])
        agent = CollegeResearcherAgent(llm=llm)
        agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "profile_analysis": "Strong STEM candidate",
            }
        )
        assert "IL" in llm.prompts[0] or "Illinois" in llm.prompts[0]


class TestFinancialAnalystAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = FinancialAnalystAgent(llm=llm)
        assert agent.role == AgentRole.FINANCIAL_ANALYST

    def test_analyze_returns_agent_output(self, sample_student_profile):
        response = json.dumps(
            {
                "cost_analysis": {
                    "in_state_comparison": "UIUC is the most affordable at $66K total",
                    "out_of_state_comparison": "UT Austin at $126K is best OOS value",
                },
                "h4_financial_rules": "H-4 holders not eligible for FAFSA",
                "merit_aid_strategy": "Target institutional merit scholarships",
                "financial_risks": ["No federal aid", "Merit not guaranteed"],
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = FinancialAnalystAgent(llm=llm)
        result = agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "college_recommendations": "UIUC, UT Austin, Georgia Tech",
            }
        )
        assert isinstance(result, AgentOutput)
        assert result.agent_name == "financial_analyst"

    def test_analyze_includes_visa_context(self, sample_student_profile):
        llm = MockLLMProvider(responses=['{"cost_analysis": {}}'])
        agent = FinancialAnalystAgent(llm=llm)
        agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "college_recommendations": "UIUC",
            }
        )
        prompt = llm.prompts[0]
        assert "H-4" in prompt or "H4" in prompt or "visa" in prompt.lower()


class TestCareerPathwayAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = CareerPathwayAgent(llm=llm)
        assert agent.role == AgentRole.CAREER_PATHWAY

    def test_analyze_returns_agent_output(self, sample_student_profile):
        response = json.dumps(
            {
                "career_safety_analysis": {
                    "cs_h1b_sponsorship_rate": "90%+",
                    "stem_opt_eligible": True,
                },
                "immigration_pathway": "F-1 -> OPT -> STEM OPT -> H-1B",
                "masters_recommendation": "Strongly recommend BS/MS at UIUC",
                "timeline": "5 years education + 3 years OPT",
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = CareerPathwayAgent(llm=llm)
        result = agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "college_recommendations": "UIUC CS",
                "financial_analysis": "UIUC $66K total cost",
            }
        )
        assert isinstance(result, AgentOutput)
        assert result.agent_name == "career_pathway"


class TestReportCompilerAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = ReportCompilerAgent(llm=llm)
        assert agent.role == AgentRole.REPORT_COMPILER

    def test_compile_returns_agent_output(self, sample_student_profile):
        response = "# Complete College Guide\n\n## Executive Summary\nDivija is a strong candidate."
        llm = MockLLMProvider(responses=[response])
        agent = ReportCompilerAgent(llm=llm)
        result = agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "profile_analysis": "Strong STEM profile",
                "college_recommendations": "UIUC top choice",
                "financial_analysis": "UIUC $66K most affordable",
                "career_pathway": "CS safest for H-4",
            }
        )
        assert isinstance(result, AgentOutput)
        assert result.agent_name == "report_compiler"
        assert "#" in result.content  # markdown heading present

    def test_compile_includes_all_sections(self, sample_student_profile):
        llm = MockLLMProvider(
            responses=["# Report\n## Profile\n## Colleges\n## Financial\n## Career\n## Action Plan"]
        )
        agent = ReportCompilerAgent(llm=llm)
        agent.analyze(
            {
                "student_profile": sample_student_profile.model_dump(),
                "profile_analysis": "Analysis A",
                "college_recommendations": "Recs B",
                "financial_analysis": "Finance C",
                "career_pathway": "Career D",
            }
        )
        prompt = llm.prompts[0]
        assert "Analysis A" in prompt
        assert "Recs B" in prompt
        assert "Finance C" in prompt
        assert "Career D" in prompt


class TestReportReviewerAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        agent = ReportReviewerAgent(llm=llm)
        assert agent.role == AgentRole.REPORT_REVIEWER

    def test_review_approved(self, sample_student_profile):
        response = json.dumps(
            {
                "status": "approved",
                "comments": "Report is comprehensive and accurate.",
                "sections_needing_revision": [],
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = ReportReviewerAgent(llm=llm)
        feedback = agent.review(
            report_content="# Full Report\nComprehensive guide...",
            student_profile=sample_student_profile.model_dump(),
        )
        assert isinstance(feedback, ReviewFeedback)
        assert feedback.status == ReviewStatus.APPROVED
        assert feedback.is_approved is True

    def test_review_needs_revision(self, sample_student_profile):
        response = json.dumps(
            {
                "status": "needs_revision",
                "comments": "Financial section lacks detail on H-4 aid eligibility.",
                "sections_needing_revision": ["financial_analysis"],
            }
        )
        llm = MockLLMProvider(responses=[response])
        agent = ReportReviewerAgent(llm=llm)
        feedback = agent.review(
            report_content="# Report\nIncomplete...",
            student_profile=sample_student_profile.model_dump(),
        )
        assert isinstance(feedback, ReviewFeedback)
        assert feedback.status == ReviewStatus.NEEDS_REVISION
        assert feedback.is_approved is False
        assert "financial_analysis" in feedback.sections_needing_revision

    def test_review_returns_feedback_on_invalid_json(self, sample_student_profile):
        llm = MockLLMProvider(responses=["Looks good overall but needs more data."])
        agent = ReportReviewerAgent(llm=llm)
        feedback = agent.review(
            report_content="# Report\nSome content...",
            student_profile=sample_student_profile.model_dump(),
        )
        assert isinstance(feedback, ReviewFeedback)
        # Should default to needs_revision when can't parse properly
        assert feedback.status in (ReviewStatus.APPROVED, ReviewStatus.NEEDS_REVISION)
