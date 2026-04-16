"""Profile Analyzer agent - analyzes student academic profile."""

import json

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput
from college_guide.prompts import profile_analyzer as prompts


class ProfileAnalyzerAgent(BaseCollegeAgent):
    """Analyzes the student's academic profile, GPA, courses, and test scores."""

    role = AgentRole.PROFILE_ANALYZER
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        student_profile = context.get("student_profile", {})
        prompt = prompts.build_prompt(student_profile)
        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        content = parsed.get("profile_assessment", response)
        if isinstance(content, dict):
            content = json.dumps(content, indent=2)

        return AgentOutput(
            agent_name=self.role.value,
            content=content,
            structured_data=parsed if parsed != {"raw_response": response} else None,
        )
