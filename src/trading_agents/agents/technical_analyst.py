from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class TechnicalAnalyst(BaseAgent):
    role = AgentRole.TECHNICAL_ANALYST
    system_prompt = (
        "You are an expert technical analyst at a top trading firm. "
        "Analyze price charts, technical indicators (RSI, MACD, Bollinger Bands, Moving Averages), "
        "and trading patterns. Identify support/resistance levels, trend direction, and momentum. "
        "You MUST respond with a JSON object in this exact format:\n"
        '{"signal": "BUY|SELL|HOLD|STRONG BUY|STRONG SELL", '
        '"confidence": 75, '
        '"summary": "Your concise technical analysis."}'
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_response(ticker, response)
        result.details = {
            "indicators": context.get("indicators", {}),
            "signals": context.get("signals", {}),
        }
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        indicators = context.get("indicators", {})
        signals = context.get("signals", {})

        parts = [f"Analyze the technical indicators for {ticker}.", "\nKey Indicators:"]

        if indicators.get("current_price"):
            parts.append(f"Current Price: ${indicators['current_price']:.2f}")
        if indicators.get("price_change_pct") is not None:
            parts.append(f"Period Change: {indicators['price_change_pct']:.2f}%")
        if indicators.get("rsi") is not None:
            parts.append(f"RSI (14): {indicators['rsi']:.2f}")
        if indicators.get("macd") is not None:
            parts.append(f"MACD: {indicators['macd']:.4f}")
        if indicators.get("macd_signal") is not None:
            parts.append(f"MACD Signal: {indicators['macd_signal']:.4f}")
        if indicators.get("sma_20") is not None:
            parts.append(f"SMA 20: ${indicators['sma_20']:.2f}")
        if indicators.get("sma_50") is not None:
            parts.append(f"SMA 50: ${indicators['sma_50']:.2f}")
        if indicators.get("bb_upper") is not None:
            parts.append(
                f"Bollinger Bands: ${indicators['bb_lower']:.2f} - ${indicators['bb_upper']:.2f}"
            )
        if indicators.get("atr") is not None:
            parts.append(f"ATR (14): {indicators['atr']:.4f}")
        if indicators.get("volume_trend") is not None:
            parts.append(f"Volume Trend: {indicators['volume_trend']:.2f}x average")

        if signals:
            parts.append("\nSignal Summary:")
            for key, value in signals.items():
                if key not in ("overall", "confidence"):
                    parts.append(f"- {key}: {value}")

        parts.append(
            "\nBased on these technical indicators, respond with JSON: "
            '{"signal": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL", '
            '"confidence": <0-100>, "summary": "<your analysis>"}'
        )
        return "\n".join(parts)
