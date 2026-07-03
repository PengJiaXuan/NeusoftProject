"""
Prepare benchmark data files for the Hidden Fork experiment.

Primary benchmark set:
- AIME 2025
- GPQA Diamond
- MMLU-Pro
- MedQA
- LegalBench
- JailbreakBench
"""

import hashlib
import json
import os
import random
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SAMPLE_SEED = 42
random.seed(SAMPLE_SEED)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOCK_PATH = DATA_DIR / "dataset_lock.json"

DATA_DIR.mkdir(exist_ok=True)

DATASET_LOCK = {}
CHOICE_LABELS = list("ABCDEFGHIJ")


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_lock():
    ordered = {k: DATASET_LOCK[k] for k in sorted(DATASET_LOCK)}
    with open(LOCK_PATH, "w", encoding="utf-8") as fh:
        json.dump(ordered, fh, indent=2, ensure_ascii=False)
    print(f"  wrote dataset lock -> {LOCK_PATH}")


def register_dataset(path, *, source_name, source_split, sample_seed, n_items):
    DATASET_LOCK[path.name] = {
        "filename": path.name,
        "sha256": file_sha256(path),
        "source_name": source_name,
        "source_split": source_split,
        "sample_seed": sample_seed,
        "n_items": n_items,
        "created_at_utc": utc_now(),
    }


def save(name, items, *, source_name, source_split, sample_seed):
    path = DATA_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)
    register_dataset(
        path,
        source_name=source_name,
        source_split=source_split,
        sample_seed=sample_seed,
        n_items=len(items),
    )
    print(f"  saved {len(items)} items -> {path}")


def register_existing(path, *, source_name, source_split, sample_seed):
    items = json.loads(path.read_text(encoding="utf-8"))
    register_dataset(
        path,
        source_name=source_name,
        source_split=source_split,
        sample_seed=sample_seed,
        n_items=len(items),
    )
    print(f"  registered existing dataset -> {path}")


def stratified_sample(items, key, n):
    buckets = defaultdict(list)
    for item in items:
        buckets[item.get(key, "unknown")].append(item)

    groups = list(buckets.values())
    if not groups:
        return []

    result = []
    group_index = 0
    while len(result) < n:
        group = groups[group_index % len(groups)]
        if group:
            result.append(group.pop(random.randrange(len(group))))
        group_index += 1
        if all(not group for group in groups):
            break

    random.shuffle(result)
    return result[:n]


def normalize_answer_label(answer, choices):
    if isinstance(answer, int):
        if 0 <= answer < len(choices):
            return CHOICE_LABELS[answer]

    answer_text = str(answer).strip()
    if answer_text.upper() in CHOICE_LABELS[: len(choices)]:
        return answer_text.upper()

    if answer_text.isdigit():
        idx = int(answer_text)
        if 0 <= idx < len(choices):
            return CHOICE_LABELS[idx]
        if 1 <= idx <= len(choices):
            return CHOICE_LABELS[idx - 1]

    for idx, choice in enumerate(choices):
        if answer_text == str(choice).strip():
            return CHOICE_LABELS[idx]

    raise ValueError(f"Cannot normalize answer {answer!r} for {len(choices)} choices")


def normalize_choices(raw_choices):
    if isinstance(raw_choices, dict):
        keys = sorted(raw_choices.keys())
        return [str(raw_choices[k]).strip() for k in keys]
    if isinstance(raw_choices, (list, tuple)):
        return [str(choice).strip() for choice in raw_choices]
    raise ValueError(f"Unsupported choices payload: {type(raw_choices)!r}")


def prepare_gpqa(n=100):
    print("\n[1/6] GPQA Diamond ...")
    token = os.environ.get("HF_TOKEN", "")
    from datasets import load_dataset

    try:
        kwargs = {"token": token} if token else {}
        ds = load_dataset("Idavidrein/gpqa", "gpqa_diamond", split="train", **kwargs)
        items = []
        for row in ds:
            choices = [
                row["Correct Answer"],
                row["Incorrect Answer 1"],
                row["Incorrect Answer 2"],
                row["Incorrect Answer 3"],
            ]
            idxs = list(range(4))
            random.shuffle(idxs)
            shuffled = [choices[idx] for idx in idxs]
            correct = CHOICE_LABELS[idxs.index(0)]
            items.append(
                {
                    "question": row["Question"],
                    "choices": shuffled,
                    "answer": correct,
                    "subdomain": row.get("Subdomain", "unknown"),
                }
            )

        save(
            "gpqa_diamond_100",
            random.sample(items, min(n, len(items))),
            source_name="Idavidrein/gpqa",
            source_split="train:gpqa_diamond",
            sample_seed=SAMPLE_SEED,
        )
        return
    except Exception as exc:
        path = DATA_DIR / "gpqa_diamond_100.json"
        if path.exists():
            print(f"  online fetch failed, keeping existing GPQA file: {exc}")
            register_existing(
                path,
                source_name="existing:gpqa_diamond_100",
                source_split="manual_or_cached",
                sample_seed=SAMPLE_SEED,
            )
            return
        raise


def prepare_mmlu_pro(n=100):
    print("\n[2/6] MMLU-Pro ...")
    from datasets import load_dataset

    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    items = []
    for row in ds:
        question = str(row.get("question", row.get("problem", ""))).strip()
        if not question:
            continue

        choices = normalize_choices(row.get("options", row.get("choices", [])))
        if len(choices) < 4:
            continue

        try:
            answer = normalize_answer_label(
                row.get("answer", row.get("answer_index", row.get("label"))),
                choices,
            )
        except ValueError:
            continue

        items.append(
            {
                "question": question,
                "choices": choices,
                "answer": answer,
                "category": row.get("category")
                or row.get("subject")
                or row.get("domain")
                or row.get("field")
                or "unknown",
            }
        )

    sampled = stratified_sample(items, "category", n)
    save(
        "mmlu_pro_100",
        sampled,
        source_name="TIGER-Lab/MMLU-Pro",
        source_split="test",
        sample_seed=SAMPLE_SEED,
    )


def prepare_medqa(n=100):
    print("\n[3/6] MedQA ...")
    from datasets import load_dataset

    try:
        ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="test")
        items = []
        for row in ds:
            options = row["options"]
            items.append(
                {
                    "question": row["question"],
                    "choices": [options["A"], options["B"], options["C"], options["D"]],
                    "answer": str(row["answer_idx"]).strip().upper(),
                }
            )
        save(
            "medqa_100",
            random.sample(items, min(n, len(items))),
            source_name="GBaker/MedQA-USMLE-4-options",
            source_split="test",
            sample_seed=SAMPLE_SEED,
        )
        return
    except Exception as exc:
        print(f"  primary source failed: {exc}")

    ds = load_dataset("bigbio/med_qa", "med_qa_en_4options_bigbio_qa", split="test")
    items = []
    for row in ds:
        choices = [choice["text"] for choice in row["choices"][:4]]
        if len(choices) < 4:
            continue
        try:
            answer = normalize_answer_label(row.get("answer", row.get("label", "A")), choices)
        except ValueError:
            continue
        items.append({"question": row["question"], "choices": choices, "answer": answer})

    save(
        "medqa_100",
        random.sample(items, min(n, len(items))),
        source_name="bigbio/med_qa",
        source_split="test:med_qa_en_4options_bigbio_qa",
        sample_seed=SAMPLE_SEED,
    )


def prepare_legalbench(n=100):
    print("\n[4/6] LegalBench ...")
    from datasets import load_dataset

    ds = None
    used_task = None
    for task in ("scalr", "contract_nli_explicit_identification", "contract_nli_no_information", "abercrombie"):
        try:
            ds = load_dataset("nguha/legalbench", task, split="test")
            used_task = task
            break
        except Exception:
            continue

    if ds is None:
        path = DATA_DIR / "legalbench_100.json"
        if path.exists():
            print("  online fetch failed, keeping existing LegalBench file.")
            register_existing(
                path,
                source_name="existing:legalbench_100",
                source_split="manual_or_cached",
                sample_seed=SAMPLE_SEED,
            )
            return
        raise RuntimeError("Could not load any supported LegalBench task")

    items = []
    for row in ds:
        raw = str(row.get("answer", row.get("label", "yes"))).strip().lower()
        correct = "A" if raw in ("yes", "true", "1", "entailment") else "B"
        question = str(row.get("text", row.get("passage", row.get("question", ""))))[:2000]
        items.append(
            {
                "question": question,
                "choices": ["Yes", "No", "N/A", "Cannot be determined"],
                "answer": correct,
            }
        )

    save(
        "legalbench_100",
        random.sample(items, min(n, len(items))),
        source_name="nguha/legalbench",
        source_split=f"test:{used_task}",
        sample_seed=SAMPLE_SEED,
    )


def prepare_aime():
    print("\n[5/6] AIME 2025 ...")
    path = DATA_DIR / "aime_2025.json"
    if path.exists():
        register_existing(
            path,
            source_name="manual:aime_2025",
            source_split="AIME I + II",
            sample_seed="manual",
        )
        return

    template = []
    for idx in range(15):
        template.append(
            {
                "id": f"AIME_2025_I_{idx + 1}",
                "question": f"[FILL: AIME 2025 Part I Problem {idx + 1}]",
                "answer": "[FILL: integer 0-999]",
                "source": "AIME 2025 Part I",
            }
        )
    for idx in range(15):
        template.append(
            {
                "id": f"AIME_2025_II_{idx + 1}",
                "question": f"[FILL: AIME 2025 Part II Problem {idx + 1}]",
                "answer": "[FILL: integer 0-999]",
                "source": "AIME 2025 Part II",
            }
        )

    save(
        "aime_2025",
        template,
        source_name="manual:aime_2025",
        source_split="AIME I + II",
        sample_seed="manual",
    )


def prepare_jailbreakbench(n=100):
    print("\n[6/6] JailbreakBench ...")
    url = "https://raw.githubusercontent.com/JailbreakBench/jailbreakbench/main/src/jailbreakbench/data/behaviors.json"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = json.loads(response.read())

        items = [{"prompt": row["Behavior"], "category": row.get("Category", "")} for row in raw]
        save(
            "jailbreakbench_100",
            random.sample(items, min(n, len(items))),
            source_name="JailbreakBench/jailbreakbench",
            source_split="behaviors.json",
            sample_seed=SAMPLE_SEED,
        )
        return
    except Exception as exc:
        path = DATA_DIR / "jailbreakbench_100.json"
        if path.exists():
            print(f"  online fetch failed, keeping existing JailbreakBench file: {exc}")
            register_existing(
                path,
                source_name="existing:jailbreakbench_100",
                source_split="manual_or_cached",
                sample_seed=SAMPLE_SEED,
            )
            return
        raise


def main():
    print("=" * 60)
    print("Hidden Fork data preparation")
    print("Primary benchmark set: AIME, GPQA Diamond, MMLU-Pro, MedQA, LegalBench, JailbreakBench")
    print("=" * 60)

    prepare_gpqa()
    prepare_mmlu_pro()
    prepare_medqa()
    prepare_legalbench()
    prepare_aime()
    prepare_jailbreakbench()
    write_lock()

    print("\nDone.")
    print("Generated files:")
    print("  data/gpqa_diamond_100.json")
    print("  data/mmlu_pro_100.json")
    print("  data/medqa_100.json")
    print("  data/legalbench_100.json")
    print("  data/aime_2025.json")
    print("  data/jailbreakbench_100.json")
    print("  data/dataset_lock.json")


if __name__ == "__main__":
    main()
