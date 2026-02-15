from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class NewsAnalyst(BaseAgent):
    role = AgentRole.NEWS_ANALYST
    system_prompt = (
        "You are an expert news analyst at a top trading firm. "
        "Evaluate the impact of recent news, macroeconomic events, and industry developments "
        "on the stock. Assess whether news is material and how it affects short-term and "
        "long-term outlook. "
        "You MUST respond with a JSON object in this exact format:\n"
        '{"signal": "BUY|SELL|HOLD|STRONG BUY|STRONG SELL", '
        '"confidence": 75, '
        '"summary": "Your concise news impact analysis."}'
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_response(ticker, response)
        result.details = {"news_analyzed": len(context.get("news", []))}
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        info = context.get("stock_info", {})
        news = context.get("news", [])

        parts = [
            f"Analyze the news impact for {ticker} ({info.get('name', ticker)}).",
            f"Sector: {info.get('sector', 'N/A')}",
            f"Industry: {info.get('industry', 'N/A')}",
            "\nRecent News:",
        ]

        if news:
            for item in news[:8]:
                title = item.get("title", "No title")
                publisher = item.get("publisher", "Unknown")
                summary = item.get("summary", "")
                parts.append(f"- [{publisher}] {title}")
                if summary:
                    parts.append(f"  Summary: {summary[:200]}")
        else:
            parts.append("- No recent news available")

        parts.append(
            "\nAssess the news impact on the stock. Identify any catalysts, risks, or "
            "material events. Respond with JSON: "
            '{"signal": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL", '
            '"confidence": <0-100>, "summary": "<your analysis>"}'
        )
        return "\n".join(parts)
