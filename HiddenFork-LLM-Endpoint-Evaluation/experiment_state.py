import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / "playwright_state"

STATE_OPENAI = str(STATE_DIR / "openai.json")
STATE_ANTHROPIC = str(STATE_DIR / "anthropic.json")
STATE_GOOGLE = str(STATE_DIR / "google.json")
OPENAI_PROFILE_DIR = str(STATE_DIR / "openai_profile")
ANTHROPIC_PROFILE_DIR = str(STATE_DIR / "anthropic_profile")
GOOGLE_PROFILE_DIR = str(STATE_DIR / "google_profile")
GOOGLE_CLONE_PROFILE_DIR = str(STATE_DIR / "google_clone_profile")

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEFAULT_CHROME_USER_DATA_DIR = str(
    Path(os.getenv("GOOGLE_CHROME_USER_DATA_DIR", Path(os.getenv("LOCALAPPDATA", "")) / "Google/Chrome/User Data"))
)


def resolve_default_chrome_profile_name() -> str:
    explicit = os.getenv("GOOGLE_CHROME_PROFILE_NAME")
    if explicit:
        return explicit
    local_state = Path(DEFAULT_CHROME_USER_DATA_DIR) / "Local State"
    try:
        if local_state.exists():
            data = json.loads(local_state.read_text(encoding="utf-8"))
            last_used = data.get("profile", {}).get("last_used")
            if last_used:
                return str(last_used)
    except Exception:
        pass
    return "Default"


DEFAULT_CHROME_PROFILE_NAME = resolve_default_chrome_profile_name()

APP_START_URL = {
    "gpt-5.4": "https://chatgpt.com/?model=gpt-5.4-thinking",
    "claude-sonnet-4-6": "https://claude.ai",
    "gemini-3-flash": "https://gemini.google.com/app",
}


def ensure_state_dir():
    STATE_DIR.mkdir(exist_ok=True)
