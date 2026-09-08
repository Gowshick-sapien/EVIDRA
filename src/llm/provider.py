from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any, Optional, Protocol, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ExtractionParseError(Exception):
    """Raised when the LLM output fails schema validation after maximum retries."""
    def __init__(self, message: str, raw_output: str, error_details: Any = None):
        super().__init__(message)
        self.raw_output = raw_output
        self.error_details = error_details


class ReasoningService(Protocol):
    """Abstract protocol for decoupled structured LLM generation."""

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> T:
        """Generate structured JSON conforming strictly to response_model."""
        ...


class OllamaProvider:
    """Production provider connecting directly to local Ollama daemon."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model_name: str = "qwen2.5:3b",
        timeout_seconds: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """Strip markdown wrappers and repair common local LLM JSON quirks."""
        cleaned = text.strip()
        
        # Strip markdown code blocks (```json ... ``` or ``` ...)
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        # Find first '{' and last '}'
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx : end_idx + 1]

        # Remove trailing commas before closing braces/brackets
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        return cleaned

    def _call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        format_spec: Any = "json",
    ) -> str:
        """Dispatch raw HTTP POST request to Ollama generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": format_spec,
            "options": {
                "temperature": 0.0,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Failed to connect to local Ollama at '{self.base_url}'. Ensure 'ollama serve' is active: {e}"
            ) from e

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> T:
        """Query Ollama with native schema enforcement and defensive repair fallback."""
        schema_dict = response_model.model_json_schema()
        
        default_system = (
            "You are a rigorous financial document extraction engine in EVIDRA. "
            "Extract explicit, non-extrapolated business and financial facts from the input document chunk. "
            "Return valid JSON conforming to the requested schema."
        )
        sys_prompt = system_prompt or default_system

        last_error = None
        last_raw = ""

        # First attempt: Use Ollama's native grammar-constrained schema format
        for attempt in range(1, max_retries + 1):
            format_spec = schema_dict if attempt == 1 else "json"
            active_prompt = prompt
            if attempt > 1:
                active_prompt = (
                    f"{prompt}\n\n"
                    f"PREVIOUS OUTPUT FAILED VALIDATION: {last_error}\n"
                    f"Please output strictly conforming JSON matching schema keys: "
                    f"{list(schema_dict.get('properties', {}).keys())}"
                )

            raw_text = self._call_ollama(active_prompt, sys_prompt, format_spec=format_spec)
            last_raw = raw_text
            cleaned_text = self._clean_json_text(raw_text)

            try:
                instance = response_model.model_validate_json(cleaned_text)
                return instance
            except (json.JSONDecodeError, ValidationError) as err:
                last_error = err

        raise ExtractionParseError(
            f"Ollama failed to generate valid '{response_model.__name__}' after {max_retries} attempts: {last_error}",
            raw_output=last_raw,
            error_details=str(last_error),
        )
