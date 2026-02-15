from dataclasses import dataclass, field
from enum import Enum

from trading_agents.llm.provider import LLMProvider


class AgentRole(Enum):
    FUNDAMENTAL_ANALYST = "fundamental_analyst"
    SENTIMENT_ANALYST = "sentiment_analyst"
    NEWS_ANALYST = "news_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"


@dataclass
class AnalysisResult:
    agent_role: AgentRole
    ticker: str
    summary: str
    signal: str = "neutral"
    confidence: float = 0.0
    details: dict = field(default_factory=dict)


class BaseAgent:
    role: AgentRole
    system_prompt: str = ""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def analyze(self, ticker: str, context: dict) -> AnalysisResult:
        raise NotImplementedError

    def _build_prompt(self, ticker: str, context: dict) -> str:
        raise NotImplementedError

    def _parse_response(self, ticker: str, response: str) -> AnalysisResult:
        signal = "neutral"
        confidence = 50.0
        lower = response.lower()

        if "strong buy" in lower or "strongly bullish" in lower:
            signal = "strong_buy"
            confidence = 85.0
        elif "buy" in lower or "bullish" in lower:
            signal = "buy"
            confidence = 70.0
        elif "strong sell" in lower or "strongly bearish" in lower:
            signal = "strong_sell"
            confidence = 85.0
        elif "sell" in lower or "bearish" in lower:
            signal = "sell"
            confidence = 70.0
        elif "hold" in lower:
            signal = "hold"
            confidence = 60.0

        return AnalysisResult(
            agent_role=self.role,
            ticker=ticker,
            summary=response,
            signal=signal,
            confidence=confidence,
        )
