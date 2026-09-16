"""Google Gemini API client using the official google-genai SDK."""

import json
import re
import time
from typing import Any, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.config import settings
from app.logging_config import logger


class GeminiClient:
    """Wrapper around google-genai SDK with exponential backoff and JSON extraction."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        """Lazy initialization of google-genai client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set. Please set GEMINI_API_KEY in .env or environment."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        """Check if API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        retries: int = 3,
        initial_delay: float = 2.0,
    ) -> dict[str, Any]:
        """Request structured JSON from Gemini with automatic retries and exponential backoff."""
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is missing. Cannot call Gemini API.")

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        delay = initial_delay
        last_error = None

        for attempt in range(1, retries + 1):
            try:
                logger.info(
                    f"Calling Gemini API (model: {self.model}, attempt {attempt}/{retries})..."
                )
                start_time = time.time()
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                elapsed = time.time() - start_time
                logger.info(f"Gemini API returned response in {elapsed:.2f}s")

                raw_text = response.text or ""
                cleaned_text = self._clean_json_text(raw_text)
                parsed_data = json.loads(cleaned_text)
                return parsed_data

            except (APIError, Exception) as e:
                last_error = e
                logger.warning(
                    f"Gemini attempt {attempt}/{retries} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                if attempt == retries:
                    break
                time.sleep(delay)
                delay *= 2.0

        logger.error(f"All {retries} attempts to call Gemini API failed: {last_error}")
        raise RuntimeError(f"Gemini API generation failed: {last_error}")

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """Strip markdown fences and whitespace if model returns them."""
        s = text.strip()
        # Remove ```json ... ``` or ``` ... ```
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*```$", "", s)
        return s.strip()
