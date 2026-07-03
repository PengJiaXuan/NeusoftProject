@echo off
setlocal

if not exist logs mkdir logs

if "%VERTEX_API_KEY%"=="" if "%GOOGLE_VERTEX_API_KEY%"=="" if "%GOOGLE_API_KEY%"=="" if "%GOOGLE_KEY%"=="" (
  echo Missing Gemini official API credentials.
  echo Set one of: VERTEX_API_KEY, GOOGLE_VERTEX_API_KEY, GOOGLE_API_KEY, GOOGLE_KEY
  exit /b 1
)

if "%OPENAI_API_KEY%"=="" if "%OPENAI_KEY%"=="" (
  echo Warning: safety scoring needs OPENAI_API_KEY or OPENAI_KEY.
  echo The run may stop at safety if no OpenAI judge key is available.
)

echo Running Gemini official API rerun...
echo Run ID: formal_gemini_api_vertex_v1
echo Vertex is preferred automatically when VERTEX_API_KEY is present.

set PYTHONUNBUFFERED=1
py -3 run_experiment.py --run-id formal_gemini_api_vertex_v1 --models gemini-3-flash --endpoints api --benchmarks aime gpqa medqa legal mmlu_pro safety >> logs\formal_gemini_api_vertex_v1.out.log 2>&1

echo.
echo Gemini API rerun finished. Log: logs\formal_gemini_api_vertex_v1.out.log
