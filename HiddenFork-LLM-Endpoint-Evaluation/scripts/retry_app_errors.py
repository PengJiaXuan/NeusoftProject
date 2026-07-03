"""
Retry E (score=None) questions using the App endpoint (browser).
Usage: py retry_app_errors.py results/claude-sonnet-4-6__app__legal.json
"""
import sys, json, time, re, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from experiment_state import STATE_ANTHROPIC, STATE_GOOGLE, STATE_OPENAI

# ── config ─────────────────────────────────────────────────────────────────
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

APP_CONFIG = {
    "claude-sonnet-4-6": {
        "url":       "https://claude.ai",
        "state":     STATE_ANTHROPIC,
        "input_sel": 'div[contenteditable="true"].ProseMirror',
        "send_sel":  'button[aria-label="Send message"]',
    },
    "gemini-3-flash": {
        "url":       "https://gemini.google.com/app",
        "state":     STATE_GOOGLE,
        "input_sel": 'rich-textarea .ql-editor, div[contenteditable="true"]',
        "send_sel":  'button[aria-label="Send message"], button.send-button',
    },
    "gpt-5.4": {
        "url":       "https://chatgpt.com/?model=gpt-5.4-thinking",
        "state":     STATE_OPENAI,
        "input_sel": '#prompt-textarea',
        "send_sel":  'button[data-testid="send-button"]',
    },
}

BENCH_MAP = {
    "gpqa":  "gpqa_diamond_100.json",
    "medqa": "medqa_100.json",
    "legal": "legalbench_100.json",
    "mmlu_pro": "mmlu_pro_100.json",
    "aime":  "aime_2025.json",
}

ROOT = Path(__file__).resolve().parent

AIME_TEMPLATE = """{question}\n\nProvide only the final integer answer (0 to 999) with no other text."""

def make_prompt(bench_name, item):
    if bench_name == "aime":
        return AIME_TEMPLATE.format(question=item["question"])
    labels = "ABCDEFGHIJ"[:len(item["choices"])]
    body = [item["question"], ""]
    for label, choice in zip(labels, item["choices"]):
        body.append(f"{label}. {choice}")
    body.append("")
    body.append(f'You may reason briefly, but end your response with exactly: "The answer is X" where X is one of {", ".join(labels)}.')
    return "\n".join(body)

def extract_mc(response):
    up = response.upper()
    m = re.search(r'(?:FINAL ANSWER|ANSWER|THE ANSWER IS)[:\s*]*\**\s*([A-J])\b', up)
    if m: return m.group(1)
    m = re.search(r'\b([A-J])\b', up[-400:])
    if m: return m.group(1)
    m = re.search(r'\b([A-J])\b', up[:200])
    return m.group(1) if m else None

def extract_int(response):
    text = response.strip()
    m = re.findall(r'\\boxed\{\s*(\d{1,3})\s*\}|(?:FINAL ANSWER|ANSWER)\s*(?:IS|:)\s*0*(\d{1,3})\b', text, flags=re.IGNORECASE)
    if m:
        last = m[-1][0] or m[-1][1]
        return int(last)
    for line in reversed(text.split('\n')[-5:]):
        line = line.strip()
        if re.match(r'^\d{1,3}$', line):
            return int(line)
    nums = re.findall(r'(?<![A-Za-z_])(\d{1,3})(?![A-Za-z_])', "\n".join(text.splitlines()[-8:]))
    return int(nums[-1]) if nums else None

def ask_on_page(page, cfg, prompt):
    """Send prompt via browser and return response text."""
    MAX_WAIT = 240
    IGNORE = ['Gemini 是一款 AI 工具', 'Gemini may display inaccurate', 'Gemini can make mistakes']

    new_chat_url = cfg["url"].rstrip("/") + "/new" if "claude.ai" in cfg["url"] else cfg["url"]
    try:
        page.goto(new_chat_url, wait_until="domcontentloaded", timeout=30000)
    except: pass
    time.sleep(1)

    # Count baseline p tags
    try:
        baseline_p = len([el for el in page.locator('p').all()
                         if el.inner_text(timeout=300).strip()
                         and not any(ig in el.inner_text(timeout=300) for ig in IGNORE)])
    except:
        baseline_p = 1

    # Type and send
    inp = page.locator(cfg["input_sel"]).first
    inp.wait_for(state="visible", timeout=20000)
    safe_prompt = prompt.replace('\n', ' ').replace('\r', ' ')
    inp.click(); time.sleep(0.2)
    inp.type(safe_prompt[:3], delay=30)
    time.sleep(0.1)
    inp.press("Control+a")
    inp.type(safe_prompt, delay=1)
    time.sleep(0.2)
    try:
        btn = page.locator(cfg["send_sel"]).first
        if btn.is_visible(timeout=3000): btn.click()
        else: inp.press("Enter")
    except: inp.press("Enter")

    # Poll for response
    last_text = ""; stable = 0
    for i in range(MAX_WAIT // 2):
        time.sleep(2)
        try:
            ps = page.locator('p').all()
            texts = [el.inner_text(timeout=500).strip() for el in ps]
            texts = [t for t in texts if t and not any(ig in t for ig in IGNORE)]
            if len(texts) > baseline_p:
                cur = f"{len(texts)}|{texts[-1]}"
                if cur == last_text:
                    stable += 1
                    if stable >= 5: break
                else:
                    stable = 0; last_text = cur
        except: pass

    # Grab response
    text = ""
    try:
        ps = page.locator('p').all()
        all_t = [el.inner_text(timeout=1000).strip() for el in ps]
        all_t = [t for t in all_t if t and not any(ig in t for ig in IGNORE)]
        asst = all_t[baseline_p:] if len(all_t) > baseline_p else all_t
        text = "\n".join(asst)
    except: pass
    return text if text else "[ERROR: no response captured]"

# ── main ───────────────────────────────────────────────────────────────────
result_path = Path(sys.argv[1])
fname = result_path.name  # e.g. claude-sonnet-4-6__app__legal.json

# Determine model, bench
parts = fname.replace('.json','').split('__')
model_key = parts[0]   # claude-sonnet-4-6
bench_name = parts[2]  # legal

if bench_name not in BENCH_MAP:
    sys.exit(f"Unknown benchmark: {bench_name}")
if model_key not in APP_CONFIG:
    sys.exit(f"Unknown model: {model_key}")

bench_items = json.loads((ROOT / "data" / BENCH_MAP[bench_name]).read_text(encoding="utf-8"))
results = json.loads(result_path.read_text(encoding="utf-8"))
errors = [r for r in results if r["score"] is None]
print(f"Found {len(errors)} E questions in {fname}, retrying via App...")

cfg = APP_CONFIG[model_key]
is_aime = (bench_name == "aime")

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False,
        executable_path=CHROME_EXE,
        args=["--disable-blink-features=AutomationControlled"],
    )
    ctx = browser.new_context(storage_state=cfg["state"], viewport={"width":1280,"height":900})
    page = ctx.new_page()
    try:
        page.goto(cfg["url"], wait_until="domcontentloaded", timeout=30000)
    except: pass
    time.sleep(2)

    for r in errors:
        idx = r["item_id"]
        if isinstance(idx, int):
            item = bench_items[idx]
        else:
            item = next((x for x in bench_items if str(x.get("id") or x.get("item_id")) == str(idx)), None)
            if item is None:
                item = bench_items[int(idx)]
        correct = item["answer"]
        prompt = make_prompt(bench_name, item)
        try:
            resp = ask_on_page(page, cfg, prompt)
            if is_aime:
                ans = extract_int(resp)
                try: score = 1 if ans == int(correct) else 0
                except: score = 0
            else:
                score = 1 if extract_mc(resp) == correct else 0
            tag = "✓" if score else "✗"
            r["score"] = score
            r["response_head"] = resp[:150]
        except Exception as e:
            resp = f"[ERROR: {e}]"
            score = None; tag = "E"
            r["response_head"] = resp[:150]
        print(f"  item {idx:3d} correct={correct!r} → {tag}  ({repr(resp[:60])})")
        time.sleep(1)

    browser.close()

result_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
valid = [r for r in results if r["score"] is not None]
acc = sum(r["score"] for r in valid) / len(valid) * 100 if valid else 0
remaining = sum(1 for r in results if r["score"] is None)
print(f"\nDone. Accuracy on {len(valid)} valid: {acc:.1f}%  ({remaining} still E)")
