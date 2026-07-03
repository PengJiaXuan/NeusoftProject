"""
=============================================================
STEP 2 — setup_sessions.py  (v2 — stealth/Chrome edition)
Hidden Fork Experiment · App Session Setup
=============================================================
"""

from pathlib import Path
from playwright.sync_api import sync_playwright
import os

STATE_DIR = Path("playwright_state")
STATE_DIR.mkdir(exist_ok=True)

SESSIONS = [
    {
        "model":       "GPT-5.4 (ChatGPT Plus)",
        "state_file":  str(STATE_DIR / "openai.json"),
        "url":         "https://chat.openai.com",
        "hint": (
            "1. Log in with your ChatGPT Plus account.\n"
            "2. If prompted, select 'GPT-5.4 Thinking'.\n"
            "3. Wait until the chat interface fully loads.\n"
            "4. Then press Enter here."
        ),
    },
    {
        "model":       "Claude Sonnet 4.6 (Claude Pro)",
        "state_file":  str(STATE_DIR / "anthropic.json"),
        "url":         "https://claude.ai",
        "hint": (
            "1. Log in with your Claude Pro account.\n"
            "2. Claude Sonnet 4.6 is the default — no selection needed.\n"
            "3. Wait until the chat interface fully loads.\n"
            "4. Then press Enter here."
        ),
    },
    {
        "model":       "Gemini 3 Flash Thinking (Google AI Pro)",
        "state_file":  str(STATE_DIR / "google.json"),
        "url":         "https://gemini.google.com/app",
        "hint": (
            "1. Log in with your Google AI Pro account.\n"
            "2. Select 'Gemini 3 Flash Thinking' from the model picker.\n"
            "3. Wait until the chat interface fully loads.\n"
            "4. Then press Enter here."
        ),
    },
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]

STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-infobars",
    "--disable-dev-shm-usage",
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


def setup_one(pw, session):
    print(f"\n{'='*60}")
    print(f"Setting up: {session['model']}")
    print('='*60)
    state_path = Path(session["state_file"])

    if state_path.exists():
        choice = input("\nSession already exists. Redo? [y/N]: ").strip().lower()
        if choice != "y":
            print("  Skipping.")
            return

    chrome = find_chrome()
    launch_kwargs = dict(headless=False, args=STEALTH_ARGS, slow_mo=50)
    if chrome:
        launch_kwargs["executable_path"] = chrome
        print(f"  Using Chrome: {chrome}")
    else:
        print("  Chrome not found — using Playwright Chromium (stealth mode)")

    browser = pw.chromium.launch(**launch_kwargs)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent=UA,
        locale="en-US",
    )
    ctx.add_init_script(
        "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
        "window.chrome={runtime:{}};"
    )

    page = ctx.new_page()
    page.goto(session["url"], wait_until="domcontentloaded", timeout=30000)

    print("\nBrowser opened. Instructions:")
    for line in session["hint"].splitlines():
        print(f"  {line}")

    input("\n>>> Press Enter when ready to save session: ")

    ctx.storage_state(path=session["state_file"])
    print(f"  ✓ Session saved → {session['state_file']}")
    browser.close()


def main():
    chrome = find_chrome()
    print("Hidden Fork — App Session Setup (v2)")
    print(f"Chrome: {chrome if chrome else 'NOT FOUND (stealth fallback)'}\n")

    with sync_playwright() as pw:
        for session in SESSIONS:
            setup_one(pw, session)

    print("\n" + "="*60)
    print("All sessions saved. Next: py run_experiment.py")
    print("="*60)


if __name__ == "__main__":
    main()
