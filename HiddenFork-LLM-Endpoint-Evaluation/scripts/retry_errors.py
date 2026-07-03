"""
Retry only the E (score=None) questions in a results JSON file.
Usage: py retry_errors.py results/claude-sonnet-4-6__api__gpqa.json
"""
import sys, json, time, re, os
import anthropic as _ant
from pathlib import Path

# Config (must match run_experiment.py)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
MODEL_ID      = "claude-sonnet-4-6"
DELAY         = 2.0

if not ANTHROPIC_KEY:
    raise RuntimeError("Set ANTHROPIC_API_KEY or ANTHROPIC_KEY before running this retry helper.")

ant_client = _ant.Anthropic(api_key=ANTHROPIC_KEY, base_url="https://api.anthropic.com")

MC_TEMPLATE = """{question}\n\nA. {A}\nB. {B}\nC. {C}\nD. {D}\n\nYou may reason briefly, but end your response with exactly: "The answer is X" where X is A, B, C, or D."""

def make_mc_prompt(item):
    return MC_TEMPLATE.format(question=item["question"],
                               A=item["choices"][0], B=item["choices"][1],
                               C=item["choices"][2], D=item["choices"][3])

def extract_mc(response):
    up = response.upper()
    m = re.search(r'(?:ANSWER|CORRECT ANSWER|THE ANSWER IS)[:\s*]*\**\s*([A-D])\b', up)
    if m: return m.group(1)
    m = re.search(r'\b([A-D])\b', up[-400:])
    if m: return m.group(1)
    m = re.search(r'\b([A-D])\b', up[:200])
    return m.group(1) if m else None

def call_api(prompt):
    for attempt in range(5):
        try:
            resp = ant_client.messages.create(
                model=MODEL_ID,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                messages=[{"role": "user", "content": prompt}],
            )
            for block in resp.content:
                if block.type == "text":
                    return block.text.strip()
            return ""
        except Exception as e:
            msg = str(e)
            if "529" in msg or "overloaded" in msg.lower():
                wait = 60 * (attempt + 1)
            elif "429" in msg or "rate" in msg.lower():
                wait = 30 * (attempt + 1)
            else:
                raise
            print(f"  [RETRY {attempt+1}/5] waiting {wait}s: {msg[:80]}")
            time.sleep(wait)
    raise RuntimeError("API failed after 5 retries")

# Main
result_path = Path(sys.argv[1])
data_dir    = Path("data")

# figure out which benchmark JSON to load
bench_map = {
    "gpqa":  "gpqa_diamond_100.json",
    "medqa": "medqa_100.json",
    "legal": "legalbench_100.json",
    "mmlu_pro": "mmlu_pro_100.json",
}
bench_name = None
for k in bench_map:
    if k in result_path.name:
        bench_name = k; break
if not bench_name:
    sys.exit(f"Cannot determine benchmark from filename: {result_path.name}")

bench_items = json.loads((data_dir / bench_map[bench_name]).read_text(encoding="utf-8"))
results     = json.loads(result_path.read_text(encoding="utf-8"))

errors = [r for r in results if r["score"] is None]
print(f"Found {len(errors)} E questions in {result_path.name}, retrying...")

for r in errors:
    idx  = r["item_id"]
    item = bench_items[idx]
    correct = item["answer"]
    prompt  = make_mc_prompt(item)
    try:
        resp  = call_api(prompt)
        score = 1 if extract_mc(resp) == correct else 0
        tag   = "OK" if score else "WRONG"
        r["score"]         = score
        r["response_head"] = resp[:150]
    except Exception as e:
        resp  = f"[ERROR: {e}]"
        score = None
        tag   = "E"
        r["response_head"] = resp[:150]
    print(f"  item {idx:3d} correct={correct!r} -> {tag}  ({repr(resp[:80])})")
    time.sleep(DELAY)

# save back
result_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
valid   = [r for r in results if r["score"] is not None]
acc     = sum(r["score"] for r in valid) / len(valid) * 100 if valid else 0
remaining_e = sum(1 for r in results if r["score"] is None)
print(f"\nDone. Accuracy on {len(valid)} valid questions: {acc:.1f}%  ({remaining_e} still E)")

