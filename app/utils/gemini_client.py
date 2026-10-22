import os

from google import genai


class _LazyGeminiClient:
    """Creates the real Gemini client on first use, so the app can start without
    GEMINI_API_KEY; only the AI features fail (with a clear message) until it is set."""

    def __init__(self):
        self._client = None

    def __getattr__(self, name):
        if self._client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file to enable AI features.")
            self._client = genai.Client(api_key=api_key)
        return getattr(self._client, name)


def get_gemini_client():
    return _LazyGeminiClient()
