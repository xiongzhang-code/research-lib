# MCP / Skill Implementation Index

Source plan: `/dat/usercache/xiongzhang/research_lib/mcp_skill_workflow_summary_20260607.md`

## Implemented MCPs

| MCP | Path |
|---|---|
| `admlq-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py` |
| `nio-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py` |
| `optq-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/optq_mcp.py` |
| `dpvcfg-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/dpvcfg_mcp.py` |
| `gpu-monitor-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/gpu_monitor_mcp.py` |
| `submission-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/submission_mcp.py` |
| `history-index-mcp` | `/dat/usercache/xiongzhang/research_lib/mcps/history_index_mcp.py` |

## Implemented Skills

| Skill | Path |
|---|---|
| `task-monitor` | `/dat/usercache/xiongzhang/research_lib/skills/task-monitor/SKILL.md` |
| `dpvcfg-editor` | `/dat/usercache/xiongzhang/research_lib/skills/dpvcfg-editor/SKILL.md` |
| `opt-analyst` | `/dat/usercache/xiongzhang/research_lib/skills/opt-analyst/SKILL.md` |
| `nio-verifier` | `/dat/usercache/xiongzhang/research_lib/skills/nio-verifier/SKILL.md` |
| `diffsolver-operator` | `/dat/usercache/xiongzhang/research_lib/skills/diffsolver-operator/SKILL.md` |
| `submission-checker` | `/dat/usercache/xiongzhang/research_lib/skills/submission-checker/SKILL.md` |
| `workflow-miner` | `/dat/usercache/xiongzhang/research_lib/skills/workflow-miner/SKILL.md` |

## Notes

- The MCP runtime is implemented in `/dat/usercache/xiongzhang/research_lib/mcps/common.py`.
- No third-party MCP Python package is required.
- Start MCP servers with `python3`; `/usr/local/bin/python` is Python 2 in this environment.
- Write-heavy tools default to dry-run where the wrapper can control execution.
- Temporary history indexes are written under `/dat/workspace/xiongzhang/tmp`.
- `/dat/usercache/xiongzhang/research_lib` is not currently a git repository, so no git checkpoint or commit was created.
