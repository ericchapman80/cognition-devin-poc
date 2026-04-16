"""Orchestrator agent - coordinates all sub-agents and manages the review loop."""

import json
from datetime import datetime, timezone
from typing import Callable

from college_guide.agents.career_pathway import CareerPathwayAgent
from college_guide.agents.college_researcher import CollegeResearcherAgent
from college_guide.agents.financial_analyst import FinancialAnalystAgent
from college_guide.agents.profile_analyzer import ProfileAnalyzerAgent
from college_guide.agents.report_compiler import ReportCompilerAgent
from college_guide.agents.report_reviewer import ReportReviewerAgent
from college_guide.models import FinalReport, ReviewStatus, StudentProfile


class OrchestratorAgent:
    """Parent orchestrator that coordinates sub-agents and manages the review loop.

    Workflow:
    1. Profile Analyzer -> analyzes student academic profile
    2. College Researcher -> recommends colleges based on profile
    3. Financial Analyst -> analyzes costs and aid for recommended colleges
    4. Career Pathway -> analyzes career and immigration pathways
    5. Report Compiler -> compiles all outputs into a unified report
    6. Report Reviewer -> reviews report quality; may request revisions
       (loops back to step 5 if revision needed, up to max_review_iterations)
    """

    def __init__(
        self,
        llm: object,
        max_review_iterations: int = 3,
        on_step: Callable[[dict], None] | None = None,
    ) -> None:
        self.llm = llm
        self.max_review_iterations = max_review_iterations
        self.on_step = on_step or (lambda step: None)

        self.profile_analyzer = ProfileAnalyzerAgent(llm=llm)
        self.college_researcher = CollegeResearcherAgent(llm=llm)
        self.financial_analyst = FinancialAnalystAgent(llm=llm)
        self.career_pathway = CareerPathwayAgent(llm=llm)
        self.report_compiler = ReportCompilerAgent(llm=llm)
        self.report_reviewer = ReportReviewerAgent(llm=llm)

    def run(self, student_profile: StudentProfile) -> FinalReport:
        """Execute the full multi-agent workflow and return a finalized report."""
        profile_data = student_profile.model_dump()

        # Step 1: Profile Analysis
        self._notify_step("profile_analyzer", "running")
        profile_output = self.profile_analyzer.analyze(
            {"student_profile": profile_data}
        )
        profile_analysis_text = self._format_agent_output(profile_output)
        self._notify_step("profile_analyzer", "completed")

        # Step 2: College Research
        self._notify_step("college_researcher", "running")
        college_output = self.college_researcher.analyze(
            {
                "student_profile": profile_data,
                "profile_analysis": profile_analysis_text,
            }
        )
        college_recs_text = self._format_agent_output(college_output)
        self._notify_step("college_researcher", "completed")

        # Step 3: Financial Analysis
        self._notify_step("financial_analyst", "running")
        financial_output = self.financial_analyst.analyze(
            {
                "student_profile": profile_data,
                "college_recommendations": college_recs_text,
            }
        )
        financial_text = self._format_agent_output(financial_output)
        self._notify_step("financial_analyst", "completed")

        # Step 4: Career Pathway
        self._notify_step("career_pathway", "running")
        career_output = self.career_pathway.analyze(
            {
                "student_profile": profile_data,
                "college_recommendations": college_recs_text,
                "financial_analysis": financial_text,
            }
        )
        career_text = self._format_agent_output(career_output)
        self._notify_step("career_pathway", "completed")

        # Step 5-6: Report Compilation and Review Loop
        report_markdown = ""
        review_iterations = 0
        review_status = ReviewStatus.NEEDS_REVISION
        revision_feedback = None

        for iteration in range(self.max_review_iterations):
            review_iterations = iteration + 1

            # Step 5: Compile Report
            self._notify_step("report_compiler", "running", iteration=review_iterations)
            compile_context = {
                "student_profile": profile_data,
                "profile_analysis": profile_analysis_text,
                "college_recommendations": college_recs_text,
                "financial_analysis": financial_text,
                "career_pathway": career_text,
            }
            if revision_feedback:
                compile_context["revision_feedback"] = revision_feedback

            compiler_output = self.report_compiler.analyze(compile_context)
            report_markdown = compiler_output.content
            self._notify_step("report_compiler", "completed", iteration=review_iterations)

            # Step 6: Review Report
            self._notify_step("report_reviewer", "running", iteration=review_iterations)
            feedback = self.report_reviewer.review(
                report_content=report_markdown,
                student_profile=profile_data,
            )
            self._notify_step(
                "report_reviewer",
                "completed",
                iteration=review_iterations,
                review_result=feedback.status.value,
            )

            if feedback.is_approved:
                review_status = ReviewStatus.APPROVED
                break

            # Prepare revision feedback for next iteration
            revision_feedback = (
                f"Review Iteration {review_iterations}:\n"
                f"Status: {feedback.status.value}\n"
                f"Comments: {feedback.comments}\n"
                f"Sections needing revision: {', '.join(feedback.sections_needing_revision)}"
            )

        report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        return FinalReport(
            student_name=student_profile.name,
            report_date=report_date,
            sections=self._extract_sections(report_markdown),
            review_status=review_status,
            review_iterations=review_iterations,
            markdown_content=report_markdown,
        )

    def _format_agent_output(self, output: object) -> str:
        """Format an AgentOutput into text for use by downstream agents."""
        content = output.content
        structured = output.structured_data
        if structured:
            return f"{content}\n\nDetailed Data:\n{json.dumps(structured, indent=2)}"
        return content

    def _extract_sections(self, markdown: str) -> dict[str, str]:
        """Extract named sections from the markdown report."""
        sections: dict[str, str] = {}
        current_section = "preamble"
        current_content: list[str] = []

        for line in markdown.split("\n"):
            if line.startswith("# ") or line.startswith("## "):
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                heading = line.lstrip("#").strip().lower()
                current_section = heading.replace(" ", "_").replace("&", "and")
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _notify_step(self, agent: str, status: str, **kwargs: object) -> None:
        """Send a step notification via the on_step callback."""
        step = {"agent": agent, "status": status}
        step.update(kwargs)
        self.on_step(step)
