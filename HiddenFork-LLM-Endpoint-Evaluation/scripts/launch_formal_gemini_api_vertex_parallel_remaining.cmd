@echo off
setlocal EnableDelayedExpansion

set "RUN_ID=formal_gemini_api_vertex_v1"

if not exist logs mkdir logs

set "BASE_KEY="
if not "%VERTEX_API_KEY%"=="" set "BASE_KEY=%VERTEX_API_KEY%"
if "!BASE_KEY!"=="" if not "%GOOGLE_VERTEX_API_KEY%"=="" set "BASE_KEY=%GOOGLE_VERTEX_API_KEY%"
if "!BASE_KEY!"=="" if not "%GOOGLE_API_KEY%"=="" set "BASE_KEY=%GOOGLE_API_KEY%"
if "!BASE_KEY!"=="" if not "%GOOGLE_KEY%"=="" set "BASE_KEY=%GOOGLE_KEY%"

if "!BASE_KEY!"=="" (
  echo Missing Gemini official API credentials.
  echo Set one of: VERTEX_API_KEY, GOOGLE_VERTEX_API_KEY, GOOGLE_API_KEY, GOOGLE_KEY
  exit /b 1
)

echo Launching parallel Gemini API shards for remaining benchmarks...
echo Run ID: %RUN_ID%
echo Existing process can keep working on legal while these shards take mmlu_pro and safety.
echo Optional extra keys:
echo   VERTEX_API_KEY_2 for mmlu_pro
echo   VERTEX_API_KEY_3 for safety
echo.

call :launch_shard mmlu_pro VERTEX_API_KEY_2
call :launch_shard safety VERTEX_API_KEY_3

echo.
echo Shards launched. Refresh reports at the end with:
echo   py -3 run_experiment.py --run-id %RUN_ID% --models gemini-3-flash --endpoints api --benchmarks aime gpqa medqa legal mmlu_pro safety --report-only
goto :eof

:launch_shard
set "BENCH=%~1"
set "KEYVAR=%~2"
set "SHARD_KEY="
call set "SHARD_KEY=%%%KEYVAR%%%"
if "!SHARD_KEY!"=="" set "SHARD_KEY=!BASE_KEY!"

set "SHARD_LOG=logs\%RUN_ID%__%BENCH%.out.log"

echo [%BENCH%] launching...
start "Gemini API %BENCH%" cmd /c "set PYTHONUNBUFFERED=1&& set VERTEX_API_KEY=!SHARD_KEY!&& py -3 run_experiment.py --run-id %RUN_ID% --models gemini-3-flash --endpoints api --benchmarks %BENCH% >> !SHARD_LOG! 2>&1"
goto :eof
