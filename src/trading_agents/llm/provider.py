import json

import requests

from trading_agents.config import LLMConfig


class LLMProvider:
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self.config.provider == "ollama":
            return self._call_ollama(prompt, system_prompt)
        elif self.config.provider == "openai":
            return self._call_openai(prompt, system_prompt)
        raise ValueError(f"Unsupported LLM provider: {self.config.provider}")

    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        url = f"{self.config.ollama_base_url}/api/generate"
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": self.config.temperature},
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.config.ollama_base_url}. "
                "Make sure Ollama is running: https://ollama.com"
            )
        except requests.Timeout:
            raise TimeoutError("Ollama request timed out after 120 seconds")

    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
        }
        resp = requests.post(url, headers=headers, json=json.dumps(payload), timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def is_available(self) -> bool:
        if self.config.provider == "ollama":
            try:
                resp = requests.get(f"{self.config.ollama_base_url}/api/tags", timeout=5)
                return resp.status_code == 200
            except (requests.ConnectionError, requests.Timeout):
                return False
        elif self.config.provider == "openai":
            return bool(self.config.openai_api_key)
        return False
