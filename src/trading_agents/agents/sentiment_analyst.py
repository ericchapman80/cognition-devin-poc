from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class SentimentAnalyst(BaseAgent):
    role = AgentRole.SENTIMENT_ANALYST
    system_prompt = (
        "You are an expert sentiment analyst at a top trading firm. "
        "Analyze market sentiment from news headlines, social media trends, and analyst opinions. "
        "Gauge the overall mood: bullish, bearish, or neutral. "
        "You MUST respond with a JSON object in this exact format:\n"
        '{"signal": "BUY|SELL|HOLD|STRONG BUY|STRONG SELL", '
        '"confidence": 75, '
        '"summary": "Your concise sentiment analysis."}'
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_response(ticker, response)
        result.details = {"news_count": len(context.get("news", []))}
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        info = context.get("stock_info", {})
        news = context.get("news", [])

        parts = [
            f"Analyze the market sentiment for {ticker} ({info.get('name', ticker)}).",
            f"Sector: {info.get('sector', 'N/A')}",
            "\nRecent News Headlines:",
        ]

        if news:
            for item in news[:8]:
                title = item.get("title", "No title")
                publisher = item.get("publisher", "Unknown")
                parts.append(f"- [{publisher}] {title}")
        else:
            parts.append("- No recent news available")

        parts.append(
            "\nBased on this sentiment analysis, respond with JSON: "
            '{"signal": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL", '
            '"confidence": <0-100>, "summary": "<your analysis>"}'
        )
        return "\n".join(parts)
