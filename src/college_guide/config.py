"""Configuration for the college guide multi-agent workflow."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class CollegeGuideConfig:
    """Configuration for the college guide workflow."""

    max_review_iterations: int = 3
    output_dir: str = str(Path.cwd() / "output")

    @classmethod
    def from_env(cls) -> "CollegeGuideConfig":
        return cls(
            max_review_iterations=int(os.getenv("COLLEGE_GUIDE_MAX_REVIEWS", "3")),
            output_dir=os.getenv("COLLEGE_GUIDE_OUTPUT_DIR", str(Path.cwd() / "output")),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.max_review_iterations < 1:
            errors.append("max_review_iterations must be >= 1")
        if self.max_review_iterations > 10:
            errors.append("max_review_iterations must be <= 10")
        return errors


@dataclass
class AppConfig:
    """Top-level configuration combining LLM and college guide settings."""

    llm_provider: str = "ollama"
    llm_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    temperature: float = 0.3
    college_guide: CollegeGuideConfig = field(default_factory=CollegeGuideConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
            llm_model=os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", "llama3")),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            college_guide=CollegeGuideConfig.from_env(),
        )

    def validate(self) -> list[str]:
        errors = self.college_guide.validate()
        if self.llm_provider not in ("ollama", "openai", "lmstudio"):
            errors.append("llm_provider must be ollama, openai, or lmstudio")
        return errors
