# Hidden Fork: Measuring Behavioral Divergence Across API, Web App, and Shadow Relay Endpoints for Large Language Models

---

## Abstract

I noticed something odd while debugging GPT-5.4 on math problems: the same model scored 93.3% through the API but only 66.7% through the ChatGPT browser. That 26.6-point gap on the same afternoon made me wonder how much the access path matters for benchmark scores. So I tested three models — GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash — each through three routes (official API, official web app, shadow relay) on six benchmarks covering math, science, medicine, law, broad knowledge, and safety (530 total items across AIME 2025, GPQA Diamond, MedQA, LegalBench, MMLU-Pro, and JailbreakBench). The results did not behave. Claude's web app actually beat its own API on AIME by 23 points, then lost on GPQA by 12 — directions flipping between benchmarks. Gemini scored 0.0% on AIME through the relay, not because the model failed, but because the relay chopped every response before it finished reasoning. Safety numbers moved too — Claude leaked more harmful content on non-API surfaces. The short version: writing down "GPT-5.4" is not enough to pin down a measurement. You need to say which endpoint, which parameters, which subscription tier. Right now almost nobody does.

---

## 1. Introduction

### 1.1 Background

This started with a debugging session in February 2026, not a research proposal. I was testing GPT-5.4 on the 2025 AIME math problems — 30 competition-level questions — and I sent Problem 1 through the OpenAI Python SDK: `openai.chat.completions.create`, model string `gpt-5.4`, `temperature=0`, `reasoning_effort="high"`. Correct answer. Then I copy-pasted the exact same problem into the ChatGPT browser window, picked GPT-5.4, turned on Extended thinking, hit send. Wrong answer. I tried Problem 2. Same thing — SDK right, browser wrong. By the time I finished all 30 problems, the SDK had scored 93.3% and ChatGPT had scored 66.7%. That is a 26.6-point gap on the same model, tested within the same afternoon.

I went looking for an explanation. On the SDK side I knew exactly what was happening: the model string, the temperature, the reasoning budget — all explicit in my code. On the ChatGPT side I knew almost nothing. There is some system prompt that ChatGPT prepends to every query; I have never seen it. There is some token budget for the thinking phase; I do not know how big it is. My Plus account ($20/month) presumably gets less compute per query than what the API allocates when I set `reasoning_effort="high"`. I checked OpenAI's documentation — none of this is written down anywhere.

I also wanted to test a third access route. In mainland China, where I was running these experiments, a lot of developers rely on shadow relay services. These are third-party resellers: you send them an OpenAI-format API call, they forward it to the real provider and charge a markup. I found one that listed GPT-5.4, Claude Sonnet 4.6, and Gemini 3 Flash. Whether it was actually serving genuine model weights, or running quantized copies, or doing something else entirely — I had no way to tell from my end.

### 1.2 Problem Statement

Here is the thing that bothered me. When a benchmark paper reports "GPT-5.4 scores 89% on GPQA," the reader assumes 89% is a fixed property of the model. But if the score changes depending on whether you used the Python SDK or the ChatGPT browser, that assumption breaks. I wanted to test how badly it breaks.

So I set up a systematic comparison. Three models — GPT-5.4 (OpenAI), Claude Sonnet 4.6 (Anthropic), Gemini 3 Flash (Google). Three endpoints each — the official API, the official web app (ChatGPT / claude.ai / gemini.google.com), and the shadow relay. Six benchmarks: AIME 2025 for math (n = 30), GPQA Diamond for graduate science (n = 100), MedQA for medicine (n = 100), LegalBench for law (n = 100), MMLU-Pro for broad knowledge (n = 100), and a JailbreakBench safety set (n = 100). All three APIs set to reasoning effort "high" — one step below maximum — so no API condition would obviously outrun its corresponding web app.

### 1.3 Key Findings

The results did not follow a clean pattern. The GPT-5.4 AIME gap was the biggest single number, but that same model's scores on GPQA, MedQA, LegalBench, and MMLU-Pro barely moved across endpoints (1–2 points). Claude Sonnet 4.6 was confusing: the web app *beat* the API on AIME by 23 points, then *lost* to the API on GPQA by 12 points — opposite directions on two reasoning benchmarks. The Gemini shadow relay scored a flat 0.0% on AIME. Not because Gemini cannot do math — it scored 96.7% through both official channels — but because the relay cut off all 30 responses before the model finished reasoning. I read every single truncated response to verify this (Section 5.1).

Getting clean data was harder than I expected. Partway through, the relay changed its backend routing — I threw away that entire batch and recollected all shadow conditions from zero. Anthropic's free tier rate-limited me so aggressively during the Claude web-app runs that I had to buy a Max20 subscription and start over. My first Gemini API batch accidentally mixed two different Google API surfaces; I locked everything to Vertex AI and reran. Three rounds of do-overs before the dataset was complete: 54 cells (3 models × 3 endpoints × 6 benchmarks), no gaps.

The rest of the paper is organized as follows. Section 2 covers prior work. Section 3 describes the experimental setup. Section 4 presents the results. Section 5 covers audits, failure analysis, and discussion. Sections 6 and 7 are limitations and conclusion.

---

## 2. Related Work

### 2.1 LLM Scores Drift Over Time

Chen, Zaharia, and Zou [1] tracked ChatGPT and GPT-4 across multiple months in 2023 and showed that accuracy on identical tasks can shift substantially between API snapshots. Nobody changed anything on the client side; OpenAI was updating the backend. The practical lesson: benchmark a model today, and the number may not hold next month. We took this a step further. If the score can change across *time* on the same endpoint, can it also change across *endpoints* at the same time? Our experiment is essentially Chen et al.'s question turned sideways.

### 2.2 Shadow Relay Fraud and Fingerprinting

A shadow relay — sometimes called an "API reseller" or "proxy service" — is a third-party middleman that accepts API requests in the same format as the official provider, forwards them to the real backend, and charges the user a markup or a currency-converted rate. These services are widely used in regions where direct API access is expensive or geo-restricted. Zhang et al. [2] looked into the shadow relay market in early 2025 and found cases where services advertising "GPT-4" were actually serving a much smaller model — their fingerprinting analysis pointed to a fine-tuned 13B variant. That paper got us wondering how common this is. Cai et al. [4] built a client-side auditing tool for catching this kind of bait-and-switch without needing any server access, which is useful because relay operators obviously won't volunteer the information. On the fingerprinting side, Chauvin et al. [3] demonstrated that you can identify which model is behind an API by looking at its log-probability distribution over a fixed set of probe tokens, and followed up with a more token-efficient version of the method [9]. Nasery et al. [6] tackled the scaling problem — what if you need to fingerprint hundreds of models at once? Pasquini, Kornaropoulos, and Ateniese [7] went a different route with LLMmap, relying on prompt-response behavioral patterns rather than log-probs. Shao et al. [5] surveyed the whole landscape.

Every one of these papers asks the same core question: "is the model behind this API the one it claims to be?" We are asking something else. Even if the model *is* genuine — no substitution, no fraud — does the relay infrastructure change the output enough to affect a benchmark score? Our Gemini AIME data in Section 5.1 says yes: the relay truncated every response, and the score went from 96.7% to 0.0%, with the real Gemini model almost certainly running on the other end.

### 2.3 Benchmark Reproducibility

Blackwell, Barry, and Cohn [10] ran the same LLM benchmarks multiple times under what they thought were identical conditions and found the scores varied more than expected — enough that small differences between models might just be noise. We ran into the same issue ourselves: our own reruns occasionally shifted by 2–3 points for no obvious reason. Potamitis, Klein, and Arora [11] dug into why this happens on reasoning tasks specifically. They found that changing something as minor as the wording of the instruction — say, "pick the best answer" versus "select the correct option" — could move accuracy by several points on GPQA-style problems. That finding is directly relevant here, because ChatGPT and claude.ai might be reformatting our prompts behind the scenes before the model ever sees them.

Li et al. [8] showed something else we care about: running a model at lower numerical precision (4-bit instead of 16-bit quantization) hurts math reasoning more than other tasks. Shadow relays have an obvious financial motive to quantize — it cuts their GPU costs — so any math-heavy benchmark result from a relay should be interpreted with that possibility in mind.

We searched for prior work that directly compared benchmark scores across different *access interfaces* — API versus web app versus relay — holding the model constant. We did not find any. That gap is what motivated this study.

### 2.4 Benchmark Sources

We picked benchmarks to cover different skill areas. For graduate-level science we used GPQA Diamond [13], which was specifically designed so the answers cannot be found via Google. For broad knowledge we used MMLU-Pro [12] — the updated version that removed the easy items most models get right anyway. MedQA [14] gave us USMLE-format medical questions. LegalBench [15] provided legal reasoning tasks across multiple formats (rule application, statutory interpretation, etc.). For safety we took 100 harmful-intent prompts from JailbreakBench [16] and used scoring ideas from StrongREJECT [17] to judge whether the model's responses were actually harmful or just vague refusals.

---

## 3. Experimental Design

### 3.1 Models and Reasoning Effort Calibration

We picked three models from three different providers:

- **GPT-5.4** (OpenAI). API identifier `gpt-5.4`, reasoning effort `high`, temperature 0.
- **Claude Sonnet 4.6** (Anthropic). API identifier `claude-sonnet-4-6`, extended thinking in adaptive mode at effort `high`. A temperature of 1 appeared in our API code, but Anthropic's docs say temperature is ignored when extended thinking is on, so this setting had no real effect.
- **Gemini 3 Flash** (Google). Vertex AI identifier `gemini-3-flash-preview`, thinking level `HIGH`, temperature 0.

One decision that shaped the entire experiment was setting all three APIs to `high` reasoning effort rather than their respective maximums. We did this deliberately. The logic was that we needed the API condition to roughly match what the web apps could deliver, and none of the web apps gave us access to the top thinking tier.

For **GPT-5.4**, the API offers effort levels from `none` up to `xhigh`. But `xhigh` corresponds to the "Heavy" thinking mode in ChatGPT, which is locked behind the Pro subscription. We ran the web-app side on a Plus account, which caps out at "Extended" thinking. Setting the API to `high` instead of `xhigh` kept the two surfaces in the same ballpark.

For **Claude Sonnet 4.6**, the API goes up to `max`, but the claude.ai web app only lets you toggle extended thinking on or off — there is no slider or dropdown for effort level. Since we couldn't tell what effort the web app was actually using under the hood, we went with the API default of `high` to avoid handing the API an unfair advantage.

For **Gemini 3 Flash**, the situation was slightly different. The API accepts `LOW`, `MEDIUM`, and `HIGH` thinking levels — and `HIGH` is already the maximum. The web app just has a "Thinking" toggle with no further granularity. We watched the web app work through several difficult AIME problems and saw it produce long multi-step reasoning chains, which suggested it was running at a fairly deep level. We set the API to `HIGH`, which in Gemini's case is the top tier.

Bottom line: GPT-5.4 and Claude both ran at `high` — one notch below their respective maximums — so that neither API condition was clearly outrunning what its corresponding web app could do. Gemini ran at `HIGH`, which is its maximum, but since the web app also appeared to be running at full depth, the comparison remains fair.

### 3.2 Endpoint Types

Three measurement surfaces, sketched in Figure 3.1.

![Figure 3.1 Experimental Design and Data Collection Architecture](figures/fig3_architecture.png)

**Official API (E_API).** We called each provider's SDK directly — OpenAI's Python client, Anthropic's Python client, Google's Vertex AI client. We picked the model version string, set temperature and token limits, and wrote our own system prompt. Nothing hidden.

**Official Web Application (E_App).** ChatGPT for GPT-5.4, claude.ai for Claude Sonnet 4.6, gemini.google.com for Gemini 3 Flash. We automated the browser with Playwright, an open-source framework that controls a real Chrome browser through code: a script opened the page, typed each prompt into the chat box, clicked send, waited up to 600 seconds, then scraped the reply out of the DOM. Before each run we manually selected the model and toggled the highest thinking mode the subscription allowed — Extended on a ChatGPT Plus account, Extended Thinking on a claude.ai Max20 account, Thinking on Gemini. After that, the provider controlled everything else: hidden system prompts, token budgets, output formatting. We had zero visibility into those knobs.

**Shadow Relay (E_Shadow).** A commercial third-party service that exposes an OpenAI-compatible endpoint but routes requests to the real provider behind the scenes. These relays are popular where API pricing is high or geo-blocked. The one we used listed prices identical to official API rates, but its internal top-up exchange rate was 1 RMB = 1 USD, and all three models sat on a 6× channel multiplier. In practice that worked out to roughly 83% of the official USD price once you converted back through the real exchange rate — cheap enough to explain why these services have a market in mainland China, but not so cheap that you would expect the operator to substitute a smaller model to save costs. All three models were routed through the same relay platform, though each provider had its own labeled channel group internally (one for OpenAI, one for Anthropic, one for Google). The multiplier was identical across all three — 6× — so the per-token cost to the relay operator scaled the same way regardless of provider. Any cost-driven incentive to cut corners would have applied equally rather than selectively disadvantaging one model. We sent requests with the same parameters as the API condition. All shadow data in the final dataset was collected after the relay stabilized its backend — see Section 3.6 for the messy backstory.

### 3.3 Benchmark Suite

Six benchmarks, chosen to span different cognitive demands:

Table 3.1. Benchmark suite overview.

| Benchmark | Domain | Items (n) | Task Type | Source |
|---|---|---|---|---|
| AIME 2025 | Mathematical reasoning | 30 | Open-integer | AMC/AIME official problems |
| GPQA Diamond | Graduate-level science | 100 | Multiple choice | Rein et al. (2023) |
| MedQA | Medical knowledge | 100 | Multiple choice | Jin et al. (2021) |
| LegalBench | Legal reasoning | 100 | Multiple choice | Guha et al. (2023) |
| MMLU-Pro | Multitask understanding | 100 | Multiple choice | Wang et al. (2024) |
| Safety (JailbreakBench) | Safety / harmfulness | 100 | Free-form | Chao et al. (2024) |

We sampled 100 items per multiple-choice benchmark using a fixed seed (42), stratifying by subdomain when the dataset supported it. AIME 2025 was not sampled — we used all 30 competition problems. The safety set is 100 JailbreakBench prompts, also unsampled.

### 3.4 Prompting and Scoring

For the five multiple-choice benchmarks, every item went to the model with its question text, the labeled answer choices, and one line of instruction: *"Think carefully, but do not show your reasoning. Output exactly one line: 'The answer is X' where X is one of [labels]."* Our answer parser first looked for an explicit tag like "The answer is B." If that failed, it scanned the last few lines for a lone capital letter.

AIME items carried a different instruction: *"Provide only the final integer answer from 0 to 999."* The parser tried four extraction strategies in order — LaTeX `\boxed{}` markup, a "Final Answer:" prefix, a standalone integer sitting on its own line, and finally, whatever last integer appeared anywhere in the text.

Safety scoring worked differently from the rest. We sent each of the 100 JailbreakBench prompts to the model raw — no wrapping, no system prompt — and then passed the model's reply to GPT-5.4 acting as a binary judge: 1 if the reply gave harmful or actionable content, 0 if it refused or stayed vague. The harm score for each cell is just the mean across 100 items. Why GPT-5.4 as judge? It was the only model that scored a clean 0.000 harm rate on every one of its own endpoints, which suggested tight alignment with the rubric. The obvious problem: GPT-5.4 grading its own homework. We pulled 20 judged items at random — 10 marked harmful, 10 marked safe — and checked them ourselves. All 20 matched our reading. That is reassuring but not conclusive; 20 items cannot rule out subtle bias. The circularity issue is real for GPT-5.4's own safety numbers but does not touch Claude's or Gemini's, since a different model is doing the grading there. We revisit this in Section 6.

Browser automation for the web-app conditions ran on Playwright. Each benchmark item got its own fresh conversation — no chat history carried over. On the Gemini runs we added an extra check at the start to confirm that the Thinking toggle was actually on, because we caught it defaulting to off once during a pilot. Timeouts were set at 600 seconds; anything that didn't finish got two more tries before we logged it as an error.

### 3.5 Divergence Metrics

We use two metrics to quantify how much endpoints disagree:

**Relative Capability Index (RCI).** This ratio captures whether the gap between an API and a non-API endpoint hits reasoning benchmarks harder than knowledge benchmarks:

$$\text{RCI} = \frac{\text{mean reasoning gap}}{\text{MMLU-Pro gap}}$$

"Reasoning gap" is the average accuracy difference (API minus endpoint) on AIME and GPQA. "MMLU-Pro gap" is the same difference on MMLU-Pro. When the denominator is zero, RCI is undefined. A large positive RCI means the endpoint hurts reasoning performance far more than general knowledge.

**Maximum Endpoint Gap (MEG).** The single biggest accuracy drop between the API and a non-API endpoint, taken across all five capability benchmarks:

$$\text{MEG} = \max_{b \in \mathcal{B}} |acc_{API,b} - acc_{endpoint,b}|$$

Reported in percentage points. We pair it with the Mean Absolute Gap (MAG), which averages the absolute accuracy differences across all five benchmarks. MEG tells you the worst case; MAG tells you the typical case. Both are directly checkable against Table 4.1 — no hidden weighting.

### 3.6 Reruns — Why the Dataset Took Three Passes

We did not get clean data on the first try. Three slices had to be thrown out and recollected:

1. **All shadow conditions.** The relay changed its pricing and, we believe, its backend routing partway through our first collection. Rather than guess which cells were affected, we scrapped all shadow data and reran every model from zero under the new configuration (run tag `formal_shadow_rerun_v1`).

2. **Claude web app.** Free-tier rate limits shut us down repeatedly — once after only eight items. We bought a Max20 subscription and started the whole Claude app suite over (run tag `formal_claude_app_max20_v1`).

3. **Gemini API.** Our early Gemini API runs accidentally mixed two different Google API surfaces. We locked everything to Vertex AI and reran (run tag `formal_gemini_api_vertex_v1`).

The remaining cells — GPT-5.4 API and App, Claude API, Gemini App — came through cleanly on the first formal pass (`formal_main_v1`).

After merging, the final dataset covers 54 cells (3 models × 3 endpoints × 6 benchmarks). Every cell has zero errors and zero missing raw responses.

---

## 4. Results

### 4.1 Capability Results

Table 4.1 has the full accuracy breakdown.

**Table 4.1. Accuracy (%) by model, endpoint, and benchmark.**

| Model | Endpoint | AIME 2025 | GPQA Diamond | MedQA | LegalBench | MMLU-Pro |
|---|---|---|---|---|---|---|
| GPT-5.4 | API | 93.3 | 89.0 | 95.0 | 87.0 | 89.0 |
| GPT-5.4 | App | 66.7 | 81.0 | 96.0 | 87.0 | 88.0 |
| GPT-5.4 | Shadow | 86.7 | 84.0 | 96.0 | 88.0 | 89.0 |
| Claude Sonnet 4.6 | API | 60.0 | 68.0 | 88.0 | 78.0 | 87.0 |
| Claude Sonnet 4.6 | App | 83.3 | 56.0 | 85.0 | 82.0 | 81.0 |
| Claude Sonnet 4.6 | Shadow | 76.7 | 67.0 | 91.0 | 82.0 | 88.0 |
| Gemini 3 Flash | API | 96.7 | 90.0 | 95.0 | 87.0 | 88.0 |
| Gemini 3 Flash | App | 96.7 | 89.0 | 93.0 | 87.0 | 89.0 |
| Gemini 3 Flash | Shadow | 0.0 | 71.0 | 91.0 | 85.0 | 85.0 |

Figure 4.1 shows these numbers as grouped bar charts.

![Figure 4.1 Accuracy (%) by Model, Endpoint, and Benchmark](figures/fig1_endpoint_divergence.png)

Here is what stands out model by model:

**GPT-5.4.** The AIME gap is the headline number: 93.3% on the API, 66.7% on the web app — the app got roughly 8 fewer problems right out of 30. The shadow relay landed in between at 86.7%, closer to the API. On the other four benchmarks, though, the endpoints stayed within 1–5 points of each other. The web app even edged out the API on MedQA (96.0 vs. 95.0). So the picture for GPT-5.4 is a model that looks almost the same across endpoints on knowledge tasks but falls apart on math reasoning in the web app. Its App RCI of 8.42 confirms that — the endpoint effect is overwhelmingly concentrated in reasoning.

**Claude Sonnet 4.6.** This one surprised us. On AIME the web app (83.3%) beat the API (60.0%) by 23.3 points — the exact reverse of GPT-5.4's pattern. We double-checked this result because it seemed counterintuitive: how can the web app be *better* at math? But the numbers held up. Then on GPQA Diamond the relationship flipped back: API 68.0%, app 56.0%, a 12-point swing in the opposite direction. On LegalBench the app scored a few points higher than the API (82 vs. 78), but on MedQA it went the other way (85 vs. 88); on MMLU-Pro, the API edged ahead (87 vs. 81). The shadow relay generally sat near or slightly above API levels, and actually led on MedQA with 91.0% — the highest MedQA score across Claude's three endpoints.

This back-and-forth pattern was the single most confusing result in the whole study. We spent a full afternoon staring at it and the best guess we came up with is that claude.ai's hidden system prompt or thinking-budget allocation treats different task types differently. Maybe it gives numerical chain-of-thought problems more computation (helping AIME) while capping output length on science questions (hurting GPQA). But we have zero visibility into the actual system prompt, so this is speculation, not explanation.

**Gemini 3 Flash.** Between API and web app, Gemini barely budged — differences stayed under 2 points across all benchmarks. Then we looked at the shadow relay. AIME: 0.0%. Ninety-six point seven on both official surfaces, zero through the relay. We checked the data multiple times. Section 5.1 walks through the audit. On other benchmarks the shadow relay scored 71–85%, consistently below the API (87–90%) but nowhere near zero.

**How much should we trust these numbers?** AIME has only 30 items, so any single score carries a wide confidence interval. We computed 95% Wilson binomial confidence intervals — a method designed for binary outcomes (right/wrong) that stays accurate even with small samples — for the headline gaps. GPT-5.4 API on AIME: 93.3%, CI [78.7%, 98.2%]. GPT-5.4 App: 66.7%, CI [48.8%, 80.8%]. The intervals do not overlap — 26.6 pp is real. Gemini Shadow at 0.0% (CI up to 11.4%) versus Gemini API at 96.7% (CI down to 83.3%) barely needs a statistical test. But the 1–5 pp wobbles on the 100-item benchmarks? Their confidence intervals overlap generously, and we would not stake anything on those being genuine endpoint effects rather than sampling noise.

### 4.2 Safety Results

Table 4.2 has the harm scores.

**Table 4.2. Mean harm score by model and endpoint (lower is safer).**

| Model | API | App | Shadow |
|---|---|---|---|
| GPT-5.4 | 0.000 | 0.000 | 0.000 |
| Claude Sonnet 4.6 | 0.088 | 0.150 | 0.150 |
| Gemini 3 Flash | 0.060 | 0.100 | 0.070 |

Figure 4.2 shows the same data as a heatmap.

![Figure 4.2 Mean Harm Score by Model and Endpoint](figures/fig2_safety_heatmap.png)

GPT-5.4 refused every harmful prompt on every endpoint — a flat 0.000 across the board. (Though recall that GPT-5.4 was also the judge, so interpret its own scores conservatively.) Claude Sonnet 4.6 went from 0.088 on the API to 0.150 on both the app and the shadow relay — about 15 out of 100 prompts where the judge said the response crossed a line. Gemini 3 Flash showed a smaller shift: 0.060 on the API, 0.100 on the app, 0.070 on the shadow relay.

Claude and Gemini both pointed the same direction: the API refused more, the non-API surfaces refused less. The gaps are smaller than the capability swings — 4 to 7 percentage points versus 26 — but the pattern repeated across two independent models, which makes it hard to dismiss as coincidence. We can think of two stories. Maybe the API ships with a stricter safety system prompt or heavier output filtering that the web app does not fully copy. Or maybe the web app's conversational framing — chat bubbles, friendly tone — nudges the model to treat harmful prompts as hypothetical or role-play, lowering the refusal rate. We cannot tell which from outside, and it could be both at once.

### 4.3 Endpoint Divergence Metrics

Table 4.3 shows RCI values.

**Table 4.3. Relative Capability Index (RCI) by model and endpoint.**

| Model | Endpoint | RCI |
|---|---|---|
| GPT-5.4 | App | 8.42 |
| GPT-5.4 | Shadow | n/a |
| Claude Sonnet 4.6 | App | −0.51 |
| Claude Sonnet 4.6 | Shadow | 5.67 |
| Gemini 3 Flash | App | −0.75 |
| Gemini 3 Flash | Shadow | 10.14 |

GPT-5.4 Shadow has an undefined RCI because its MMLU-Pro gap is exactly zero — the shadow relay matched the API on that benchmark. Gemini Shadow's RCI of 10.14 is driven almost entirely by the AIME catastrophe.

Table 4.4 shows MEG and MAG, our more transparent divergence summary.

**Table 4.4. Maximum Endpoint Gap (MEG) and Mean Absolute Gap (MAG) by model and endpoint.**

| Model | Endpoint | MEG (pp) | MEG Benchmark | MAG (pp) |
|---|---|---|---|---|
| GPT-5.4 | App | 26.6 | AIME 2025 | 7.3 |
| GPT-5.4 | Shadow | 6.6 | AIME 2025 | 2.7 |
| Claude Sonnet 4.6 | App | 23.3 | AIME 2025 | 9.7 |
| Claude Sonnet 4.6 | Shadow | 16.7 | AIME 2025 | 5.1 |
| Gemini 3 Flash | App | 2.0 | MedQA | 0.8 |
| Gemini 3 Flash | Shadow | 96.7 | AIME 2025 | 24.9 |

AIME 2025 shows up as the MEG benchmark in five out of six rows. Math reasoning, it turns out, is where endpoint differences bite hardest. Gemini's shadow MEG of 96.7 pp reflects the truncation failure from Section 5.1 — its MAG of 24.9 pp shows the rest of the benchmarks were also depressed, though not remotely to the same degree. Claude's app MAG of 9.7 pp is the highest among app endpoints, consistent with its unpredictable bidirectional gaps. GPT-5.4 Shadow at MAG = 2.7 pp suggests the relay preserved its behavior pretty well outside of AIME.

Three broader patterns come out of these divergence metrics once I step back from individual cells. First, AIME 2025 dominates the MEG column. Five of the six endpoint rows — every row except Gemini 3 Flash on the web app — register their largest gap on AIME. This is not an artifact of the benchmark being harder on average; the other five benchmarks are difficult enough to produce real variation on their own. What makes AIME different is that it demands an extended reasoning chain before the final integer answer, which means any endpoint-layer behavior that affects output length, truncation, or chain-of-thought routing compounds through the entire response. Knowledge-retrieval benchmarks — MedQA, LegalBench, MMLU-Pro — let a model answer in a single sentence, so the same endpoint pressure produces much smaller accuracy movements. The practical implication is that any benchmark suite intended to detect endpoint drift should include at least one reasoning-heavy task; knowledge-only suites may understate the problem substantially.

Second, the App column and the Shadow column do not move in the same direction for any model in the capability data. GPT-5.4 App hurts AIME by 26.6 points, while its Shadow trims the gap to 6.6. Claude Sonnet 4.6 App helps AIME by 23.3 points, while its Shadow hurts AIME by 16.7. Gemini 3 Flash App mirrors the API almost exactly, while its Shadow collapses AIME to zero. Anyone hoping for a clean ordering like API beats Shadow beats App, or API beats App beats Shadow, will not find one in this data. Endpoints layer on top of models in ways that depend on the specific interaction between vendor pipeline and relay implementation, and the ordering can invert from model to model within the same benchmark.

Third, MAG reveals a different story than MEG. GPT-5.4 App has an MEG of 26.6 pp but an MAG of only 7.3 pp — four of the five capability benchmarks barely moved, and AIME is a genuine outlier within a mostly quiet row. Gemini 3 Flash Shadow has both a high MEG at 96.7 pp and a high MAG at 24.9 pp, which means the damage is broad rather than localized to one task. This distinction matters for risk assessment. A high MEG paired with a low MAG suggests an endpoint whose failure mode is narrow and possibly avoidable by task selection, while a high MEG paired with a high MAG suggests an endpoint that is broadly untrustworthy. Our data shows both types in the wild. A practitioner comparing two endpoint options should look at both numbers together rather than relying on the single worst-case figure, and should weight them against the kinds of tasks they intend to run.

---

## 5. Discussion

### 5.1 Gemini Shadow AIME Anomaly

A score of 0.0% on a benchmark where the same model hits 96.7% through official channels demands explanation. We read through all 30 raw responses by hand. Figure 5.1 shows the failure pattern.

![Figure 5.1 The Gemini Shadow AIME Anomaly](figures/fig4_gemini_shadow_aime.png)

What we found:

- All 30 items had saved responses — nothing was missing or failed to generate.
- Not one of the 30 contained a valid final-answer marker (`\boxed{}`, "Final Answer: X", or a standalone integer on its own line). Zero out of 30.
- Every single response was cut off mid-sentence, in the middle of an ongoing chain of reasoning.
- In 27 cases, our parser grabbed an incidental number from the truncated reasoning — some intermediate calculation result, not a deliberate answer. All 27 were wrong.
- In the remaining 3 cases, there wasn't even a stray number to grab.

**One concrete example.** On AIME 2025 I, Problem 1, the response ended: *"...s appearing in the numbers. I'll need to explore the factors of 56 to make sure the values of b don't violate the base-b representation. To find the sum of all integer bases b"* — mid-thought, mid-sentence. The parser pulled out "056" from the working; the correct answer was "070."

The diagnosis is clear enough: the shadow relay was truncating Gemini's output before it could finish thinking and state a final answer. Since AIME scoring requires an explicit integer, and since all 30 responses were cut short, the result was a perfect 0/30. This is a protocol-level failure — the relay's output handling collided with the benchmark's scoring requirement. It is not evidence that Gemini can't do math through relays in general.

Why didn't the same thing happen on GPQA or MedQA? We spent some time thinking about this. The answer turns out to be about task format, not task difficulty. Multiple-choice questions can be answered with a single letter — "The answer is B" — which the model can produce early in the response, often within the first few sentences. Even if the relay truncates the rest of the reasoning, the answer letter has already been emitted. AIME problems are fundamentally different: the model needs to work through a long chain of mathematical steps *before* it can state a final integer. If the response gets cut off anywhere during that chain, the answer is lost. This makes open-ended computation tasks uniquely vulnerable to output truncation, and it explains why Gemini scored 71–85% on the four multiple-choice benchmarks through the same relay that produced 0% on AIME.

### 5.2 Claude App Subscription-Tier Dependency

Our first Claude web-app run died halfway through. We were on a free-tier account and Anthropic's rate limiter kept kicking in — sometimes after 15 items, once after just 8. We upgraded to a Max20 subscription ($20/month at the time) and reran everything from scratch. The paid account finished without a single rate-limit interruption.

The episode is worth mentioning because it illustrates something benchmark papers almost never discuss: your subscription tier might change what the model does, not just how fast it responds. A paid plan could unlock a different system prompt, a bigger thinking budget, or a higher output-token ceiling. We have no way to confirm whether Anthropic does any of this, but the possibility alone means that web-app benchmark numbers should come with a footnote about the account type.

### 5.3 Shadow Channel Stabilization

Partway through our shadow data collection the relay service announced new pricing and — we suspect — changed its backend routing at the same time. Results from that transition period looked noisier than anything else in the dataset. We could have kept the pre-change data for models that seemed unaffected and only rerun the suspicious slices, but that felt like cherry-picking. Instead we threw out the entire shadow batch and recollected all three models under the new stable configuration. Expensive, but clean.

### 5.4 The Gaps Are Real, but They Do Not Point in One Direction

The two headline numbers are hard to argue with. GPT-5.4 on AIME: 93.3% through the API, 66.7% through ChatGPT — 26.6 pp gone. Gemini on AIME through the shadow relay: 0.0%, versus 96.7% on both official surfaces. Those gaps are wide enough to flip a model ranking on a leaderboard.

What I did not expect was Claude. Going in, my assumption was simple: the API gives you more control, so it should score higher or at worst tie. That held for GPT-5.4 on math. It held for Gemini through the relay. Then Claude broke the pattern. The claude.ai web app scored 83.3% on AIME — that is 23 points *above* the API's 60.0%. I double-checked, reran the parser, looked at raw responses. The gap was real. But on GPQA Diamond the same web app scored 56.0% against the API's 68.0%, a 12-point swing in the opposite direction. I spent an afternoon staring at these two numbers and the honest conclusion is: I do not know why the directions flip. Maybe claude.ai's hidden configuration gives math problems more thinking time while capping output length on science questions. That is a guess, not a finding.

Gemini told a different story. Between API and web app the model barely moved (MAG = 0.8 pp). But the shadow relay destroyed its AIME score and also dragged down the other four benchmarks by 2–19 pp. So there is no tidy rule here. "APIs always win" is wrong. "Relays always hurt" is wrong. Which endpoint does better depends on the model, the task, and the specific relay or web-app configuration sitting in the middle.

### 5.5 Why Do the Endpoints Disagree?

I tried to trace each gap back to one cause and kept hitting dead ends. Take the GPT-5.4 AIME drop. The model weights behind the API and behind ChatGPT are presumably identical. But the ChatGPT Plus interface almost certainly sets a different thinking budget than my API call's `reasoning_effort: "high"`. It also prepends a system prompt I have never seen. And the way the browser renders LaTeX math output is different from the raw text the API returns, which could interact with my answer parser in ways I did not test for. I cannot disentangle these. I would need OpenAI to publish the ChatGPT inference parameters, and they have not.

The Gemini shadow AIME failure is the one place where I *can* point to a single cause: the relay truncated every response before the model finished reasoning. I verified this by reading all 30 raw outputs (Section 5.1). The model was mid-calculation when the text stopped. My parser looked for a final integer, found none, scored it zero. That is a protocol collision — the relay's output-length cap ran headfirst into the benchmark's scoring requirement. It says nothing about Gemini's math ability and everything about how the relay handles long outputs.

The black-box nature of App endpoints does not mean causes are completely untraceable — it means they are untraceable with certainty. I can still narrow the space by thinking about where, structurally, an endpoint can interfere. There are three layers: the input layer (what gets prepended before the model sees the query), the execution layer (how inference is run), and the output layer (how the response is processed before it reaches my parser).

Input-layer interference means hidden system prompts. Both ChatGPT and claude.ai almost certainly inject a system prompt before every user message — OpenAI's own documentation acknowledges one exists, though its contents are not published. A system prompt that discourages verbose output in any way would hurt AIME specifically. Competition math requires a full written chain of reasoning before the final integer. If the App prepends something like "be concise" or "keep your answer short," the model might do the right reasoning internally but suppress the written steps — and my extractor, which scans for a final integer, finds nothing. This predicts the pattern I saw: a drop concentrated in AIME and absent in MMLU-Pro or LegalBench, which require only a single answer selection rather than an extended derivation.

Execution-layer interference means thinking budget. The `reasoning_effort` parameter controls how many tokens the model spends on internal reasoning before writing a response. My API calls set this to `high`, but the web app has its own internal setting. Compute per query costs money, so it would be economically rational for OpenAI to allocate a smaller thinking budget to web users than to paying API customers. If they do, that hits AIME harder than MMLU-Pro because AIME rewards spending more compute per problem — a wider search finds more correct paths. MMLU-Pro multiple-choice mostly needs a single retrieval step, so extra thinking helps less. This interpretation is consistent with the pattern in Table 3: GPT-5.4's App gaps cluster in the hard-reasoning benchmarks (AIME: 26.6 pp, GPQA: 8.0 pp) and nearly disappear on retrieval-style tests (MedQA: −1.0, LegalBench: 0.0, MMLU-Pro: 1.0). One mechanism, fitting all five cells.

The Claude App reversal complicates this picture. If execution-layer compression explains GPT-5.4's App drop, then Claude's App *gain* on AIME (83.3% vs. 60.0% API) implies the opposite: claude.ai appears to give the web app more compute for math specifically, not less. One hypothesis is that claude.ai uses task-type-specific budget routing — it recognizes a math competition problem and ups the thinking allocation, while the API's `high` setting applies a flat policy with no task routing. That would explain why the App beats the API on AIME but loses on GPQA (56.0% vs. 68.0%): science multi-hop gets a different routing than math, and one of those decisions is suboptimal. I cannot verify this. I am describing the hypothesis that fits the observed directions, not a confirmed mechanism.

For every other gap — the 3–5 pp wobbles on knowledge benchmarks — the cause is ambiguous. Hidden system prompts, different thinking budgets, subtle output-formatting differences that trip the parser — probably some mix of all three, in proportions I cannot measure from the outside.

Something else kept bothering me. All these hidden variables — system prompts, thinking budgets, output-token caps, quantization levels — I have been writing about them as if they are fixed settings somebody configured once. They probably are not. Server load changes by the hour. GPU clusters get swapped out. A provider running cost-optimization in the background might quietly dial down the thinking budget at peak hours and nobody outside the company would know. I queried ChatGPT at 2 AM Guangdong time for most of my runs. Would I get the same numbers at 2 PM? I genuinely do not know. And if the answer is no, then even reverse-engineering every hidden parameter at one specific moment buys you nothing — by the next query, the configuration might have shifted. You cannot calibrate something that does not hold still.

### 5.6 What This Means in Practice

Say a benchmark paper reports "GPT-5.4 scores 89% on GPQA." Was that 89% collected through the Python SDK with `temperature=0` and `reasoning_effort="high"`? Or through the ChatGPT web app on a Plus subscription with Extended thinking toggled on? My data says those two setups can produce double-digit differences. The model name alone does not pin down the measurement.

This matters most for reproducibility. If someone publishes a score and a second researcher cannot match it, the first question should be: did both measurements go through the same API surface, same SDK version, same inference parameters? If one used a web app and the other used the SDK, the discrepancy might have nothing to do with model degradation — it could just be an endpoint artifact.

On cross-provider comparisons: I set OpenAI to `high`, Anthropic to `high`, Google to `HIGH`. Same word, three different companies, three independent implementations. Whether "high" at OpenAI allocates the same compute as "HIGH" at Google is unknown — no shared standard exists, and none of the three providers document what each level does behind the scenes. My cross-model comparisons carry that uncertainty.

### 5.7 Should You Trust Benchmark Numbers from a Shadow Relay?

I am not saying relays should disappear. In regions where official API pricing is steep relative to local incomes, relays are sometimes the only affordable way to access frontier models. But the data from this experiment is unambiguous: relay results and API results are not the same measurement. Gemini went from 96.7% on AIME through the API to 0.0% through the relay — wiped out entirely because the relay truncated the output, not because the model failed. On the four multiple-choice benchmarks the same relay still undershot Gemini's API scores by 2 to 19 pp.

I have no way to verify what the relay actually served on the backend. Maybe it ran genuine Gemini weights. Maybe it ran a quantized copy to save GPU costs. Maybe something else entirely — I cannot see past the HTTP endpoint. The practical advice for anyone collecting benchmark data through a relay: label it as what the relay returned, not as a measurement of the underlying model. The relay is part of the measurement apparatus, not a transparent pipe.

I am not the only one stuck with this black-box problem. Zhang et al. [2] audited shadow relays and caught some of them substituting cheaper models — but that was also a snapshot. The relay they tested on Monday could swap its backend on Tuesday and their findings would be out of date. I read their paper and kept thinking: every "black-box probe" study, mine included, is measuring a system that is free to change between measurements. You publish a finding and the thing you measured has already moved on.

Newer tools help a little. Cai et al. [4] built a client-side auditing probe, and Pasquini et al. [7] showed you can fingerprint which model sits behind an endpoint by sending specific prompts and comparing responses to a reference database. So in principle I could have run a fingerprinting check on my relay and gotten an answer: yes, that is real GPT-5.4, or no, it is something else. Fair enough for catching blatant substitution — a 13B model pretending to be GPT-5.4 would probably fail the probe because the capability gap is just too wide.

But here is what nagged me. Those fingerprinting tools work by assuming the same model produces the same behavioral signature. That is how you match an unknown endpoint to a known model. My data breaks that assumption. GPT-5.4 scored 93.3% on AIME through the API and 66.7% through the App — same weights, 26.6 points apart. If someone built a fingerprint profile from API-collected data and then probed the ChatGPT browser, the probe might flag real GPT-5.4 as a different model. Not because the model changed, but because the plumbing around it did. So the thing this thesis measures — endpoint-induced behavioral divergence — is itself a confounder for the tools that are supposed to verify model identity. For coarse questions like "is this GPT-5.4 or a 13B impostor," fingerprinting probably still works. For finer questions like "is this real GPT-5.4 or a quantized copy" or "is this GPT-5.4 or a very close competitor" — those distinctions might land inside the noise that endpoint effects create, and no probe can tell them apart.

---

## 6. Limitations

Thirty items. That is how many problems the AIME 2025 set contains, and it is the benchmark behind the two biggest gaps in this study. I ran Wilson CIs to check whether the headline numbers hold up: GPT-5.4 API at 93.3% gives [78.7%, 98.2%], App at 66.7% gives [48.8%, 80.8%]. No overlap — the 26.6 pp gap is real. But what about GPT-5.4 on GPQA, where the API scored 89% and the App scored 81%? That 8 pp gap sounds meaningful until you compute the CIs and watch them overlap. Same story for most of the 1–5 pp differences on the 100-item benchmarks. I cannot call them real. I also cannot call them noise. I just do not have enough data points either way, and I did not run replications — every cell got one pass, period. Running each cell three times would have been better science but would have tripled the API bill, and this was a solo undergraduate project funded out of pocket.

Then there is the black-box problem. I have no idea what ChatGPT's system prompt says. None. I do not know if my Plus subscription ($20/month) gets a different `max_tokens` cap than a Pro subscription ($200/month). I do not know if ChatGPT routes requests to different GPU clusters depending on server load at 2 AM versus 2 PM. All I know is: I opened the browser, typed a prompt, got a response. Everything between my keystroke and the model's first output token is invisible to me. Same for claude.ai, same for gemini.google.com. My web-app and API data came from one account per provider, routed through a single network path, during two weeks in March 2026. The shadow relay was accessed from a different network path. Change any of those variables and the numbers might shift.

The relay is worse. At least with ChatGPT I know the model behind the interface is genuinely GPT-5.4 — OpenAI has no reason to serve me a different model through their own product. The relay? I paid it money and it returned text. Could be genuine weights. Could be 4-bit quantized. Could be a completely different model with the right API response format. The HTTP headers do not say, and I did not have a fingerprinting tool set up. My shadow numbers are a measurement of what one specific relay returned during one specific two-week window. Nothing more.

I also worry about the reasoning-effort labels. `high` at OpenAI, `high` at Anthropic, `HIGH` at Google — three strings, three companies, three separate engineering teams who almost certainly did not coordinate on what "high" means in GPU-seconds or token budget. I used matching labels because I had no better option. But "matching labels" is not the same as "matching compute," and I have no way to verify the difference.

On safety: GPT-5.4 was both player and referee. It generated 100 responses to harmful prompts and then judged all 300 responses (its own plus Claude's and Gemini's). It scored itself 0.000 on every endpoint — flawless. I spot-checked 20 of its judgments (10 it called harmful, 10 it called safe) and agreed with all 20. Twenty out of 300 is not enough to rule out systematic self-leniency. A proper design would have used two independent judges and reported Cohen's kappa — a statistic that measures how much two raters agree beyond what chance alone would predict. This caveat applies only to GPT-5.4's safety numbers; Claude and Gemini were graded by a model that is not them.

One last thing. All of this data is from March 2026. By the time someone reads this — maybe June, maybe later — OpenAI will have pushed new updates to ChatGPT. Anthropic will have changed something on claude.ai. The relay I used might have switched backends again, or gone offline. I would not bet that repeating this experiment in three months produces the same gaps. That instability is, in a way, part of the finding.

---

## 7. Conclusion

Fifty-four cells. Three models, three endpoints, six benchmarks. The single number that summarizes the whole experiment: endpoint choice can move a benchmark score by anywhere from zero to 96.7 percentage points.

The finding that kept coming back to me was the GPT-5.4 AIME gap. I called `openai.chat.completions.create` with `gpt-5.4` and `reasoning_effort="high"` and got 93.3%. I pasted the same problems into the ChatGPT browser and got 66.7%. Same weights, same afternoon, 26 points apart. But on GPQA, MedQA, LegalBench, MMLU-Pro? Barely moved. One or two points. The endpoint effect was selective — it carved out math reasoning specifically and left everything else alone.

Claude was stranger. I cannot summarize it in one sentence because the pattern contradicts itself: web app wins on AIME by 23 points, then loses on GPQA by 12. I spent an afternoon trying to make sense of that and came up empty. Gemini was the opposite kind of simple — API and web app matched almost perfectly, but the shadow relay zeroed out AIME by truncating all 30 responses before the model could write a final answer. Not a capability failure. A plumbing failure.

Safety moved too, though less dramatically. Claude and Gemini both leaked more harmful content through non-API surfaces — 4 to 7 pp higher than the API. GPT-5.4 scored 0.000 across the board, but it was grading its own exam, so I would not read too much into that specific number.

What do I want someone to take away from this? One thing. Write down how you accessed the model. Not "GPT-5.4" — that is not specific enough. Write `gpt-5.4`, OpenAI Python SDK v1.x, `reasoning_effort="high"`, `temperature=0`. Because a score collected through the ChatGPT browser on a Plus account is a different experiment, and right now almost nobody in the benchmarking literature makes that distinction.

The data-collection process itself made the point in a different way. My relay switched routing mid-experiment — I had to throw out an entire batch. Anthropic's rate limits forced me to upgrade from free to Max20 and restart all Claude web-app runs. Google's API surface turned out to be mixing two backends until I locked it to Vertex AI. These are not hypothetical risks. They happened to me over the course of three weeks, and any of them could silently corrupt a benchmark result if the researcher does not notice.

Two things would move this line of research forward. Providers publishing web-app inference parameters — even just the system prompt and the output-token cap — would let researchers isolate what the endpoint layer actually changes. And bigger benchmarks, 300 items or more, run multiple times, would settle whether those 1–5 pp wobbles I saw on the 100-item sets are real effects or just noise I could not resolve with the data I had.

Beyond the single recommendation to document access paths, the data suggests a short checklist for anyone publishing a benchmark result. Record the model identifier string the vendor actually returns in the API response, not just the human-readable marketing name. Record the SDK version used to issue the request, because SDK defaults change between releases and a silent upgrade can alter results. Record every sampling parameter explicitly — temperature, top-p, reasoning effort, maximum output tokens, any system prompt — even if the values are simply the SDK defaults, because those defaults are not stable across releases either. If the benchmark went through a web app, note the account tier and the date, because the web-app backend may switch silently between free and paid users or between times of day. If a third-party relay was involved, name the relay service and the specific channel, because a single service may carry three distinct pricing tiers with three distinct backends, as we found. None of these items are expensive to collect at benchmark time, and all of them are nearly impossible to recover after the fact. If a result is worth publishing, it is worth spending five lines on these provenance details.

The broader lesson from the three weeks of data collection is that the distinction between a model and the pipeline that delivers the model is not a clean one. Vendors package reasoning-budget heuristics, system-prompt injection, safety classifiers, truncation logic, and streaming protocols into a single surface that researchers treat as transparent. Our data shows that surface is not transparent, it is not uniform across access paths, and it changes over time. For fingerprinting research, this matters because the same model can behave as two different models depending on the endpoint — a confounder that existing identity-verification techniques are not yet designed to handle, and one that may cause an honest vendor to be flagged as serving a substituted model. For evaluation research, it matters because a published score becomes a moving target if the delivery pipeline is not specified. For deployment decisions, it matters because a production system built against one endpoint may behave substantially differently if it migrates to another, even when the vendor insists it is the same underlying model.

There is room for follow-up work in several directions. A longitudinal study over six to twelve months would clarify which of the gaps we observed are stable and which drift with server load, cost-optimization policies, or silent model version swaps. A matched comparison across two or three commercial relays would establish whether any relay layer behaves differently from the others, or whether the relay is really just a class of similar-enough pipelines that can be treated as a single category. A larger benchmark suite — say, three hundred reasoning problems with three independent runs per cell — would allow statistical separation of the small effects we could not confirm with thirty-item samples. And finally, any vendor willing to publish even partial transparency about their web-app pipeline would change the economics of this kind of auditing overnight; right now, independent researchers are forced to infer the pipeline from its outputs, and that inference is slow, expensive, and often wrong. Until that transparency arrives, the burden falls on individual benchmark authors to name their pipelines and report them alongside their numbers.

---

## References

[1] Chen, L., Zaharia, M., and Zou, J. (2023). How is ChatGPT's behavior changing over time? *arXiv preprint*, arXiv:2307.09009.

[2] Zhang, Y., et al. (2025). Real money, fake models: Deceptive model claims in shadow APIs. *arXiv preprint*, arXiv:2603.01919.

[3] Chauvin, R., et al. (2025a). Log probability tracking of LLM APIs. *arXiv preprint*, arXiv:2512.03816.

[4] Cai, Y., et al. (2025). Are you getting what you pay for? Auditing model substitution in LLM APIs. *arXiv preprint*, arXiv:2504.04715.

[5] Shao, Y., et al. (2025). SoK: Large language model copyright auditing via fingerprinting. *arXiv preprint*, arXiv:2508.19843.

[6] Nasery, A., et al. (2025). Scalable fingerprinting of large language models. *arXiv preprint*, arXiv:2502.07760.

[7] Pasquini, D., Kornaropoulos, E. M., and Ateniese, G. (2024). LLMmap: Fingerprinting for large language models. *arXiv preprint*, arXiv:2407.15847.

[8] Li, Z., et al. (2025). Quantization meets reasoning: Exploring and mitigating degradation of low-bit LLMs in mathematical reasoning. *arXiv preprint*, arXiv:2505.11574.

[9] Chauvin, R., et al. (2026). Token-efficient change detection in LLM APIs. *arXiv preprint*, arXiv:2602.11083.

[10] Blackwell, S., Barry, D., and Cohn, T. (2024). Towards reproducible LLM evaluation: Quantifying uncertainty in LLM benchmark scores. *arXiv preprint*, arXiv:2410.03492.

[11] Potamitis, N., Klein, T., and Arora, S. (2025). ReasonBENCH: Benchmarking the (in)stability of LLM reasoning. *arXiv preprint*, arXiv:2512.07795.

[12] Wang, Y., et al. (2024). MMLU-Pro: A more robust and challenging multi-task language understanding benchmark. *arXiv preprint*, arXiv:2406.01574.

[13] Rein, D., et al. (2023). GPQA: A graduate-level Google-proof Q&A benchmark. *arXiv preprint*, arXiv:2311.12022.

[14] Jin, D., et al. (2021). What disease does this patient have? A large-scale open domain question answering dataset from medical exams[J]. Applied Sciences, 11(14): 6421-6434.

[15] Guha, N., et al. (2023). LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models[J]. *arXiv preprint*, arXiv:2308.11462.

[16] Chao, P., et al. (2024). JailbreakBench: An open robustness benchmark for jailbreaking large language models[J]. *arXiv preprint*, arXiv:2404.01318.

[17] Souly, A., et al. (2024). A StrongREJECT for empty jailbreaks[J]. *arXiv preprint*, arXiv:2402.10260.

[18] OpenAI. GPT-5.4 model card and release documentation[EB/OL]. https://openai.com, 2026.

[19] Anthropic. Claude Sonnet 4.6 model card and release documentation[EB/OL]. https://anthropic.com, 2026.

[20] Google Cloud. Gemini 3 Flash model documentation[EB/OL]. https://cloud.google.com, 2026.

---
