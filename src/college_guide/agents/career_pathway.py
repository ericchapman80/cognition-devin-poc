"""Career Pathway agent - analyzes career and immigration pathways."""

import json

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput
from college_guide.prompts import career_pathway as prompts


class CareerPathwayAgent(BaseCollegeAgent):
    """Analyzes career safety, immigration pathways, and MS degree strategy."""

    role = AgentRole.CAREER_PATHWAY
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        student_profile = context.get("student_profile", {})
        college_recommendations = context.get("college_recommendations", "")
        financial_analysis = context.get("financial_analysis", "")
        prompt = prompts.build_prompt(student_profile, college_recommendations, financial_analysis)
        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        content = parsed.get("immigration_pathway", response)
        if isinstance(content, dict):
            content = json.dumps(content, indent=2)

        return AgentOutput(
            agent_name=self.role.value,
            content=content,
            structured_data=parsed if parsed != {"raw_response": response} else None,
        )
