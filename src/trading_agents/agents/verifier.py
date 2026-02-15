import json

from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class VerifierAgent(BaseAgent):
    role = AgentRole.VERIFIER
    system_prompt = (
        "You are a senior quality assurance analyst at a top trading firm. "
        "Your job is to review the entire analysis pipeline output and verify: "
        "1) Consistency: Do the analyst signals align with their stated reasoning? "
        "2) Contradictions: Are there conflicting signals that weren't addressed? "
        "3) Data support: Are key claims backed by actual data points? "
        "4) Missing risks: Are there obvious risks that no analyst mentioned? "
        "5) Bias check: Is the final decision overly influenced by one analyst? "
        "\nYou must respond with a JSON object: "
        '{"verdict": "APPROVED|FLAGGED|REJECTED", "confidence_adjustment": <int>, '
        '"issues": [<list of issues found>], "summary": "<your assessment>"}'
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        return self.verify(
            ticker=ticker,
            analyst_reports=context.get("analyst_reports", []),
            trader_summary=context.get("trader_summary", ""),
            risk_assessment=context.get("risk_assessment", ""),
        )

    def verify(
        self,
        ticker: str,
        analyst_reports: list[AnalysisResult],
        trader_summary: str,
        risk_assessment: str,
    ) -> AnalysisResult:
        prompt = self._build_verify_prompt(
            ticker, analyst_reports, trader_summary, risk_assessment
        )
        response = self.llm.generate(prompt, self.system_prompt)
        return self._parse_verify_response(ticker, response)

    def _build_verify_prompt(
        self,
        ticker: str,
        analyst_reports: list[AnalysisResult],
        trader_summary: str,
        risk_assessment: str,
    ) -> str:
        parts = [
            f"Verify the analysis pipeline output for {ticker}.",
            "\n--- ANALYST REPORTS ---",
        ]

        if analyst_reports:
            for report in analyst_reports:
                role_val = report.agent_role
                role = role_val.value if hasattr(role_val, "value") else str(role_val)
                parts.append(
                    f"\n[{role}] Signal: {report.signal} | "
                    f"Confidence: {report.confidence}%"
                )
                parts.append(f"Summary: {report.summary[:400]}")
        else:
            parts.append("No analyst reports provided.")

        parts.append("\n--- TRADER DECISION ---")
        parts.append(trader_summary[:500] if trader_summary else "No trader summary.")

        parts.append("\n--- RISK ASSESSMENT ---")
        parts.append(risk_assessment[:500] if risk_assessment else "No risk assessment.")

        parts.append(
            "\nReview for consistency, contradictions, unsupported claims, "
            "missing risks, and bias. Respond with JSON: "
            '{"verdict": "APPROVED|FLAGGED|REJECTED", '
            '"confidence_adjustment": <int -30 to 0>, '
            '"issues": [<list>], "summary": "<assessment>"}'
        )
        return "\n".join(parts)

    def _build_prompt(self, ticker: str, context: dict) -> str:
        return self._build_verify_prompt(
            ticker,
            context.get("analyst_reports", []),
            context.get("trader_summary", ""),
            context.get("risk_assessment", ""),
        )

    def _parse_verify_response(self, ticker: str, response: str) -> AnalysisResult:
        parsed = None
        text = response.strip()

        if text.startswith("{") and text.endswith("}"):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
        elif "```json" in text:
            try:
                block = text.split("```json", 1)[1].split("```", 1)[0].strip()
                parsed = json.loads(block)
            except (IndexError, json.JSONDecodeError):
                parsed = None

        if isinstance(parsed, dict):
            verdict = str(parsed.get("verdict", "")).lower().strip()
            issues = parsed.get("issues", [])
            confidence_adj = parsed.get("confidence_adjustment", 0)
            summary = str(parsed.get("summary", response))

            signal = self._verdict_to_signal(verdict)

            return AnalysisResult(
                agent_role=self.role,
                ticker=ticker,
                summary=summary,
                signal=signal,
                confidence=max(0.0, 100.0 + float(confidence_adj)),
                details={
                    "verdict": verdict,
                    "issues": issues if isinstance(issues, list) else [],
                    "confidence_adjustment": confidence_adj,
                },
            )

        signal = self._verdict_from_text(response)
        return AnalysisResult(
            agent_role=self.role,
            ticker=ticker,
            summary=response,
            signal=signal,
            confidence=70.0,
            details={"verdict": signal, "issues": [], "confidence_adjustment": 0},
        )

    def _verdict_to_signal(self, verdict: str) -> str:
        if "approved" in verdict or "approve" in verdict:
            return "approved"
        if "rejected" in verdict or "reject" in verdict:
            return "rejected"
        if "flagged" in verdict or "flag" in verdict:
            return "flagged"
        return "flagged"

    def _verdict_from_text(self, response: str) -> str:
        lower = response.lower()
        if "approved" in lower or "approve" in lower:
            return "approved"
        if "rejected" in lower or "reject" in lower:
            return "rejected"
        return "flagged"
