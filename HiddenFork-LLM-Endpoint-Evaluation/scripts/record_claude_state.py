"""
Record Claude login state to the unified Playwright state path.
Close all Chrome windows before running.
"""

from playwright.sync_api import sync_playwright

from experiment_state import APP_START_URL, CHROME_EXE, STATE_ANTHROPIC, ensure_state_dir


def main():
    ensure_state_dir()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,
            executable_path=CHROME_EXE,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(APP_START_URL["claude-sonnet-4-6"], wait_until="domcontentloaded", timeout=60000)
        print("Log in to Claude in the opened browser, then return here and press Enter.")
        input()
        ctx.storage_state(path=STATE_ANTHROPIC)
        print(f"Saved login state to: {STATE_ANTHROPIC}")
        browser.close()


if __name__ == "__main__":
    main()
