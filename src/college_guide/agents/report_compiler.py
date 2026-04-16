"""Report Compiler agent - compiles all sub-agent outputs into a unified report."""

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput
from college_guide.prompts import report_compiler as prompts


class ReportCompilerAgent(BaseCollegeAgent):
    """Compiles all analysis outputs into a comprehensive markdown report."""

    role = AgentRole.REPORT_COMPILER
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        student_profile = context.get("student_profile", {})
        profile_analysis = context.get("profile_analysis", "")
        college_recommendations = context.get("college_recommendations", "")
        financial_analysis = context.get("financial_analysis", "")
        career_pathway = context.get("career_pathway", "")
        revision_feedback = context.get("revision_feedback")

        prompt = prompts.build_prompt(
            student_profile=student_profile,
            profile_analysis=profile_analysis,
            college_recommendations=college_recommendations,
            financial_analysis=financial_analysis,
            career_pathway=career_pathway,
            revision_feedback=revision_feedback,
        )
        response = self._call_llm(prompt)

        return AgentOutput(
            agent_name=self.role.value,
            content=response.strip(),
        )
