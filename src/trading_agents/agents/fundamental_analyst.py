from trading_agents.agents.base import AgentRole, AnalysisResult, BaseAgent
from trading_agents.llm.provider import LLMProvider


class FundamentalAnalyst(BaseAgent):
    role = AgentRole.FUNDAMENTAL_ANALYST
    system_prompt = (
        "You are an expert fundamental analyst at a top trading firm. "
        "Evaluate company financials, valuation metrics, growth prospects, "
        "and competitive position. "
        "You MUST respond with a JSON object in this exact format:\n"
        '{"signal": "BUY|SELL|HOLD|STRONG BUY|STRONG SELL", '
        '"confidence": 75, '
        '"summary": "Your concise analysis with key drivers."}\n'
        "Be concise but thorough. Focus on key financial metrics."
    )

    def __init__(self, llm: LLMProvider):
        super().__init__(llm)

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        prompt = self._build_prompt(ticker, context)
        response = self.llm.generate(prompt, self.system_prompt)
        result = self._parse_response(ticker, response)
        result.details = {
            "stock_info": context.get("stock_info", {}),
            "financials_available": "financials" in context,
        }
        return result

    def _build_prompt(self, ticker: str, context: dict) -> str:
        info = context.get("stock_info", {})
        parts = [f"Analyze the fundamentals of {ticker} ({info.get('name', ticker)})."]
        parts.append(f"Sector: {info.get('sector', 'N/A')}")
        parts.append(f"Industry: {info.get('industry', 'N/A')}")

        if info.get("market_cap"):
            parts.append(f"Market Cap: ${info['market_cap']:,.0f}")
        if info.get("pe_ratio"):
            parts.append(f"P/E Ratio: {info['pe_ratio']:.2f}")
        if info.get("forward_pe"):
            parts.append(f"Forward P/E: {info['forward_pe']:.2f}")
        if info.get("revenue_growth"):
            parts.append(f"Revenue Growth: {info['revenue_growth']:.2%}")
        if info.get("profit_margins"):
            parts.append(f"Profit Margins: {info['profit_margins']:.2%}")
        if info.get("debt_to_equity"):
            parts.append(f"Debt/Equity: {info['debt_to_equity']:.2f}")
        if info.get("return_on_equity"):
            parts.append(f"ROE: {info['return_on_equity']:.2%}")
        if info.get("free_cash_flow"):
            parts.append(f"Free Cash Flow: ${info['free_cash_flow']:,.0f}")
        if info.get("dividend_yield"):
            parts.append(f"Dividend Yield: {info['dividend_yield']:.2%}")

        parts.append(
            "\nBased on these fundamentals, respond with JSON: "
            '{"signal": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL", '
            '"confidence": <0-100>, "summary": "<your analysis>"}'
        )
        return "\n".join(parts)
