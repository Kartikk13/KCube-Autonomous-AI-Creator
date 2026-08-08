import asyncio
import os

# Workaround for local SSL interception (corporate proxy / MITM) on Windows:
# google-generativeai uses requests internally; verification fails even with a
# correct CA bundle path. Disable verification for local dev only — revisit
# before production deployment.
os.environ["CURL_CA_BUNDLE"] = ""

import requests

_original_session_init = requests.Session.__init__


def _session_init_verify_disabled(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False


requests.Session.__init__ = _session_init_verify_disabled

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"


async def generate(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key, transport="rest")
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=system_prompt,
    )
    response = await asyncio.to_thread(model.generate_content, user_prompt)
    return (response.text or "").strip()
