from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, StateGraph

from trading_agents.agents.base import AnalysisResult
from trading_agents.agents.bear_researcher import BearResearcher
from trading_agents.agents.bull_researcher import BullResearcher
from trading_agents.agents.fundamental_analyst import FundamentalAnalyst
from trading_agents.agents.news_analyst import NewsAnalyst
from trading_agents.agents.risk_manager import RiskManager
from trading_agents.agents.sentiment_analyst import SentimentAnalyst
from trading_agents.agents.technical_analyst import TechnicalAnalyst
from trading_agents.agents.trader import TraderAgent
from trading_agents.agents.verifier import VerifierAgent
from trading_agents.analysis.technical_indicators import TechnicalAnalyzer
from trading_agents.config import AppConfig
from trading_agents.data.market_data import MarketDataProvider
from trading_agents.llm.provider import LLMProvider


def _merge_lists(left: list, right: list) -> list:
    return left + right


class TradingState(TypedDict, total=False):
    ticker: str
    date: str | None
    stock_info: dict
    news: list
    price_data: Any
    indicators: dict
    signals: dict
    analyst_reports: Annotated[list, _merge_lists]
    debate_history: Annotated[list, _merge_lists]
    trader_summary: str
    trader_signal: str
    trader_confidence: float
    risk_assessment: str
    final_signal: str
    final_confidence: float
    verification_summary: str
    verification_issues: list
    risk_tolerance: str
    max_debate_rounds: int
    analysis_period_days: int
    steps: Annotated[list, _merge_lists]
    error: str


@dataclass
class StepResult:
    step_name: str
    status: str = "pending"
    data: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class TradingDecision:
    ticker: str
    final_signal: str = "hold"
    confidence: float = 0.0
    trader_summary: str = ""
    risk_assessment: str = ""
    analyst_reports: list = field(default_factory=list)
    debate_history: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    stock_info: dict = field(default_factory=dict)
    indicators: dict = field(default_factory=dict)
    signals: dict = field(default_factory=dict)
    price_data: Any = None
    verification_summary: str = ""
    verification_issues: list = field(default_factory=list)


class TradingAgentsGraph:
    def __init__(self, config: AppConfig, on_step: callable = None):
        self.config = config
        self.on_step = on_step or (lambda s: None)
        self.llm = LLMProvider(config.llm)
        self.data_provider = MarketDataProvider()
        self.tech_analyzer = TechnicalAnalyzer()

        self.fundamental_analyst = FundamentalAnalyst(self.llm)
        self.sentiment_analyst = SentimentAnalyst(self.llm)
        self.news_analyst = NewsAnalyst(self.llm)
        self.technical_analyst = TechnicalAnalyst(self.llm)
        self.bull_researcher = BullResearcher(self.llm)
        self.bear_researcher = BearResearcher(self.llm)
        self.trader = TraderAgent(self.llm)
        self.risk_manager = RiskManager(self.llm)
        self.verifier = VerifierAgent(self.llm)

        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(TradingState)

        builder.add_node("fetch_data", self._node_fetch_data)
        builder.add_node("fundamental_analysis", self._node_fundamental)
        builder.add_node("sentiment_analysis", self._node_sentiment)
        builder.add_node("news_analysis", self._node_news)
        builder.add_node("technical_analysis", self._node_technical)
        builder.add_node("research_debate", self._node_research_debate)
        builder.add_node("trader_decision", self._node_trader_decision)
        builder.add_node("risk_review", self._node_risk_review)
        builder.add_node("verification", self._node_verification)

        builder.set_entry_point("fetch_data")

        builder.add_edge("fetch_data", "fundamental_analysis")
        builder.add_edge("fetch_data", "sentiment_analysis")
        builder.add_edge("fetch_data", "news_analysis")
        builder.add_edge("fetch_data", "technical_analysis")

        builder.add_edge("fundamental_analysis", "research_debate")
        builder.add_edge("sentiment_analysis", "research_debate")
        builder.add_edge("news_analysis", "research_debate")
        builder.add_edge("technical_analysis", "research_debate")

        builder.add_edge("research_debate", "trader_decision")
        builder.add_edge("trader_decision", "risk_review")
        builder.add_edge("risk_review", "verification")
        builder.add_edge("verification", END)

        return builder.compile()

    def _emit_step(self, name: str, status: str, data: dict | None = None, error: str = ""):
        step = StepResult(step_name=name, status=status, data=data or {}, error=error)
        try:
            self.on_step(step)
        except Exception:
            pass
        return step

    def _node_fetch_data(self, state: TradingState) -> dict:
        self._emit_step("Fetching Market Data", "pending")
        ticker = state["ticker"]
        date = state.get("date")
        period = state.get("analysis_period_days", 90)

        try:
            price_data = self.data_provider.get_historical_data(ticker, period, date)
            stock_info = self.data_provider.get_stock_info(ticker)
            news = self.data_provider.get_recent_news(ticker)
            indicators = self.tech_analyzer.compute_indicators(price_data)
            signals = self.tech_analyzer.get_signal_summary(indicators)

            step_data = {
                "stock_info": stock_info,
                "news": news,
                "indicators": indicators,
                "signals": signals,
                "rows": len(price_data),
            }
            self._emit_step("Fetching Market Data", "completed", step_data)

            return {
                "stock_info": stock_info,
                "news": news,
                "price_data": price_data,
                "indicators": indicators,
                "signals": signals,
                "steps": [
                    {"name": "Fetching Market Data", "status": "completed"}
                ],
            }
        except Exception as e:
            self._emit_step("Fetching Market Data", "error", error=str(e))
            raise

    def _node_fundamental(self, state: TradingState) -> dict:
        self._emit_step("Fundamental Analysis", "pending")
        ticker = state["ticker"]
        context = {
            "stock_info": state.get("stock_info", {}),
            "indicators": state.get("indicators", {}),
            "signals": state.get("signals", {}),
        }
        try:
            result = self.fundamental_analyst.analyze(ticker, context)
            self._emit_step(
                "Fundamental Analysis",
                "completed",
                {"signal": result.signal, "confidence": result.confidence},
            )
            return {
                "analyst_reports": [result],
                "steps": [{"name": "Fundamental Analysis", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Fundamental Analysis", "error", error=str(e))
            fallback = AnalysisResult(
                agent_role=self.fundamental_analyst.role,
                ticker=ticker,
                summary=f"Analysis failed: {e}",
                signal="neutral",
                confidence=0.0,
            )
            return {
                "analyst_reports": [fallback],
                "steps": [
                    {"name": "Fundamental Analysis", "status": "error", "error": str(e)}
                ],
            }

    def _node_sentiment(self, state: TradingState) -> dict:
        self._emit_step("Sentiment Analysis", "pending")
        ticker = state["ticker"]
        context = {
            "stock_info": state.get("stock_info", {}),
            "news": state.get("news", []),
        }
        try:
            result = self.sentiment_analyst.analyze(ticker, context)
            self._emit_step(
                "Sentiment Analysis",
                "completed",
                {"signal": result.signal, "confidence": result.confidence},
            )
            return {
                "analyst_reports": [result],
                "steps": [{"name": "Sentiment Analysis", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Sentiment Analysis", "error", error=str(e))
            fallback = AnalysisResult(
                agent_role=self.sentiment_analyst.role,
                ticker=ticker,
                summary=f"Analysis failed: {e}",
                signal="neutral",
                confidence=0.0,
            )
            return {
                "analyst_reports": [fallback],
                "steps": [
                    {"name": "Sentiment Analysis", "status": "error", "error": str(e)}
                ],
            }

    def _node_news(self, state: TradingState) -> dict:
        self._emit_step("News Analysis", "pending")
        ticker = state["ticker"]
        context = {
            "stock_info": state.get("stock_info", {}),
            "news": state.get("news", []),
        }
        try:
            result = self.news_analyst.analyze(ticker, context)
            self._emit_step(
                "News Analysis",
                "completed",
                {"signal": result.signal, "confidence": result.confidence},
            )
            return {
                "analyst_reports": [result],
                "steps": [{"name": "News Analysis", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("News Analysis", "error", error=str(e))
            fallback = AnalysisResult(
                agent_role=self.news_analyst.role,
                ticker=ticker,
                summary=f"Analysis failed: {e}",
                signal="neutral",
                confidence=0.0,
            )
            return {
                "analyst_reports": [fallback],
                "steps": [{"name": "News Analysis", "status": "error", "error": str(e)}],
            }

    def _node_technical(self, state: TradingState) -> dict:
        self._emit_step("Technical Analysis", "pending")
        ticker = state["ticker"]
        context = {
            "indicators": state.get("indicators", {}),
            "signals": state.get("signals", {}),
        }
        try:
            result = self.technical_analyst.analyze(ticker, context)
            self._emit_step(
                "Technical Analysis",
                "completed",
                {"signal": result.signal, "confidence": result.confidence},
            )
            return {
                "analyst_reports": [result],
                "steps": [{"name": "Technical Analysis", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Technical Analysis", "error", error=str(e))
            fallback = AnalysisResult(
                agent_role=self.technical_analyst.role,
                ticker=ticker,
                summary=f"Analysis failed: {e}",
                signal="neutral",
                confidence=0.0,
            )
            return {
                "analyst_reports": [fallback],
                "steps": [
                    {"name": "Technical Analysis", "status": "error", "error": str(e)}
                ],
            }

    def _node_research_debate(self, state: TradingState) -> dict:
        self._emit_step("Research Debate", "pending")
        ticker = state["ticker"]
        max_rounds = state.get("max_debate_rounds", 2)
        context = {
            "analyst_reports": state.get("analyst_reports", []),
            "stock_info": state.get("stock_info", {}),
            "indicators": state.get("indicators", {}),
        }
        try:
            bull_result = self.bull_researcher.analyze(ticker, context)
            bear_result = self.bear_researcher.analyze(ticker, context)
            debate_history = [{"bull": bull_result.summary, "bear": bear_result.summary}]

            for _ in range(1, max_rounds):
                bull_counter = self.bull_researcher.debate(
                    ticker, context, bear_result.summary
                )
                bear_counter = self.bear_researcher.debate(
                    ticker, context, bull_result.summary
                )
                debate_history.append({"bull": bull_counter, "bear": bear_counter})
                bull_result.summary = bull_counter
                bear_result.summary = bear_counter

            self._emit_step("Research Debate", "completed", {"rounds": len(debate_history)})
            return {
                "analyst_reports": [bull_result, bear_result],
                "debate_history": debate_history,
                "steps": [{"name": "Research Debate", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Research Debate", "error", error=str(e))
            return {
                "steps": [{"name": "Research Debate", "status": "error", "error": str(e)}],
            }

    def _node_trader_decision(self, state: TradingState) -> dict:
        self._emit_step("Trader Decision", "pending")
        ticker = state["ticker"]
        context = {
            "analyst_reports": state.get("analyst_reports", []),
            "debate_history": state.get("debate_history", []),
            "risk_tolerance": state.get("risk_tolerance", "moderate"),
            "stock_info": state.get("stock_info", {}),
            "indicators": state.get("indicators", {}),
        }
        try:
            result = self.trader.analyze(ticker, context)
            self._emit_step(
                "Trader Decision",
                "completed",
                {"signal": result.signal, "confidence": result.confidence},
            )
            return {
                "trader_summary": result.summary,
                "trader_signal": result.signal,
                "trader_confidence": result.confidence,
                "final_signal": result.signal,
                "final_confidence": result.confidence,
                "steps": [{"name": "Trader Decision", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Trader Decision", "error", error=str(e))
            return {
                "steps": [{"name": "Trader Decision", "status": "error", "error": str(e)}],
            }

    def _node_risk_review(self, state: TradingState) -> dict:
        self._emit_step("Risk Review", "pending")
        ticker = state["ticker"]
        trader_decision_result = AnalysisResult(
            agent_role=self.trader.role,
            ticker=ticker,
            summary=state.get("trader_summary", ""),
            signal=state.get("trader_signal", "hold"),
            confidence=state.get("trader_confidence", 0.0),
        )
        context = {
            "trader_decision": trader_decision_result,
            "indicators": state.get("indicators", {}),
            "stock_info": state.get("stock_info", {}),
            "risk_tolerance": state.get("risk_tolerance", "moderate"),
        }
        try:
            risk_result = self.risk_manager.analyze(ticker, context)
            final_signal = state.get("final_signal", "hold")
            final_confidence = state.get("final_confidence", 50.0)

            if risk_result.signal == "reject":
                final_signal = "hold"
                final_confidence = max(final_confidence * 0.5, 20.0)
            elif risk_result.signal == "modify":
                final_confidence = max(final_confidence * 0.75, 30.0)

            self._emit_step(
                "Risk Review",
                "completed",
                {
                    "risk_signal": risk_result.signal,
                    "final_signal": final_signal,
                    "final_confidence": final_confidence,
                },
            )
            return {
                "risk_assessment": risk_result.summary,
                "final_signal": final_signal,
                "final_confidence": final_confidence,
                "steps": [{"name": "Risk Review", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Risk Review", "error", error=str(e))
            return {
                "steps": [{"name": "Risk Review", "status": "error", "error": str(e)}],
            }

    def _node_verification(self, state: TradingState) -> dict:
        self._emit_step("Verification", "pending")
        ticker = state["ticker"]
        try:
            result = self.verifier.verify(
                ticker=ticker,
                analyst_reports=state.get("analyst_reports", []),
                trader_summary=state.get("trader_summary", ""),
                risk_assessment=state.get("risk_assessment", ""),
            )

            issues = result.details.get("issues", [])
            conf_adj = result.details.get("confidence_adjustment", 0)

            final_confidence = state.get("final_confidence", 50.0)
            if conf_adj:
                final_confidence = max(10.0, final_confidence + float(conf_adj))

            self._emit_step(
                "Verification",
                "completed",
                {
                    "verdict": result.signal,
                    "issues_count": len(issues),
                    "confidence_adjustment": conf_adj,
                },
            )
            return {
                "verification_summary": result.summary,
                "verification_issues": issues,
                "final_confidence": final_confidence,
                "steps": [{"name": "Verification", "status": "completed"}],
            }
        except Exception as e:
            self._emit_step("Verification", "error", error=str(e))
            return {
                "steps": [{"name": "Verification", "status": "error", "error": str(e)}],
            }

    def propagate(self, ticker: str, date: str | None = None) -> TradingDecision:
        initial_state: TradingState = {
            "ticker": ticker,
            "date": date,
            "risk_tolerance": self.config.trading.risk_tolerance,
            "max_debate_rounds": self.config.trading.max_debate_rounds,
            "analysis_period_days": self.config.trading.analysis_period_days,
            "analyst_reports": [],
            "debate_history": [],
            "steps": [],
        }

        final_state = self.graph.invoke(initial_state)

        decision = TradingDecision(
            ticker=ticker,
            final_signal=final_state.get("final_signal", "hold"),
            confidence=final_state.get("final_confidence", 0.0),
            trader_summary=final_state.get("trader_summary", ""),
            risk_assessment=final_state.get("risk_assessment", ""),
            analyst_reports=final_state.get("analyst_reports", []),
            debate_history=final_state.get("debate_history", []),
            steps=[
                StepResult(
                    step_name=s.get("name", ""),
                    status=s.get("status", ""),
                    error=s.get("error", ""),
                )
                for s in final_state.get("steps", [])
            ],
            stock_info=final_state.get("stock_info", {}),
            indicators=final_state.get("indicators", {}),
            signals=final_state.get("signals", {}),
            price_data=final_state.get("price_data"),
            verification_summary=final_state.get("verification_summary", ""),
            verification_issues=final_state.get("verification_issues", []),
        )
        return decision
