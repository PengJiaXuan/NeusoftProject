@echo off
setlocal

set "SHADOW_BASE_URL=https://yansd666.top"
set "SHADOW_GPT_CHANNEL_LABEL=official relay OpenAI (OpenAI official)"
set "SHADOW_CLAUDE_CHANNEL_LABEL=official relay Claude 2 (AWS + official relay)"
set "SHADOW_GEMINI_CHANNEL_LABEL=premium official relay Gemini"
set "SHADOW_PRICE_MULTIPLIER=6x"
set "SHADOW_CREDIT_NOTE=shadow api 1 RMB = 1 USD equivalent credit; model billing follows official API base pricing multiplied by 6x"

py -3 run_experiment.py --run-id formal_shadow_rerun_v1 --models gpt-5.4 claude-sonnet-4-6 gemini-3-flash --endpoints shadow --benchmarks aime gpqa medqa legal mmlu_pro safety %* >> logs\formal_shadow_rerun_v1.out.log 2>&1
