"""Base agent class for college guide agents."""

import json
from abc import ABC, abstractmethod
from enum import Enum

from college_guide.models import AgentOutput


class AgentRole(Enum):
    """Roles for college guide sub-agents."""

    PROFILE_ANALYZER = "profile_analyzer"
    COLLEGE_RESEARCHER = "college_researcher"
    FINANCIAL_ANALYST = "financial_analyst"
    CAREER_PATHWAY = "career_pathway"
    REPORT_COMPILER = "report_compiler"
    REPORT_REVIEWER = "report_reviewer"


class BaseCollegeAgent(ABC):
    """Abstract base class for all college guide agents."""

    role: AgentRole
    system_prompt: str = ""

    def __init__(self, llm: object) -> None:
        self.llm = llm

    @abstractmethod
    def analyze(self, context: dict) -> AgentOutput:
        """Run the agent's analysis given context."""

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        sys_prompt = system_prompt or self.system_prompt
        return self.llm.generate(prompt=prompt, system_prompt=sys_prompt)

    def _parse_json_response(self, response: str) -> dict:
        """Parse a JSON response from the LLM, handling markdown code blocks."""
        text = response.strip()

        # Direct JSON object
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # JSON in markdown code block
        if "```json" in text:
            try:
                block = text.split("```json", 1)[1].split("```", 1)[0].strip()
                return json.loads(block)
            except (IndexError, json.JSONDecodeError):
                pass

        # Try to find any JSON object in the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        return {"raw_response": text}
