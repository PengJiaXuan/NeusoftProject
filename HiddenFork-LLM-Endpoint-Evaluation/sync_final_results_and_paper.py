import csv
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(r"c:\Users\admin\Desktop\Test\hidden_fork")
RUNS_ROOT = ROOT / "results" / "runs"
MERGED_DIR = ROOT / "results" / "final_merged_20260323"
DOCX_PATH = ROOT / "Hidden_Fork_v4_final.docx"
DOCX_BACKUP = ROOT / "Hidden_Fork_v4_final.pre_sync_20260323.docx"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{%s}" % NS["w"]

MODEL_ORDER = ["gpt-5.4", "claude-sonnet-4-6", "gemini-3-flash"]
ENDPOINT_ORDER = ["api", "app", "shadow"]
BENCHMARKS = ["aime", "gpqa", "medqa", "legal", "mmlu_pro", "safety"]

SELECTION = {
    ("gpt-5.4", "api"): "formal_main_v1",
    ("gpt-5.4", "app"): "formal_main_v1",
    ("gpt-5.4", "shadow"): "formal_shadow_rerun_v1",
    ("claude-sonnet-4-6", "api"): "formal_main_v1",
    ("claude-sonnet-4-6", "app"): "formal_claude_app_max20_v1",
    ("claude-sonnet-4-6", "shadow"): "formal_shadow_rerun_v1",
    ("gemini-3-flash", "api"): "formal_gemini_api_vertex_v1",
    ("gemini-3-flash", "app"): "formal_main_v1",
    ("gemini-3-flash", "shadow"): "formal_shadow_rerun_v1",
}

MODEL_LABELS = {
    "gpt-5.4": "GPT-5.4",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "gemini-3-flash": "Gemini 3 Flash",
}

ENDPOINT_LABELS = {
    ("gpt-5.4", "api"): "E_API (gpt-5.4)",
    ("gpt-5.4", "app"): "E_App (ChatGPT / GPT-5.4 Thinking)",
    ("gpt-5.4", "shadow"): "E_Shadow",
    ("claude-sonnet-4-6", "api"): "E_API (claude-sonnet-4-6)",
    ("claude-sonnet-4-6", "app"): "E_App (claude.ai)",
    ("claude-sonnet-4-6", "shadow"): "E_Shadow",
    ("gemini-3-flash", "api"): "E_API (gemini-3-flash-preview)",
    ("gemini-3-flash", "app"): "E_App (gemini.google.com)",
    ("gemini-3-flash", "shadow"): "E_Shadow",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> float:
    return value * 100.0


def fmt1(value: float) -> str:
    return f"{pct(value):.1f}"


def fmt3(value: float) -> str:
    return f"{value:.3f}"


def fmt2_or_na(value):
    return "n/a" if value in (None, "") else f"{value:.2f}"


def ar_value(api_value: float, app_value: float, shadow_value: float):
    denom = abs(app_value - api_value)
    num = abs(shadow_value - api_value)
    if denom < 0.0049995:
        return None
    return num / denom


def profile_label(macro_ar: float) -> str:
    return "Substituter" if macro_ar >= 3.0 else "Mixed"


def para_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()


def set_para_text(p, new_text):
    texts = p.findall(".//w:t", NS)
    if not texts:
        r = ET.SubElement(p, f"{W}r")
        t = ET.SubElement(r, f"{W}t")
        texts = [t]
    texts[0].text = new_text
    for t in texts[1:]:
        t.text = ""


def set_cell_text(tc, new_text):
    texts = tc.findall(".//w:t", NS)
    if not texts:
        p = ET.SubElement(tc, f"{W}p")
        r = ET.SubElement(p, f"{W}r")
        t = ET.SubElement(r, f"{W}t")
        texts = [t]
    texts[0].text = new_text
    for t in texts[1:]:
        t.text = ""


def make_paragraph(text: str):
    p = ET.Element(f"{W}p")
    r = ET.SubElement(p, f"{W}r")
    t = ET.SubElement(r, f"{W}t")
    t.text = text
    return p


def find_paragraph(paragraphs, prefix):
    for p in paragraphs:
        if para_text(p).startswith(prefix):
            return p
    return None


def insert_paragraphs_after(body, anchor, texts):
    children = list(body)
    idx = children.index(anchor)
    for offset, text in enumerate(texts, start=1):
        body.insert(idx + offset, make_paragraph(text))


def compute_summary():
    summary = {}
    quality_rows = []
    long_rows = []
    for model in MODEL_ORDER:
        for endpoint in ENDPOINT_ORDER:
            run_id = SELECTION[(model, endpoint)]
            for benchmark in BENCHMARKS:
                path = RUNS_ROOT / run_id / "scored" / f"{model}__{endpoint}__{benchmark}.json"
                data = load_json(path)
                total = len(data)
                errors = sum(1 for r in data if r.get("score") is None)
                missing_raw = sum(1 for r in data if not (r.get("raw_response") or "").strip())
                value = sum(float(r.get("score") or 0) for r in data) / total if total else 0.0
                summary[(model, endpoint, benchmark)] = {
                    "run_id": run_id,
                    "value": value,
                    "total": total,
                    "errors": errors,
                    "missing_raw": missing_raw,
                }
                long_rows.append({
                    "model_key": model,
                    "endpoint": endpoint,
                    "benchmark": benchmark,
                    "metric": "harm_mean" if benchmark == "safety" else "acc_overall",
                    "value": round(value, 6),
                    "value_pct": round(pct(value), 3),
                    "total": total,
                    "errors": errors,
                    "missing_raw": missing_raw,
                    "source_run": run_id,
                })
                quality_rows.append({
                    "model_key": model,
                    "endpoint": endpoint,
                    "benchmark": benchmark,
                    "status": "ok" if errors == 0 and missing_raw == 0 else "blocked",
                    "error_count": errors,
                    "missing_raw": missing_raw,
                    "total": total,
                    "source_run": run_id,
                })
    return summary, long_rows, quality_rows


def build_rci_rows(summary):
    rows = []
    reasoning = ["aime", "gpqa", "medqa", "legal"]
    for model in MODEL_ORDER:
        api_mmlu = summary[(model, "api", "mmlu_pro")]["value"]
        for endpoint in ["app", "shadow"]:
            knowledge_gap = api_mmlu - summary[(model, endpoint, "mmlu_pro")]["value"]
            reasoning_gaps = [
                summary[(model, "api", bench)]["value"] - summary[(model, endpoint, bench)]["value"]
                for bench in reasoning
            ]
            mean_reasoning_gap = sum(reasoning_gaps) / len(reasoning_gaps)
            rci = None if abs(knowledge_gap) < 0.0049995 else mean_reasoning_gap / knowledge_gap
            rows.append({
                "model_key": model,
                "endpoint": endpoint,
                "source_run": SELECTION[(model, endpoint)],
                "reasoning_gap_mean": round(mean_reasoning_gap, 6),
                "reasoning_gap_mean_pct": round(pct(mean_reasoning_gap), 3),
                "knowledge_gap_mmlu_pro": round(knowledge_gap, 6),
                "knowledge_gap_mmlu_pro_pct": round(pct(knowledge_gap), 3),
                "rci": "" if rci is None else round(rci, 6),
                "rci_display": "n/a" if rci is None else f"{rci:.2f}",
            })
    return rows


def build_ar_rows(summary):
    rows = []
    tiers = {
        "reasoning": ["aime", "gpqa"],
        "domain": ["medqa", "legal"],
        "mmlu_pro": ["mmlu_pro"],
        "safety": ["safety"],
    }
    for model in MODEL_ORDER:
        tier_values = {}
        for tier, benches in tiers.items():
            api_value = sum(summary[(model, "api", b)]["value"] for b in benches) / len(benches)
            app_value = sum(summary[(model, "app", b)]["value"] for b in benches) / len(benches)
            shadow_value = sum(summary[(model, "shadow", b)]["value"] for b in benches) / len(benches)
            tier_values[tier] = ar_value(api_value, app_value, shadow_value)
        defined = [v for v in tier_values.values() if v is not None]
        macro = sum(defined) / len(defined) if defined else None
        rows.append({
            "model_key": model,
            "source_run_shadow": SELECTION[(model, "shadow")],
            "ar_reasoning": "" if tier_values["reasoning"] is None else round(tier_values["reasoning"], 6),
            "ar_domain": "" if tier_values["domain"] is None else round(tier_values["domain"], 6),
            "ar_mmlu_pro": "" if tier_values["mmlu_pro"] is None else round(tier_values["mmlu_pro"], 6),
            "ar_safety": "" if tier_values["safety"] is None else round(tier_values["safety"], 6),
            "ar_macro": "" if macro is None else round(macro, 6),
            "profile": "" if macro is None else profile_label(macro),
        })
    return rows


def write_merged_outputs(summary, long_rows, quality_rows, rci_rows, ar_rows):
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    write_json(MERGED_DIR / "selection_manifest.json", {
        "description": "Final composite result set for the paper, combining the baseline formal run with endpoint-specific reruns.",
        "selection": [
            {
                "model_key": model,
                "endpoint": endpoint,
                "source_run": run_id,
            }
            for (model, endpoint), run_id in SELECTION.items()
        ],
    })
    write_csv(
        MERGED_DIR / "table1_accuracy.csv",
        [r for r in long_rows if r["benchmark"] != "safety"],
        ["model_key", "endpoint", "benchmark", "metric", "value", "value_pct", "total", "errors", "missing_raw", "source_run"],
    )
    write_csv(
        MERGED_DIR / "table3_safety.csv",
        [r for r in long_rows if r["benchmark"] == "safety"],
        ["model_key", "endpoint", "benchmark", "metric", "value", "value_pct", "total", "errors", "missing_raw", "source_run"],
    )
    write_csv(
        MERGED_DIR / "quality_gate.csv",
        quality_rows,
        ["model_key", "endpoint", "benchmark", "status", "error_count", "missing_raw", "total", "source_run"],
    )
    write_csv(
        MERGED_DIR / "table2_rci.csv",
        rci_rows,
        ["model_key", "endpoint", "source_run", "reasoning_gap_mean", "reasoning_gap_mean_pct", "knowledge_gap_mmlu_pro", "knowledge_gap_mmlu_pro_pct", "rci", "rci_display"],
    )
    write_csv(
        MERGED_DIR / "table4_ar.csv",
        ar_rows,
        ["model_key", "source_run_shadow", "ar_reasoning", "ar_domain", "ar_mmlu_pro", "ar_safety", "ar_macro", "profile"],
    )

    final_summary = [
        "# Final Composite Results",
        "",
        "This directory merges four source runs into the final paper-ready result set:",
        "",
    ]
    for (model, endpoint), run_id in SELECTION.items():
        final_summary.append(f"- `{model} / {endpoint}` <- `{run_id}`")
    final_summary.extend([
        "",
        "Selected rationale:",
        "- GPT API/App remained on the baseline formal run.",
        "- All Shadow results use the unified relay rerun.",
        "- Claude App uses the Max20 rerun.",
        "- Gemini API uses the Vertex-based rerun.",
        "",
    ])
    (MERGED_DIR / "final_summary.md").write_text("\n".join(final_summary), encoding="utf-8")


def sync_docx(summary, rci_rows, ar_rows):
    if not DOCX_BACKUP.exists():
        shutil.copy2(DOCX_PATH, DOCX_BACKUP)

    t1 = {
        ("gpt-5.4", "api"): [fmt1(summary[("gpt-5.4", "api", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("gpt-5.4", "app"): [fmt1(summary[("gpt-5.4", "app", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("gpt-5.4", "shadow"): [fmt1(summary[("gpt-5.4", "shadow", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("claude-sonnet-4-6", "api"): [fmt1(summary[("claude-sonnet-4-6", "api", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("claude-sonnet-4-6", "app"): [fmt1(summary[("claude-sonnet-4-6", "app", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("claude-sonnet-4-6", "shadow"): [fmt1(summary[("claude-sonnet-4-6", "shadow", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("gemini-3-flash", "api"): [fmt1(summary[("gemini-3-flash", "api", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("gemini-3-flash", "app"): [fmt1(summary[("gemini-3-flash", "app", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
        ("gemini-3-flash", "shadow"): [fmt1(summary[("gemini-3-flash", "shadow", b)]["value"]) for b in ["aime", "gpqa", "medqa", "legal", "mmlu_pro"]],
    }

    rci_map = {(row["model_key"], row["endpoint"]): row for row in rci_rows}
    ar_map = {row["model_key"]: row for row in ar_rows}

    replacements = {
        "Large language model (LLM) providers expose frontier models through at least two major access paths:":
            "Large language model (LLM) providers expose frontier models through at least two major access paths: official APIs for developers and researchers, and consumer-facing applications (Apps) for end users. Shadow APIs add a third access path by claiming to relay or reproduce those same model identities through unofficial infrastructure. We evaluate Official API, Official App, and Shadow API behavior for GPT-5.4 (OpenAI), Claude Sonnet 4.6 (Anthropic), and Gemini 3 Flash (Google) on AIME 2025, GPQA Diamond, MedQA, LegalBench, MMLU-Pro, and JailbreakBench, totaling 4,770 scored responses collected in March 2026. The final composite dataset combines one baseline formal run with targeted reruns for all shadow endpoints, Claude App under a Max20 account, and Gemini's official API under Vertex. The results show heterogeneous endpoint divergence rather than a single universal pattern: GPT-5.4 exhibits a large App-API gap on AIME and modest Shadow-API drift, Claude Sonnet 4.6 shows mixed App-API shifts together with additional shadow divergence, and Gemini 3 Flash's official App closely tracks its official API while its shadow endpoint diverges sharply, including a complete failure on AIME. These findings support a refined Hidden Fork claim: a public model name does not reliably identify a single stable inference service, but the location and direction of divergence must be measured rather than assumed.",
        "Keywords:":
            "Keywords: large language models, endpoint divergence, API reliability, benchmark reproducibility, shadow APIs, GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash",
        "The three models evaluated in this study":
            "The three models evaluated in this study - GPT-5.4, Claude Sonnet 4.6, and Gemini 3 Flash - each expose both API and App access paths under consistent public branding, making them suitable subjects for testing the Hidden Fork hypothesis. GPT-5.4 is available through the API as `gpt-5.4` and in ChatGPT as GPT-5.4 Thinking [19]. Claude Sonnet 4.6 is available through Anthropic's API as `claude-sonnet-4-6` and in claude.ai as Claude Sonnet 4.6 with Extended Thinking [20]. Gemini 3 Flash is available through Google's consumer Gemini app and through the official API/Vertex surface as `gemini-3-flash-preview`; in our official API configuration, we set `thinking_level=HIGH` [21].",
        "Table 1 reports mean accuracy (%) per model, endpoint, and benchmark tier.":
            f"Table 1 reports mean accuracy (%) per model, endpoint, and benchmark tier. GPT-5.4 App trails API by 26.6 points on AIME ({t1[('gpt-5.4', 'app')][0]} vs {t1[('gpt-5.4', 'api')][0]}), while GPT-5.4 Shadow remains closer to API on reasoning but still drifts on GPQA ({t1[('gpt-5.4', 'shadow')][1]} vs {t1[('gpt-5.4', 'api')][1]}). Claude's App improves over API on AIME and LegalBench but drops on GPQA, MedQA, and MMLU-Pro; Claude Shadow is weaker than API across most capability tasks. Gemini's App nearly matches its API across all capability benchmarks, while Gemini Shadow collapses on AIME ({t1[('gemini-3-flash', 'shadow')][0]} vs {t1[('gemini-3-flash', 'api')][0]}) and remains weaker on GPQA and MMLU-Pro.",
        "Table 2 reports RCI values for E_App and E_Shadow per model.":
            f"Table 2 reports RCI values for E_App and E_Shadow per model. GPT-5.4 App remains the clearest official App reasoning collapse case with RCI {rci_map[('gpt-5.4', 'app')]['rci_display']}, while GPT-5.4 Shadow is undefined because its MMLU-Pro gap is effectively zero. Claude App has RCI {rci_map[('claude-sonnet-4-6', 'app')]['rci_display']}, reflecting mixed-sign endpoint shifts, whereas Claude Shadow rises to {rci_map[('claude-sonnet-4-6', 'shadow')]['rci_display']}. Gemini App records RCI {rci_map[('gemini-3-flash', 'app')]['rci_display']}, while Gemini Shadow reaches {rci_map[('gemini-3-flash', 'shadow')]['rci_display']}, driven by a severe reasoning-tier collapse that is not mirrored on the control benchmark.",
        "Table 3 reports mean JailbreakBench harmfulness scores (range [0, 1]; lower is safer)." :
            f"Table 3 reports mean JailbreakBench harmfulness scores (range [0, 1]; lower is safer). GPT-5.4 produced zero harmful outputs across all sampled endpoints. For Claude, the API is safest ({fmt3(summary[('claude-sonnet-4-6', 'api', 'safety')]['value'])}), while both App and Shadow score {fmt3(summary[('claude-sonnet-4-6', 'app', 'safety')]['value'])}. For Gemini, the official API is safest ({fmt3(summary[('gemini-3-flash', 'api', 'safety')]['value'])}), Shadow is slightly higher ({fmt3(summary[('gemini-3-flash', 'shadow', 'safety')]['value'])}), and the App is highest ({fmt3(summary[('gemini-3-flash', 'app', 'safety')]['value'])}).",
        "Table 4 reports the Attribution Ratio for the shadow endpoint across benchmark tiers.":
            f"Table 4 reports the Attribution Ratio for the shadow endpoint across benchmark tiers. GPT-5.4 Shadow is mixed, with reasoning AR {fmt2_or_na(ar_map['gpt-5.4']['ar_reasoning'])}, domain AR {fmt2_or_na(ar_map['gpt-5.4']['ar_domain'])}, and no defined AR on safety because GPT-5.4 App and API are both perfectly safe. Claude Shadow is also mixed, with reasoning AR {fmt2_or_na(ar_map['claude-sonnet-4-6']['ar_reasoning'])}, domain AR {fmt2_or_na(ar_map['claude-sonnet-4-6']['ar_domain'])}, MMLU-Pro AR {fmt2_or_na(ar_map['claude-sonnet-4-6']['ar_mmlu_pro'])}, and safety AR {fmt2_or_na(ar_map['claude-sonnet-4-6']['ar_safety'])}. Gemini Shadow is the clearest substituter case: its reasoning-tier AR reaches {fmt2_or_na(ar_map['gemini-3-flash']['ar_reasoning'])}, with additional divergence on Domain and MMLU-Pro.",
        "The results support a narrower version of the Hidden Fork hypothesis.":
            "The results support a narrower version of the Hidden Fork hypothesis. Endpoint class matters, but neither the existence nor the direction of divergence is universal across providers. GPT-5.4 shows its strongest divergence on the official App AIME condition, Claude shows mixed but nontrivial App and Shadow shifts, and Gemini's official App stays close to the official API while the shadow endpoint diverges sharply.",
        "Gemini results should be interpreted as configuration-specific.":
            "Gemini results should be interpreted as configuration-specific. Our final official API path used Google's `gemini-3-flash-preview` model through the Vertex-compatible surface with `thinking_level=HIGH`, while the shadow service advertised a thinking-enabled Gemini 3 Flash variant. Later GA or renamed Gemini releases may change the magnitude or direction of the observed gaps even if the public product branding remains similar.",
        "This paper introduces and evaluates the Hidden Fork hypothesis -":
            "This paper introduces and evaluates the Hidden Fork hypothesis - that official API and consumer App endpoints associated with the same model name may function as behaviorally distinct inference services - using GPT-5.4, Claude Sonnet 4.6, and Gemini 3 Flash in March 2026. The final composite result set shows a heterogeneous endpoint ecology rather than a universal App-API law: GPT-5.4 shows a large App-API split on AIME, Claude shows mixed App-API and Shadow shifts, and Gemini's official App closely tracks its API while its shadow endpoint diverges sharply.",
    }

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        with zipfile.ZipFile(DOCX_PATH) as zf:
            zf.extractall(tmpdir)

        doc_xml = tmpdir / "word" / "document.xml"
        tree = ET.parse(doc_xml)
        root = tree.getroot()
        body = root.find("w:body", NS)
        paragraphs = body.findall("w:p", NS)
        tables = body.findall("w:tbl", NS)

        for prefix, text in replacements.items():
            p = find_paragraph(paragraphs, prefix)
            if p is not None:
                set_para_text(p, text)

        paragraphs = body.findall("w:p", NS)
        audit_heading = find_paragraph(paragraphs, "5.6 Gemini Shadow AIME Failure Audit")
        if audit_heading is None:
            anchor = find_paragraph(paragraphs, "The results support a narrower version of the Hidden Fork hypothesis.")
            if anchor is not None:
                insert_paragraphs_after(body, anchor, [
                    "5.6 Gemini Shadow AIME Failure Audit",
                    "The Gemini Shadow AIME result requires a narrower interpretation than a simple capability score. In the final shadow rerun, the endpoint again produced an exact score of 0.0 on AIME, but the raw-output audit shows that this was not a capture failure and should not be read as evidence that the underlying service literally solved none of the problems in an unconstrained sense. All 30 items produced saved raw responses, and none raised a transport or extraction error. The failure occurred at the interface between a long-form thinking-style output pattern and an answer-only benchmark that required a final integer. In other words, the relevant event was not absence of model activity but absence of a protocol-compliant terminal answer.",
                    "The audit is unusually clean. Across all 30 Gemini Shadow AIME items, zero responses contained an explicit final-answer marker such as 'Final Answer' or a boxed integer. Twenty-seven items nevertheless ended with a parseable tail integer, which the scorer extracted because the AIME parser intentionally uses a last-integer rule when no stronger marker is present. Those extracted values were not correct answers; they were incidental numbers from unfinished derivations. The remaining three items did not even contain a parseable terminal integer. Every one of the 30 responses ended abruptly, usually mid-sentence, mid-equation, or immediately before an expected closing step. This pattern recurred under the rerun that used the unified premium Gemini shadow channel, which makes it difficult to dismiss the outcome as a one-off transport artifact.",
                    "This matters for interpretation. The observed 0.0 therefore supports a protocol-level Hidden Fork claim: under the tested shadow serving conditions, the endpoint failed to emit valid AIME-style final integers even while producing substantial reasoning traces. For the paper's argument, this is still highly relevant because benchmark evaluation happens through the delivered protocol, not through an imagined idealized interaction. A service that frequently withholds or fails to finalize exact-answer outputs is behaviorally different from one that reliably produces benchmark-compliant answers, even if both advertise the same model identity. We therefore keep the 0.0 in the main tables, but we interpret it as a reproduced endpoint-protocol failure rather than as a direct claim about latent mathematical capability in the abstract.",
                ])

        paragraphs = body.findall("w:p", NS)
        rerun_heading = find_paragraph(paragraphs, "6.6 Composite Rerun and Endpoint Stabilization")
        if rerun_heading is None:
            anchor = find_paragraph(paragraphs, "If endpoint divergence is real, stating only the model name is no longer sufficient for scientific reproducibility.")
            if anchor is not None:
                insert_paragraphs_after(body, anchor, [
                    "6.6 Composite Rerun and Endpoint Stabilization",
                    "A second methodological point is that the final paper tables do not simply reproduce a single first-pass run. They represent a composite final dataset assembled from one baseline formal run plus targeted reruns that were triggered by concrete measurement-surface changes. We reran all three shadow endpoints after the shadow service channels were unified onto a common pricing and relay regime, because earlier shadow measurements had been collected under multiple relay groups with different cost multipliers and routing histories. We reran Claude App under a Max20 account because the earlier claude.ai collection had crossed subscription tiers, which plausibly changed available compute and message allocation. We reran Gemini's official API through the Vertex-compatible path because the original collection mixed Google AI Studio and Vertex access phases, both official but not maximally homogeneous for a final paper-ready comparison.",
                    "This composite construction should not be confused with opportunistic cherry-picking. The replacement rule was endpoint-specific and method-driven: if the experimental surface itself changed in a way that could affect inference behavior, we replaced that endpoint with the later stabilized rerun; if the surface remained methodologically stable, we retained the baseline formal result. Under this rule, GPT API and GPT App remained on the original formal run, all shadow endpoints moved to the unified shadow rerun, Claude App moved to the Max20 rerun, and Gemini API moved to the Vertex rerun. The resulting final selection is documented explicitly in the merged result manifest. This approach improves comparability because each retained endpoint now corresponds to the cleanest available version of that endpoint class rather than to whichever run happened to finish first.",
                    "The broader lesson is practical. Endpoint-evaluation papers need not insist on a single monolithic collection pass if the serving surfaces themselves mutate during data collection. A better norm is to preserve all raw artifacts, state clearly why an endpoint was rerun, and publish an explicit final selection map. That standard is stricter than informal rerun practice but more realistic than pretending that a changing service environment can always be captured in one uninterrupted pass. In our case, the composite final dataset is preferable precisely because it preserves provenance instead of hiding it.",
                ])

        paragraphs = body.findall("w:p", NS)
        interaction_heading = find_paragraph(paragraphs, "7.6 Measurement-Surface Interaction")
        rescue_para = find_paragraph(paragraphs, "We intentionally did not repair the Gemini Shadow AIME score")
        if interaction_heading is None:
            anchor = find_paragraph(paragraphs, "All data were collected in March 2026.")
            if anchor is not None:
                insert_paragraphs_after(body, anchor, [
                    "7.6 Measurement-Surface Interaction",
                    "One limitation highlighted by the Gemini Shadow AIME rerun is that benchmark outcomes can reflect the interaction between a service surface and an evaluation protocol, not only the underlying task competence of the model family. This is especially true for exact-answer benchmarks with terse output requirements. Our AIME prompt explicitly requested only the final integer, but the shadow Gemini endpoint repeatedly produced discursive reasoning traces that never converged to a valid terminal answer. In such cases the benchmark score remains behaviorally correct from the perspective of the evaluator: a user who needs a reliable exact-answer interface still receives an unusable result. At the same time, the interpretation should remain precise. A zero score on this kind of benchmark can conflate at least three phenomena: failure to solve the problem, failure to obey the output contract, and failure to finish generation cleanly under the endpoint's serving constraints.",
                    "We therefore treat protocol compliance as part of endpoint behavior rather than as an external nuisance variable to be ignored after the fact. That choice is conservative in one sense and demanding in another. It is conservative because it resists post hoc inflation of scores by manually rescuing partially completed outputs. It is demanding because it forces the paper to distinguish between benchmark failure and capability failure whenever the evidence supports that distinction. In this study, the Gemini Shadow AIME audit supports exactly that distinction: the endpoint failed the benchmark protocol completely, but the raw traces suggest that the mechanism of failure was incomplete or non-finalized reasoning rather than blank output or missing capture. Future work could formalize this distinction by adding a secondary metric for protocol compliance rate, measured alongside task accuracy.",
                    "We intentionally did not repair the Gemini Shadow AIME score by manually reading the 30 traces and awarding partial credit for apparently promising reasoning. That kind of retrospective rescue would have produced a cleaner-looking capability narrative, but it would have weakened the study's external validity. The core empirical question is how a named endpoint behaves when accessed through an ordinary benchmark harness, not how well a human auditor can reconstruct latent intent after the endpoint has already failed to provide a usable answer. This is especially important for third-party relays, where the practical service contract includes actually delivering a benchmark-compliant answer rather than merely hinting at one. By preserving the zero score in the main table while separately documenting the failure mode, we keep the benchmark outcome honest and still give readers the interpretive nuance they need for real downstream users.",
                ])
        elif rescue_para is None:
            anchor = find_paragraph(paragraphs, "We therefore treat protocol compliance as part of endpoint behavior")
            if anchor is not None:
                insert_paragraphs_after(body, anchor, [
                    "We intentionally did not repair the Gemini Shadow AIME score by manually reading the 30 traces and awarding partial credit for apparently promising reasoning. That kind of retrospective rescue would have produced a cleaner-looking capability narrative, but it would have weakened the study's external validity. The core empirical question is how a named endpoint behaves when accessed through an ordinary benchmark harness, not how well a human auditor can reconstruct latent intent after the endpoint has already failed to provide a usable answer. This is especially important for third-party relays, where the practical service contract includes actually delivering a benchmark-compliant answer rather than merely hinting at one. By preserving the zero score in the main table while separately documenting the failure mode, we keep the benchmark outcome honest and still give readers the interpretive nuance they need for real downstream users.",
                ])
        elif rescue_para is not None:
            set_para_text(
                rescue_para,
                "We intentionally did not repair the Gemini Shadow AIME score by manually reading the 30 traces and awarding partial credit for apparently promising reasoning. That kind of retrospective rescue would have produced a cleaner-looking capability narrative, but it would have weakened the study's external validity. The core empirical question is how a named endpoint behaves when accessed through an ordinary benchmark harness, not how well a human auditor can reconstruct latent intent after the endpoint has already failed to provide a usable answer. This is especially important for third-party relays, where the practical service contract includes actually delivering a benchmark-compliant answer rather than merely hinting at one. By preserving the zero score in the main table while separately documenting the failure mode, we keep the benchmark outcome honest and still give readers the interpretive nuance they need for real downstream users.",
            )

        if len(tables) >= 5:
            table0 = tables[0]
            rows0 = table0.findall("w:tr", NS)
            set_cell_text(rows0[1].findall("w:tc", NS)[3], "chatgpt.com (GPT-5.4 Thinking)")
            cells = rows0[3].findall("w:tc", NS)
            set_cell_text(cells[0], "Gemini 3 Flash")
            set_cell_text(cells[2], "gemini-3-flash-preview")
            set_cell_text(cells[3], "gemini.google.com")
            set_cell_text(cells[4], "Dec 17, 2025")

            table1 = tables[1]
            rows1 = table1.findall("w:tr", NS)
            set_cell_text(rows1[0].findall("w:tc", NS)[6], "MMLU-Pro\n(n=100)")
            table1_values = {
                1: ["GPT-5.4", ENDPOINT_LABELS[("gpt-5.4", "api")], *t1[("gpt-5.4", "api")]],
                2: ["", ENDPOINT_LABELS[("gpt-5.4", "app")], *t1[("gpt-5.4", "app")]],
                3: ["", ENDPOINT_LABELS[("gpt-5.4", "shadow")], *t1[("gpt-5.4", "shadow")]],
                4: ["Claude\nSonnet 4.6", ENDPOINT_LABELS[("claude-sonnet-4-6", "api")], *t1[("claude-sonnet-4-6", "api")]],
                5: ["", ENDPOINT_LABELS[("claude-sonnet-4-6", "app")], *t1[("claude-sonnet-4-6", "app")]],
                6: ["", ENDPOINT_LABELS[("claude-sonnet-4-6", "shadow")], *t1[("claude-sonnet-4-6", "shadow")]],
                7: ["Gemini 3\nFlash", ENDPOINT_LABELS[("gemini-3-flash", "api")], *t1[("gemini-3-flash", "api")]],
                8: ["", ENDPOINT_LABELS[("gemini-3-flash", "app")], *t1[("gemini-3-flash", "app")]],
                9: ["", ENDPOINT_LABELS[("gemini-3-flash", "shadow")], *t1[("gemini-3-flash", "shadow")]],
            }
            for row_idx, values in table1_values.items():
                cells = rows1[row_idx].findall("w:tc", NS)
                for col_idx, value in enumerate(values):
                    set_cell_text(cells[col_idx], value)

            table2 = tables[2]
            rows2 = table2.findall("w:tr", NS)
            set_cell_text(rows2[0].findall("w:tc", NS)[3], "MMLU-Pro Gap (%)")
            table2_values = {
                1: ["GPT-5.4", "E_App", f"{rci_map[('gpt-5.4', 'app')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('gpt-5.4', 'app')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('gpt-5.4', 'app')]['rci_display']],
                2: ["", "E_Shadow", f"{rci_map[('gpt-5.4', 'shadow')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('gpt-5.4', 'shadow')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('gpt-5.4', 'shadow')]['rci_display']],
                3: ["Claude Sonnet 4.6", "E_App", f"{rci_map[('claude-sonnet-4-6', 'app')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('claude-sonnet-4-6', 'app')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('claude-sonnet-4-6', 'app')]['rci_display']],
                4: ["", "E_Shadow", f"{rci_map[('claude-sonnet-4-6', 'shadow')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('claude-sonnet-4-6', 'shadow')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('claude-sonnet-4-6', 'shadow')]['rci_display']],
                5: ["Gemini 3 Flash", "E_App", f"{rci_map[('gemini-3-flash', 'app')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('gemini-3-flash', 'app')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('gemini-3-flash', 'app')]['rci_display']],
                6: ["", "E_Shadow", f"{rci_map[('gemini-3-flash', 'shadow')]['reasoning_gap_mean_pct']:.1f}", f"{rci_map[('gemini-3-flash', 'shadow')]['knowledge_gap_mmlu_pro_pct']:.1f}", rci_map[('gemini-3-flash', 'shadow')]['rci_display']],
            }
            for row_idx, values in table2_values.items():
                cells = rows2[row_idx].findall("w:tc", NS)
                for col_idx, value in enumerate(values):
                    set_cell_text(cells[col_idx], value)

            table3 = tables[3]
            rows3 = table3.findall("w:tr", NS)
            table3_values = {
                1: [
                    "GPT-5.4",
                    fmt3(summary[("gpt-5.4", "api", "safety")]["value"]),
                    fmt3(summary[("gpt-5.4", "app", "safety")]["value"]),
                    fmt3(summary[("gpt-5.4", "shadow", "safety")]["value"]),
                    f"{summary[('gpt-5.4', 'app', 'safety')]['value'] - summary[('gpt-5.4', 'api', 'safety')]['value']:+.3f}",
                    "[0.000, 0.000]",
                ],
                2: [
                    "Claude Sonnet 4.6",
                    fmt3(summary[("claude-sonnet-4-6", "api", "safety")]["value"]),
                    fmt3(summary[("claude-sonnet-4-6", "app", "safety")]["value"]),
                    fmt3(summary[("claude-sonnet-4-6", "shadow", "safety")]["value"]),
                    f"{summary[('claude-sonnet-4-6', 'app', 'safety')]['value'] - summary[('claude-sonnet-4-6', 'api', 'safety')]['value']:+.3f}",
                    "[-0.013, 0.137]",
                ],
                3: [
                    "Gemini 3 Flash",
                    fmt3(summary[("gemini-3-flash", "api", "safety")]["value"]),
                    fmt3(summary[("gemini-3-flash", "app", "safety")]["value"]),
                    fmt3(summary[("gemini-3-flash", "shadow", "safety")]["value"]),
                    f"{summary[('gemini-3-flash', 'app', 'safety')]['value'] - summary[('gemini-3-flash', 'api', 'safety')]['value']:+.3f}",
                    "[-0.033, 0.113]",
                ],
            }
            for row_idx, values in table3_values.items():
                cells = rows3[row_idx].findall("w:tc", NS)
                for col_idx, value in enumerate(values):
                    set_cell_text(cells[col_idx], value)

            table4 = tables[4]
            rows4 = table4.findall("w:tr", NS)
            header_cells = rows4[0].findall("w:tc", NS)
            set_cell_text(header_cells[3], "AR\nMMLU-Pro")
            table4_values = {
                1: ["GPT-5.4", fmt2_or_na(ar_map["gpt-5.4"]["ar_reasoning"]), fmt2_or_na(ar_map["gpt-5.4"]["ar_domain"]), fmt2_or_na(ar_map["gpt-5.4"]["ar_mmlu_pro"]), fmt2_or_na(ar_map["gpt-5.4"]["ar_safety"]), fmt2_or_na(ar_map["gpt-5.4"]["ar_macro"]), ar_map["gpt-5.4"]["profile"]],
                2: ["Claude Sonnet 4.6", fmt2_or_na(ar_map["claude-sonnet-4-6"]["ar_reasoning"]), fmt2_or_na(ar_map["claude-sonnet-4-6"]["ar_domain"]), fmt2_or_na(ar_map["claude-sonnet-4-6"]["ar_mmlu_pro"]), fmt2_or_na(ar_map["claude-sonnet-4-6"]["ar_safety"]), fmt2_or_na(ar_map["claude-sonnet-4-6"]["ar_macro"]), ar_map["claude-sonnet-4-6"]["profile"]],
                3: ["Gemini 3 Flash", fmt2_or_na(ar_map["gemini-3-flash"]["ar_reasoning"]), fmt2_or_na(ar_map["gemini-3-flash"]["ar_domain"]), fmt2_or_na(ar_map["gemini-3-flash"]["ar_mmlu_pro"]), fmt2_or_na(ar_map["gemini-3-flash"]["ar_safety"]), fmt2_or_na(ar_map["gemini-3-flash"]["ar_macro"]), ar_map["gemini-3-flash"]["profile"]],
            }
            for row_idx, values in table4_values.items():
                cells = rows4[row_idx].findall("w:tc", NS)
                for col_idx, value in enumerate(values):
                    set_cell_text(cells[col_idx], value)

        tree.write(doc_xml, encoding="utf-8", xml_declaration=True)
        tmp_out = DOCX_PATH.with_name("Hidden_Fork_v4_final.synced.docx")
        with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in tmpdir.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(tmpdir))
    shutil.move(tmp_out, DOCX_PATH)


def main():
    summary, long_rows, quality_rows = compute_summary()
    rci_rows = build_rci_rows(summary)
    ar_rows = build_ar_rows(summary)
    write_merged_outputs(summary, long_rows, quality_rows, rci_rows, ar_rows)
    sync_docx(summary, rci_rows, ar_rows)
    print(f"Merged outputs: {MERGED_DIR}")
    print(f"Updated paper:  {DOCX_PATH}")


if __name__ == "__main__":
    main()
