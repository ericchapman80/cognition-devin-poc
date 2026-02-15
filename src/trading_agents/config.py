import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    provider: str = "ollama"
    model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    temperature: float = 0.3

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        )


@dataclass
class TradingConfig:
    max_debate_rounds: int = 2
    risk_tolerance: str = "moderate"
    analysis_period_days: int = 90
    data_cache_dir: str = str(Path.home() / ".ai_trading_agents" / "cache")
    tickers: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"])

    def validate(self) -> list[str]:
        errors = []
        if self.max_debate_rounds < 1:
            errors.append("max_debate_rounds must be >= 1")
        if self.risk_tolerance not in ("conservative", "moderate", "aggressive"):
            errors.append("risk_tolerance must be conservative, moderate, or aggressive")
        if self.analysis_period_days < 7:
            errors.append("analysis_period_days must be >= 7")
        if not self.tickers:
            errors.append("tickers list cannot be empty")
        return errors


@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(llm=LLMConfig.from_env(), trading=TradingConfig())

    def validate(self) -> list[str]:
        return self.trading.validate()
