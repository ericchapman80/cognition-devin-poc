"""Report Reviewer agent - reviews compiled report for quality and completeness."""

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput, ReviewFeedback, ReviewStatus
from college_guide.prompts import report_reviewer as prompts


class ReportReviewerAgent(BaseCollegeAgent):
    """Reviews the compiled report and provides approval or revision feedback."""

    role = AgentRole.REPORT_REVIEWER
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        report_content = context.get("report_content", "")
        student_profile = context.get("student_profile", {})
        feedback = self.review(report_content, student_profile)
        return AgentOutput(
            agent_name=self.role.value,
            content=feedback.comments,
            structured_data=feedback.model_dump(),
        )

    def review(self, report_content: str, student_profile: dict) -> ReviewFeedback:
        """Review a report and return structured feedback."""
        prompt = prompts.build_review_prompt(report_content, student_profile)
        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        raw = parsed.get("raw_response")
        if raw is not None:
            # Could not parse JSON - try to infer from text
            lower = response.lower()
            if "approved" in lower or "looks good" in lower or "comprehensive" in lower:
                return ReviewFeedback(
                    status=ReviewStatus.APPROVED,
                    comments=response,
                    sections_needing_revision=[],
                )
            return ReviewFeedback(
                status=ReviewStatus.NEEDS_REVISION,
                comments=response,
                sections_needing_revision=["general"],
            )

        status_str = str(parsed.get("status", "needs_revision")).lower()
        if status_str == "approved":
            status = ReviewStatus.APPROVED
        else:
            status = ReviewStatus.NEEDS_REVISION

        return ReviewFeedback(
            status=status,
            comments=str(parsed.get("comments", "")),
            sections_needing_revision=parsed.get("sections_needing_revision", []),
        )
