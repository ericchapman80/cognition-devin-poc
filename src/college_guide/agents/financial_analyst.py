"""Financial Analyst agent - analyzes costs, aid, and ROI for college options."""

import json

from college_guide.agents.base import AgentRole, BaseCollegeAgent
from college_guide.models import AgentOutput
from college_guide.prompts import financial_analyst as prompts


class FinancialAnalystAgent(BaseCollegeAgent):
    """Performs financial analysis including cost breakdowns, aid strategy, and ROI."""

    role = AgentRole.FINANCIAL_ANALYST
    system_prompt = prompts.SYSTEM_PROMPT

    def analyze(self, context: dict) -> AgentOutput:
        student_profile = context.get("student_profile", {})
        college_recommendations = context.get("college_recommendations", "")
        prompt = prompts.build_prompt(student_profile, college_recommendations)
        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        cost_analysis = parsed.get("cost_analysis", {})
        if isinstance(cost_analysis, dict):
            content = cost_analysis.get("best_value_overall", response)
            if isinstance(content, dict):
                content = json.dumps(content, indent=2)
        else:
            content = str(cost_analysis) if cost_analysis else response

        return AgentOutput(
            agent_name=self.role.value,
            content=content,
            structured_data=parsed if parsed != {"raw_response": response} else None,
        )
