import pytest
from pydantic import BaseModel

# pyrefly: ignore [missing-import]
from src.llm.provider import OllamaProvider


class DummySchema(BaseModel):
    name: str
    amount: float


def test_ollama_json_cleaning():
    """Verify that _clean_json_text strips markdown fences and removes trailing commas."""
    provider = OllamaProvider()
    
    # 1. Clean markdown fences
    raw_markdown = "```json\n{\"name\": \"Revenue\", \"amount\": 500.0}\n```"
    cleaned = provider._clean_json_text(raw_markdown)
    assert cleaned == "{\"name\": \"Revenue\", \"amount\": 500.0}"
    
    # 2. Clean trailing commas in objects and arrays
    raw_trailing = "{\"name\": \"Revenue\", \"amount\": 500.0,}"
    cleaned = provider._clean_json_text(raw_trailing)
    assert cleaned == "{\"name\": \"Revenue\", \"amount\": 500.0}"
    
    raw_array = "{\"items\": [1, 2, 3,],}"
    cleaned = provider._clean_json_text(raw_array)
    assert cleaned == "{\"items\": [1, 2, 3]}"


def test_ollama_json_cleaning_with_surrounding_prose():
    """Verify extraction of outermost JSON braces when LLM emits conversational filler."""
    provider = OllamaProvider()
    raw = "Here is the extracted data you requested:\n{\"name\": \"Operating Profit\", \"amount\": 120.5}\nHope this helps!"
    cleaned = provider._clean_json_text(raw)
    assert cleaned == "{\"name\": \"Operating Profit\", \"amount\": 120.5}"
