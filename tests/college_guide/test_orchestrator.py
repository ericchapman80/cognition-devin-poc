"""Tests for the orchestrator agent - TDD: tests written first."""

import json

from college_guide.models import ReviewStatus
from college_guide.orchestrator import OrchestratorAgent

from .conftest import MockLLMProvider


class TestOrchestratorAgent:
    def test_instantiation(self):
        llm = MockLLMProvider()
        orchestrator = OrchestratorAgent(llm=llm)
        assert orchestrator is not None
        assert orchestrator.max_review_iterations == 3

    def test_custom_max_review_iterations(self):
        llm = MockLLMProvider()
        orchestrator = OrchestratorAgent(llm=llm, max_review_iterations=5)
        assert orchestrator.max_review_iterations == 5

    def test_run_generates_final_report(self, sample_student_profile):
        # Provide responses for each agent in sequence:
        # 1. ProfileAnalyzer
        # 2. CollegeResearcher
        # 3. FinancialAnalyst
        # 4. CareerPathway
        # 5. ReportCompiler
        # 6. ReportReviewer (approved on first try)
        responses = [
            json.dumps(
                {
                    "profile_assessment": "Strong STEM candidate",
                    "strengths": ["4.32 GPA", "AP STEM courses"],
                    "competitiveness": "highly_competitive",
                }
            ),
            json.dumps(
                {
                    "in_state_colleges": [{"name": "UIUC", "classification": "match"}],
                    "out_of_state_colleges": [{"name": "Georgia Tech", "classification": "match"}],
                    "executive_summary": "UIUC is the top recommendation.",
                }
            ),
            json.dumps(
                {
                    "cost_analysis": {"in_state": "UIUC $66K total"},
                    "h4_financial_rules": "Not eligible for FAFSA",
                    "merit_aid_strategy": "Target institutional merit",
                }
            ),
            json.dumps(
                {
                    "career_safety_analysis": {"cs_sponsorship": "90%+"},
                    "immigration_pathway": "F-1 -> OPT -> STEM OPT -> H-1B",
                    "masters_recommendation": "BS/MS at UIUC recommended",
                }
            ),
            "# Divija Mondal: Complete College Guide\n\n## Executive Summary\nStrong candidate...",
            json.dumps(
                {
                    "status": "approved",
                    "comments": "Comprehensive and accurate report.",
                    "sections_needing_revision": [],
                }
            ),
        ]
        llm = MockLLMProvider(responses=responses)
        orchestrator = OrchestratorAgent(llm=llm)
        report = orchestrator.run(sample_student_profile)

        assert report is not None
        assert report.student_name == "Divija Mondal"
        assert report.review_status == ReviewStatus.APPROVED
        assert report.is_finalized is True
        assert len(report.markdown_content) > 0
        assert report.review_iterations >= 1

    def test_run_with_revision_cycle(self, sample_student_profile):
        # Responses for agents + reviewer rejects first, then approves on recompile
        responses = [
            # 1. ProfileAnalyzer
            json.dumps({"profile_assessment": "Strong STEM candidate"}),
            # 2. CollegeResearcher
            json.dumps(
                {
                    "in_state_colleges": [{"name": "UIUC"}],
                    "out_of_state_colleges": [],
                }
            ),
            # 3. FinancialAnalyst
            json.dumps({"cost_analysis": {"in_state": "UIUC $66K"}}),
            # 4. CareerPathway
            json.dumps({"career_safety_analysis": {"cs": "90%+"}}),
            # 5. ReportCompiler (first attempt)
            "# Report v1\nIncomplete draft...",
            # 6. ReportReviewer (rejects)
            json.dumps(
                {
                    "status": "needs_revision",
                    "comments": "Missing financial detail for H-4.",
                    "sections_needing_revision": ["financial_analysis"],
                }
            ),
            # 7. ReportCompiler (revision attempt)
            "# Report v2\nComplete report with H-4 financial details...",
            # 8. ReportReviewer (approves)
            json.dumps(
                {
                    "status": "approved",
                    "comments": "Now comprehensive.",
                    "sections_needing_revision": [],
                }
            ),
        ]
        llm = MockLLMProvider(responses=responses)
        orchestrator = OrchestratorAgent(llm=llm)
        report = orchestrator.run(sample_student_profile)

        assert report.review_status == ReviewStatus.APPROVED
        assert report.review_iterations == 2
        assert report.is_finalized is True

    def test_run_max_iterations_forces_approval(self, sample_student_profile):
        # Reviewer always rejects - should stop after max_review_iterations
        responses = [
            json.dumps({"profile_assessment": "Strong candidate"}),
            json.dumps({"in_state_colleges": [], "out_of_state_colleges": []}),
            json.dumps({"cost_analysis": {}}),
            json.dumps({"career_safety_analysis": {}}),
        ]
        # Add compile + reject cycles for max_review_iterations
        for i in range(3):
            responses.append(f"# Report v{i + 1}\nDraft {i + 1}")
            responses.append(
                json.dumps(
                    {
                        "status": "needs_revision",
                        "comments": f"Still needs work (iteration {i + 1}).",
                        "sections_needing_revision": ["all"],
                    }
                )
            )

        llm = MockLLMProvider(responses=responses)
        orchestrator = OrchestratorAgent(llm=llm, max_review_iterations=3)
        report = orchestrator.run(sample_student_profile)

        # Should finalize after max iterations even if not approved
        assert report is not None
        assert report.review_iterations == 3
        assert len(report.markdown_content) > 0

    def test_run_calls_agents_in_correct_order(self, sample_student_profile):
        responses = [
            json.dumps({"profile_assessment": "Strong"}),
            json.dumps({"in_state_colleges": [], "out_of_state_colleges": []}),
            json.dumps({"cost_analysis": {}}),
            json.dumps({"career_safety_analysis": {}}),
            "# Report\nFinal",
            json.dumps(
                {"status": "approved", "comments": "Good", "sections_needing_revision": []}
            ),
        ]
        llm = MockLLMProvider(responses=responses)
        orchestrator = OrchestratorAgent(llm=llm)
        orchestrator.run(sample_student_profile)

        # 6 LLM calls: profile, college, financial, career, compiler, reviewer
        assert llm.call_count == 6

    def test_on_step_callback(self, sample_student_profile):
        responses = [
            json.dumps({"profile_assessment": "Strong"}),
            json.dumps({"in_state_colleges": [], "out_of_state_colleges": []}),
            json.dumps({"cost_analysis": {}}),
            json.dumps({"career_safety_analysis": {}}),
            "# Report\nFinal",
            json.dumps(
                {"status": "approved", "comments": "Good", "sections_needing_revision": []}
            ),
        ]
        llm = MockLLMProvider(responses=responses)
        steps: list[dict] = []
        orchestrator = OrchestratorAgent(llm=llm, on_step=lambda step: steps.append(step))
        orchestrator.run(sample_student_profile)

        # Should have step notifications for each agent
        assert len(steps) >= 6
        step_names = [s["agent"] for s in steps]
        assert "profile_analyzer" in step_names
        assert "college_researcher" in step_names
        assert "financial_analyst" in step_names
        assert "career_pathway" in step_names
        assert "report_compiler" in step_names
        assert "report_reviewer" in step_names
