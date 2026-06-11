---
name: task-monitor
description: Use when monitoring AutoDML ADMLQ queue jobs, deciding queued/running/retry/failed/done status, checking NIO completeness, confirming OPTQ handoff, or inspecting ADMLQ_diffsolver worker health. Uses admlq-mcp, nio-mcp, optq-mcp, and gpu-monitor-mcp wrappers under research_lib/mcps.
---

# Task Monitor

Announce: `I'm using task-monitor to inspect ADMLQ state, retry/fail routing, NIO completeness, and OPTQ handoff evidence.`

## Defaults

- Queue root: `/dat/usercache/xiongzhang/projects/DML_workspace`
- OPTQ: `/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500`
- Standard NIO checker: `/dat/usercache/xiongzhang/projects/DML_workspace/tools/checknio.py -s 20220101`
- MCP entrypoints:
  - `/dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/optq_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/gpu_monitor_mcp.py`

## Workflow

1. Resolve the specific `cfgpath`, `nioname`, `queue_dir`, or ADMLQ family scope.
2. Use `admlq-mcp.inspect_queues` or direct filesystem checks to distinguish:
   queued source XML, consumed source `.done.xml`, actual run in `donedir`, retry in `retrydir`, failure in `faildir`, and logs in `logdir`.
3. If a run finished, inspect the generated cfg and call `autodml/runtime/run_decider.py` when available; treat `should_retry_after_run(cfgpath)` as the retry truth source.
4. Extract `OpNio2.dumpPath`, `OpNio2.dumpName`, `delay`, `dateoffset`, and `SNAPTIME`; verify NIO with `nio-mcp.checknio`.
5. Treat NIO as complete only when the full-period summary row has `tratio=1`.
6. If NIO is complete, use `optq-mcp.inspect_optq` and filename searches to classify OPTQ state.
7. For diffsolver queues, also inspect worker process count, recent `ADMLQ_diffsolver.log`, GPU health, and solver leases.

## OPTQ Naming

- Default superrunOpt-style config: `nioname_YYMMDD-HHmmSS.xml`.
- Same-name-as-dpvcfg mode is only for explicit user requests.
- `Alpha.niodir` should be the directory containing the NIO file, not the full NIO path.

## Status Labels

Use exactly one primary label when reporting: `queued`, `running`, `retrying`, `failed`, `done but NIO-incomplete`, `done and waiting for OPTQ`, `already in OPTQ`, or `blocked by runtime health`.

## Guardrails

- Do not infer success from source `*.done.xml`; inspect run output directories.
- Do not kill processes, cancel configs, or submit OPTQ unless explicitly requested.
- MCP submit/cancel tools are dry-run by default; set `dry_run=false` only after user intent is clear.
