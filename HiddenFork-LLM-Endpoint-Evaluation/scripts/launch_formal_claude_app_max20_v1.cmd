@echo off
setlocal

if not exist logs mkdir logs

echo Running Claude app rerun with the current saved anthropic state...
echo Run ID: formal_claude_app_max20_v1

py -3 run_experiment.py --run-id formal_claude_app_max20_v1 --models claude-sonnet-4-6 --endpoints app --benchmarks aime gpqa medqa legal mmlu_pro safety >> logs\formal_claude_app_max20_v1.out.log 2>&1

echo.
echo Claude app rerun finished. Log: logs\formal_claude_app_max20_v1.out.log
