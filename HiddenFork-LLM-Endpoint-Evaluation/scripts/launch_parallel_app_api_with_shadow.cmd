@echo off
setlocal

echo Shadow rerun should already be running as:
echo   formal_shadow_rerun_v1
echo.
echo Starting Claude app rerun in a separate window...
start "formal_claude_app_max20_v1" cmd /k c:\Users\admin\Desktop\Test\hidden_fork\launch_formal_claude_app_max20_v1.cmd

echo Starting Gemini API rerun in a separate window...
start "formal_gemini_api_vertex_v1" cmd /k c:\Users\admin\Desktop\Test\hidden_fork\launch_formal_gemini_api_vertex_v1.cmd

echo.
echo Parallel launch requested:
echo   Shadow: formal_shadow_rerun_v1
echo   Claude app: formal_claude_app_max20_v1
echo   Gemini API: formal_gemini_api_vertex_v1
