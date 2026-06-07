---
name: diffsolver-operator
description: Use when running or monitoring diffsolver experiments, checking ADMLQ_diffsolver queues, GPU/solver lease health, solver-budget/firewall failures, or comparing longshort/tvr/slack/loss variants. Uses gpu-monitor-mcp, admlq-mcp, and optq-mcp.
---

# DiffSolver Operator

Announce: `I'm using diffsolver-operator to inspect queue state, GPU/solver health, and diffsolver result evidence.`

## Defaults

- Diffsolver queue log: `/dat/usercache/xiongzhang/projects/DML_workspace/log/ADMLQ_diffsolver.log`
- Infodict: `/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2/configure/infodict_diffsolver.json`
- Lease dir: `/dat/workspace/xiongzhang/tmp/dpv_diffsolver_solver_leases`
- MCP entrypoints:
  - `/dat/usercache/xiongzhang/research_lib/mcps/gpu_monitor_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/optq_mcp.py`

## Runtime Health Workflow

1. Resolve queue, infodict, configured servers, worker targets, and `diffsolver_global_max_solvers`.
2. Inspect recent log tail before old history. Look for worker start/stop, queue produce, skip reasons, solver budget, firewall, unhealthy GPU, and `Simulation done`.
3. Count relevant live processes: `ADMLQ_diffsolver`, `runpysim`, `superRun`, `perfRun`, and target cfg names.
4. Compare actual workers to configured target.
5. Inspect solver leases; classify active vs stale by PID liveness and timestamp.
6. Check `nvidia-smi`/GpuStat only as far as needed to classify runtime health.
7. Stop when classified as one of: scheduler stopped, worker-count mismatch, queue-empty/skip-only, retry/fail routing, solver-budget exhaustion, GPU firewall/unhealthy, stale lease pressure, or external server/access failure.

## Experiment Comparison

When comparing variants, align by cfg family, date window, universe, risk/TVR mode, loss/slack knobs, and OPT result period. Separate runtime failure from optimizer quality.

## Guardrails

- Do not kill workers, clear leases, or change solver limits unless explicitly requested.
- A run with firewall/new_solver_failed markers plus `Simulation done` is a false-success candidate; inspect result quality before acceptance.
- Keep GPU health evidence and OPT performance evidence separate.
