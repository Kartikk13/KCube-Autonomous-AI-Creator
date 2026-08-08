import os

from dotenv import load_dotenv

load_dotenv()

PERSONA = {
    "name": os.getenv("PERSONA_NAME", "Ada"),
    "domain": os.getenv("PERSONA_DOMAIN", "AI Security"),
    "voice": os.getenv("PERSONA_VOICE", "professional and concise"),
}
