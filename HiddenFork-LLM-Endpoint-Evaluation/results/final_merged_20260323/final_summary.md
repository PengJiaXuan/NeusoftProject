# Final Composite Results

This directory merges four source runs into the final paper-ready result set:

- `gpt-5.4 / api` <- `formal_main_v1`
- `gpt-5.4 / app` <- `formal_main_v1`
- `gpt-5.4 / shadow` <- `formal_shadow_rerun_v1`
- `claude-sonnet-4-6 / api` <- `formal_main_v1`
- `claude-sonnet-4-6 / app` <- `formal_claude_app_max20_v1`
- `claude-sonnet-4-6 / shadow` <- `formal_shadow_rerun_v1`
- `gemini-3-flash / api` <- `formal_gemini_api_vertex_v1`
- `gemini-3-flash / app` <- `formal_main_v1`
- `gemini-3-flash / shadow` <- `formal_shadow_rerun_v1`

Selected rationale:
- GPT API/App remained on the baseline formal run.
- All Shadow results use the unified relay rerun.
- Claude App uses the Max20 rerun.
- Gemini API uses the Vertex-based rerun.
