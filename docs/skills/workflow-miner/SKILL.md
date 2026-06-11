---
name: workflow-miner
description: Use when mining recent Codex sessions, ~/.codex/history.jsonl, or .bash_history to summarize common scripts, command frequencies, workflow patterns, recurring blockers, and candidate MCP/skill updates. Uses history-index-mcp.
---

# Workflow Miner

Announce: `I'm using workflow-miner to mine recent command and session history into reusable workflow signals.`

## Defaults

- Time window: last 30 days
- Codex sessions: `/home/xiongzhang/.codex/sessions`
- Codex history: `/home/xiongzhang/.codex/history.jsonl`
- Shell history: `/home/xiongzhang/.bash_history`
- Temporary index output: `/dat/workspace/xiongzhang/tmp`
- MCP entrypoint: `/dat/usercache/xiongzhang/research_lib/mcps/history_index_mcp.py`

## Workflow

1. Use `history-index-mcp.command_frequency` for top command families.
2. Search targeted terms with `history-index-mcp.search_history`, such as `ADMLQ`, `checknio`, `optresult`, `diffsolver`, `production_validate`, or a strategy name.
3. Write compact indexes with `history-index-mcp.write_index` when the user wants a durable artifact.
4. Group findings into: common scripts, repeated command templates, queue/result workflows, blockers/failure modes, and recommended skill/MCP updates.
5. If proposing updates, keep them concrete and scoped to existing skill/MCP files.

## Guardrails

- Do not rewrite or delete history files.
- Bash history has no timestamps; treat it as supplementary all-history evidence.
- Do not quote large private session chunks. Summarize short contexts and cite local file paths when helpful.
