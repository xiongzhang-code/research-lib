# Research MCP Servers

These MCP servers are dependency-free Python stdio wrappers around local research tools.
They implement the MCP methods `initialize`, `tools/list`, and `tools/call`.

## Servers

- `admlq_mcp.py`: ADMLQ queue state, submit/cancel dry-runs, worker process checks.
- `nio_mcp.py`: `checknio.py`, `comparenio.py`, `test_livehist.py`, `test_ckp.py`, `niupos2025`.
- `optq_mcp.py`: OPTQ status, optresult discovery, opt summary/rank/exposure helpers.
- `dpvcfg_mcp.py`: cfg discovery, `config_search.py`, dpvcfg compare/modify/datacfg checks.
- `gpu_monitor_mcp.py`: GpuStat, nvidia-smi, diffsolver monitors, solver leases, log tails.
- `submission_mcp.py`: production converter/validator/checkcfg/hist-live/upload wrappers.
- `history_index_mcp.py`: recent Codex/bash history command frequency and keyword search.

## Local Smoke Commands

```bash
python3 /dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py --list-tools
python3 /dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py --call checknio --args '{"niopath":"/path/to/file.N,6656f"}'
python3 /dat/usercache/xiongzhang/research_lib/mcps/history_index_mcp.py --call command_frequency --args '{"days":30,"limit":20}'
```

Submit/cancel/upload/conversion tools default to `dry_run=true`; set `dry_run=false` only
when execution is intended.

## MCP Client Command Form

Use one server per MCP entry. Example:

```json
{
  "mcpServers": {
    "admlq-mcp": {
      "command": "python3",
      "args": ["/dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py"]
    }
  }
}
```
