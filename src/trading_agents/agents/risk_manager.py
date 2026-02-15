from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class RiskManager(BaseAgent):
    role = AgentRole.RISK_MANAGER
    system_prompt = (
        "You are the head of risk management at a top trading firm. "
        "Review the trader's proposed decision and assess portfolio risk. "
        "Evaluate: market volatility, position concentration, liquidity risk, "
        "correlation risk, and downside scenarios. "
        "You can APPROVE, MODIFY, or REJECT the trade proposal. "
        "If modifying, suggest adjusted position size or conditions."
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_risk_response(ticker, response)
        trader_dec = context.get("trader_decision")
        trader_signal = trader_dec.signal if trader_dec else ""
        result.details = {"trader_signal": trader_signal}
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        trader_decision = context.get("trader_decision")
        indicators = context.get("indicators", {})

        parts = [f"Review the trading proposal for {ticker}.", "\n--- TRADER PROPOSAL ---"]

        if trader_decision:
            parts.append(f"Signal: {trader_decision.signal}")
            parts.append(f"Confidence: {trader_decision.confidence}%")
            parts.append(f"Summary: {trader_decision.summary[:500]}")

        parts.append("\n--- RISK METRICS ---")
        if indicators.get("atr") is not None:
            parts.append(f"ATR (Volatility): {indicators['atr']:.4f}")
        if indicators.get("rsi") is not None:
            parts.append(f"RSI: {indicators['rsi']:.2f}")
        if indicators.get("volume_trend") is not None:
            parts.append(f"Volume Trend: {indicators['volume_trend']:.2f}x")

        stock_info = context.get("stock_info", {})
        if stock_info.get("beta"):
            parts.append(f"Beta: {stock_info['beta']:.2f}")
        if stock_info.get("debt_to_equity"):
            parts.append(f"Debt/Equity: {stock_info['debt_to_equity']:.2f}")

        risk_tolerance = context.get("risk_tolerance", "moderate")
        parts.append(f"\nPortfolio Risk Tolerance: {risk_tolerance}")
        parts.append(
            "\nProvide your risk assessment:\n"
            "1. Decision: APPROVE / MODIFY / REJECT\n"
            "2. Risk level: LOW / MEDIUM / HIGH\n"
            "3. If MODIFY: suggested adjustments\n"
            "4. Key risk factors\n"
            "5. Recommended stop-loss level if applicable"
        )
        return "\n".join(parts)

    def _parse_risk_response(self, ticker: str, response: str) -> AnalysisResult:
        lower = response.lower()
        if "reject" in lower:
            signal = "reject"
            confidence = 80.0
        elif "modify" in lower:
            signal = "modify"
            confidence = 65.0
        elif "approve" in lower:
            signal = "approve"
            confidence = 75.0
        else:
            signal = "review"
            confidence = 50.0

        return AnalysisResult(
            agent_role=self.role,
            ticker=ticker,
            summary=response,
            signal=signal,
            confidence=confidence,
        )
