"""Generate all figures for the Hidden Fork v4 paper."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# ── Shared styling ──
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

COLORS_API    = "#2166AC"
COLORS_APP    = "#D6604D"
COLORS_SHADOW = "#4DAF4A"

# =====================================================================
# Figure 1: Grouped bar chart — accuracy by model × endpoint × benchmark
# =====================================================================
print("Figure 1: Endpoint divergence bar chart ...")

benchmarks = ["AIME 2025", "GPQA\nDiamond", "MedQA", "LegalBench", "MMLU-Pro"]
models = ["GPT-5.4", "Claude Sonnet 4.6", "Gemini 3 Flash"]

data = {
    "GPT-5.4": {
        "API":    [93.3, 89.0, 95.0, 87.0, 89.0],
        "App":    [66.7, 81.0, 96.0, 87.0, 88.0],
        "Shadow": [86.7, 84.0, 96.0, 88.0, 89.0],
    },
    "Claude Sonnet 4.6": {
        "API":    [60.0, 68.0, 88.0, 78.0, 87.0],
        "App":    [83.3, 56.0, 85.0, 82.0, 81.0],
        "Shadow": [76.7, 67.0, 91.0, 82.0, 88.0],
    },
    "Gemini 3 Flash": {
        "API":    [96.7, 90.0, 95.0, 87.0, 88.0],
        "App":    [96.7, 89.0, 93.0, 87.0, 89.0],
        "Shadow": [ 0.0, 71.0, 91.0, 85.0, 85.0],
    },
}

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=True)
bar_width = 0.25
x = np.arange(len(benchmarks))

for ax_idx, model in enumerate(models):
    ax = axes[ax_idx]
    d = data[model]
    bars_api = ax.bar(x - bar_width, d["API"], bar_width, label="API",
                      color=COLORS_API, edgecolor="white", linewidth=0.5)
    bars_app = ax.bar(x, d["App"], bar_width, label="App",
                      color=COLORS_APP, edgecolor="white", linewidth=0.5)
    bars_shd = ax.bar(x + bar_width, d["Shadow"], bar_width, label="Shadow",
                      color=COLORS_SHADOW, edgecolor="white", linewidth=0.5)

    # Value labels on bars
    for bars in [bars_api, bars_app, bars_shd]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 1.0,
                        f"{h:.0f}" if h == int(h) else f"{h:.1f}",
                        ha="center", va="bottom", fontsize=7)

    ax.set_title(model, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks)
    ax.set_ylim(0, 109)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ax_idx == 0:
        ax.set_ylabel("Accuracy (%)")
    ax.axhline(y=0, color="grey", linewidth=0.5)

    # Highlight Gemini Shadow AIME anomaly
    if model == "Gemini 3 Flash":
        ax.annotate("Protocol\nfailure",
                     xy=(0 + bar_width, 0), xytext=(0 + bar_width + 0.35, 18),
                     fontsize=8, color="#B2182B", fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color="#B2182B", lw=1.2),
                     ha="center")

handles = [
    mpatches.Patch(color=COLORS_API, label="Official API"),
    mpatches.Patch(color=COLORS_APP, label="Official Web App"),
    mpatches.Patch(color=COLORS_SHADOW, label="Shadow Relay"),
]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False,
           bbox_to_anchor=(0.5, 1.02), fontsize=11)
fig.suptitle("Figure 1. Accuracy (%) by Model, Endpoint, and Benchmark",
             y=1.08, fontsize=14, fontweight="bold")
plt.tight_layout()
fig.savefig(OUT / "fig1_endpoint_divergence.png")
fig.savefig(OUT / "fig1_endpoint_divergence.pdf")
plt.close(fig)
print("  -> fig1_endpoint_divergence.png / .pdf")


# =====================================================================
# Figure 2: Safety heatmap
# =====================================================================
print("Figure 2: Safety heatmap ...")

safety_data = np.array([
    [0.000, 0.000, 0.000],  # GPT
    [0.088, 0.150, 0.150],  # Claude
    [0.060, 0.100, 0.070],  # Gemini
])
row_labels = ["GPT-5.4", "Claude Sonnet 4.6", "Gemini 3 Flash"]
col_labels = ["API", "App", "Shadow"]

fig, ax = plt.subplots(figsize=(6, 3.5))
im = ax.imshow(safety_data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=0.20)

ax.set_xticks(range(3))
ax.set_xticklabels(col_labels, fontsize=11)
ax.set_yticks(range(3))
ax.set_yticklabels(row_labels, fontsize=11)

# Annotate cells
for i in range(3):
    for j in range(3):
        val = safety_data[i, j]
        color = "white" if val > 0.12 else "black"
        ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                fontsize=13, fontweight="bold", color=color)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Mean Harm Score", fontsize=10)

ax.set_title("Figure 2. Mean Harm Score by Model and Endpoint\n(lower is safer)",
             fontsize=12, fontweight="bold", pad=12)
plt.tight_layout()
fig.savefig(OUT / "fig2_safety_heatmap.png")
fig.savefig(OUT / "fig2_safety_heatmap.pdf")
plt.close(fig)
print("  -> fig2_safety_heatmap.png / .pdf")


# =====================================================================
# Figure 3: Experiment architecture flowchart
# =====================================================================
print("Figure 3: Experiment architecture flowchart ...")

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")

box_style = dict(boxstyle="round,pad=0.4", facecolor="#E8E8E8", edgecolor="#333", linewidth=1.2)
api_style = dict(boxstyle="round,pad=0.4", facecolor="#D1E5F0", edgecolor=COLORS_API, linewidth=1.5)
app_style = dict(boxstyle="round,pad=0.4", facecolor="#FDDBC7", edgecolor=COLORS_APP, linewidth=1.5)
shd_style = dict(boxstyle="round,pad=0.4", facecolor="#D9F0D3", edgecolor=COLORS_SHADOW, linewidth=1.5)
bench_style = dict(boxstyle="round,pad=0.3", facecolor="#FFF9C4", edgecolor="#F9A825", linewidth=1.2)
score_style = dict(boxstyle="round,pad=0.4", facecolor="#F3E5F5", edgecolor="#7B1FA2", linewidth=1.5)

# Title
ax.text(6, 7.5, "Experiment Architecture", ha="center", va="center",
        fontsize=15, fontweight="bold")

# Benchmark box (top)
ax.text(6, 6.6, "Benchmark Suite\nAIME · GPQA · MedQA · LegalBench · MMLU-Pro · Safety",
        ha="center", va="center", fontsize=9, bbox=bench_style)

# Three endpoint paths
# API
ax.text(2, 5.0, "Official API\n(E_API)", ha="center", va="center",
        fontsize=10, fontweight="bold", bbox=api_style)
ax.text(2, 3.6, "Provider SDK / HTTP\nreasoning_effort = high\ntemperature = 0\nDirect model access",
        ha="center", va="center", fontsize=8, bbox=api_style)

# App
ax.text(6, 5.0, "Official Web App\n(E_App)", ha="center", va="center",
        fontsize=10, fontweight="bold", bbox=app_style)
ax.text(6, 3.6, "Playwright automation\nThinking mode enabled\nNo parameter control\nSubscription-dependent",
        ha="center", va="center", fontsize=8, bbox=app_style)

# Shadow
ax.text(10, 5.0, "Shadow Relay\n(E_Shadow)", ha="center", va="center",
        fontsize=10, fontweight="bold", bbox=shd_style)
ax.text(10, 3.6, "Third-party relay API\nSame params as E_API\n6× cost multiplier\nRelay may modify output",
        ha="center", va="center", fontsize=8, bbox=shd_style)

# Arrows from benchmark to endpoints
for xpos in [2, 6, 10]:
    ax.annotate("", xy=(xpos, 5.45), xytext=(6, 6.2),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

# Model boxes at bottom of each path
for xpos, label in [(2, "GPT-5.4\nClaude Sonnet 4.6\nGemini 3 Flash"),
                     (6, "GPT-5.4\nClaude Sonnet 4.6\nGemini 3 Flash"),
                     (10, "GPT-5.4\nClaude Sonnet 4.6\nGemini 3 Flash")]:
    ax.text(xpos, 2.3, label, ha="center", va="center", fontsize=8,
            bbox=box_style)
    ax.annotate("", xy=(xpos, 2.75), xytext=(xpos, 3.15),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.1))

# Scoring & Comparison box
ax.text(6, 1.0, "Unified Scoring Pipeline\nMC extraction · AIME integer extraction · GPT-5.4 safety judge\n→ Accuracy, Harm Score, RCI, AR",
        ha="center", va="center", fontsize=9, bbox=score_style)

# Arrows from model boxes to scoring
for xpos in [2, 6, 10]:
    ax.annotate("", xy=(xpos if xpos == 6 else (xpos + 0.8 if xpos < 6 else xpos - 0.8), 1.5),
                xytext=(xpos, 1.95),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.1))

ax.set_title("Figure 3. Experimental Design and Data Collection Architecture",
             fontsize=13, fontweight="bold", pad=15, loc="center")
plt.tight_layout()
fig.savefig(OUT / "fig3_architecture.png")
fig.savefig(OUT / "fig3_architecture.pdf")
plt.close(fig)
print("  -> fig3_architecture.png / .pdf")


# =====================================================================
# Figure 4: Gemini Shadow AIME failure illustration
# =====================================================================
print("Figure 4: Gemini Shadow AIME failure illustration ...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left panel: bar comparison of AIME scores across endpoints for all models
ax = axes[0]
models_short = ["GPT-5.4", "Claude\nSonnet 4.6", "Gemini 3\nFlash"]
aime_api    = [93.3, 60.0, 96.7]
aime_app    = [66.7, 83.3, 96.7]
aime_shadow = [86.7, 76.7,  0.0]

x = np.arange(3)
w = 0.25
b1 = ax.bar(x - w, aime_api, w, color=COLORS_API, label="API", edgecolor="white")
b2 = ax.bar(x, aime_app, w, color=COLORS_APP, label="App", edgecolor="white")
b3 = ax.bar(x + w, aime_shadow, w, color=COLORS_SHADOW, label="Shadow", edgecolor="white")

for bars in [b1, b2, b3]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1.5,
                f"{h:.1f}", ha="center", va="bottom", fontsize=9)

# Highlight the 0.0
ax.annotate("0.0%\n(protocol failure)", xy=(2 + w, 0), xytext=(2 + w + 0.15, 25),
            fontsize=9, color="#B2182B", fontweight="bold", ha="center",
            arrowprops=dict(arrowstyle="->", color="#B2182B", lw=1.5))

ax.set_xticks(x)
ax.set_xticklabels(models_short)
ax.set_ylabel("AIME 2025 Accuracy (%)")
ax.set_ylim(0, 115)
ax.set_title("(a) AIME 2025 Accuracy by Model and Endpoint", fontweight="bold")
ax.legend(frameon=False, fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Right panel: Failure anatomy diagram
ax = axes[1]
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

ax.set_title("(b) Anatomy of the Gemini Shadow AIME Failure", fontweight="bold", pad=10)

# Flow diagram
flow_box = dict(boxstyle="round,pad=0.5", edgecolor="#333", linewidth=1.2)

ax.text(5, 9.2, "Gemini 3 Flash via Shadow Relay", ha="center", fontsize=11,
        fontweight="bold", bbox=dict(**flow_box, facecolor="#D9F0D3"))

ax.annotate("", xy=(5, 8.1), xytext=(5, 8.7),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

ax.text(5, 7.6, "Model begins extended reasoning\n(mathematical working visible in response)",
        ha="center", fontsize=9, bbox=dict(**flow_box, facecolor="#FFF9C4"))

ax.annotate("", xy=(5, 6.5), xytext=(5, 7.1),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

ax.text(5, 5.9, "Response truncated mid-sentence\nby relay (all 30/30 items)",
        ha="center", fontsize=9, color="#B2182B", fontweight="bold",
        bbox=dict(**flow_box, facecolor="#FFCDD2"))

ax.annotate("", xy=(5, 4.8), xytext=(5, 5.4),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

ax.text(5, 4.2, "No final-answer marker present\n(no \\boxed{}, no 'Final Answer:', no standalone integer)",
        ha="center", fontsize=9,
        bbox=dict(**flow_box, facecolor="#FFF3E0"))

ax.annotate("", xy=(5, 3.1), xytext=(5, 3.7),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

ax.text(5, 2.4, "Scorer extracts incidental tail integer\nfrom unfinished reasoning (27/30)\nor finds nothing (3/30)",
        ha="center", fontsize=9,
        bbox=dict(**flow_box, facecolor="#E8EAF6"))

ax.annotate("", xy=(5, 1.3), xytext=(5, 1.85),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.3))

ax.text(5, 0.7, "Result: 0/30 correct → 0.0% accuracy",
        ha="center", fontsize=10, fontweight="bold", color="#B2182B",
        bbox=dict(**flow_box, facecolor="#FFCDD2"))

fig.suptitle("Figure 4. The Gemini Shadow AIME Anomaly", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
fig.savefig(OUT / "fig4_gemini_shadow_aime.png")
fig.savefig(OUT / "fig4_gemini_shadow_aime.pdf")
plt.close(fig)
print("  -> fig4_gemini_shadow_aime.png / .pdf")

print("\nAll figures generated in:", OUT)
