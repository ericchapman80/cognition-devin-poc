from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class TraderAgent(BaseAgent):
    role = AgentRole.TRADER
    system_prompt = (
        "You are a senior trader at a top trading firm. You receive reports from analysts "
        "and researchers (both bull and bear cases). Your job is to synthesize all information "
        "and make a final trading decision. Consider risk/reward, timing, and position sizing. "
        "You MUST respond with a JSON object in this exact format:\n"
        '{"signal": "BUY|SELL|HOLD|STRONG BUY|STRONG SELL", '
        '"confidence": 75, '
        '"summary": "Your decision rationale with key factors."}\n'
        "Include suggested position size (% of portfolio) and time horizon in summary."
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_response(ticker, response)
        result.details = {
            "analyst_count": len(context.get("analyst_reports", [])),
            "debate_rounds": len(context.get("debate_history", [])),
        }
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        parts = [f"Make a trading decision for {ticker}.", "\n--- ANALYST REPORTS ---"]

        for report in context.get("analyst_reports", []):
            role_val = report.agent_role
            role = role_val.value if hasattr(role_val, "value") else role_val
            parts.append(f"\n[{role}] Signal: {report.signal} | Confidence: {report.confidence}%")
            parts.append(f"Summary: {report.summary[:400]}")

        debate_history = context.get("debate_history", [])
        if debate_history:
            parts.append("\n--- RESEARCH DEBATE ---")
            for i, entry in enumerate(debate_history):
                parts.append(f"\nRound {i + 1}:")
                parts.append(f"Bull: {entry.get('bull', '')[:300]}")
                parts.append(f"Bear: {entry.get('bear', '')[:300]}")

        risk_tolerance = context.get("risk_tolerance", "moderate")
        parts.append(f"\nRisk Tolerance: {risk_tolerance}")
        parts.append(
            "\nBased on all the above, respond with JSON: "
            '{"signal": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL", '
            '"confidence": <0-100>, "summary": "<decision with position size, '
            'time horizon, and top 3 factors>"}'
        )
        return "\n".join(parts)
