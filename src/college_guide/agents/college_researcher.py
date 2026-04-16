"""College Researcher agent - recommends in-state and out-of-state colleges."""

import json

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput
from college_guide.prompts import college_researcher as prompts


class CollegeResearcherAgent(BaseCollegeAgent):
    """Researches and recommends colleges based on student profile and analysis."""

    role = AgentRole.COLLEGE_RESEARCHER
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        student_profile = context.get("student_profile", {})
        profile_analysis = context.get("profile_analysis", "")
        prompt = prompts.build_prompt(student_profile, profile_analysis)
        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        content = parsed.get("executive_summary", response)
        if isinstance(content, dict):
            content = json.dumps(content, indent=2)

        return AgentOutput(
            agent_name=self.role.value,
            content=content,
            structured_data=parsed if parsed != {"raw_response": response} else None,
        )
