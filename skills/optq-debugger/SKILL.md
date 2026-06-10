---
name: optq-debugger
description: Use when an OPTQ or OptTest queue is stuck, failing, repeatedly leaving XML without result, producing empty/partial result files, missing expected done/result variant files, failing remote PySim execution, failing result merge/summary, or appears to need a root-cause fix in OPTQ/OptTest config/runtime/code. Also use when debugging live OPTQ incidents that may require reading /dat/usercache/xiongzhang/projects/versions/OptTest/v0.4.
---

# OPTQ Debugger

Announce: `I'm using optq-debugger to locate the OPTQ fault, separate live queue symptoms from root cause, and apply the smallest safe fix.`

## Default Paths

- Project OPTQ: `/dat/usercache/xiongzhang/projects/2026/06/big_scale_model/NNOPTQ_zz500`
- Legacy/default OPTQ: `/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500`
- Legacy/default optresult root: `/dat/usercache/xiongzhang/opttest/optresult/ZZ500`
- OptTest repo: `/dat/usercache/xiongzhang/projects/versions/OptTest/v0.4`
- Main OptTest entrypoint: `nnopttest.py`
- Main manager: `src/manager/OptTest_v20250826.py`
- Config/render/execute code: `src/core/optcfg.py`, `src/core/optqcfg.py`, `src/core/executor.py`
- MCP entrypoint: `/dat/usercache/xiongzhang/research_lib/mcps/optq_mcp.py`

When paths conflict, prefer the explicit user path first, then the current project OPTQ, then the legacy/default OPTQ.

## When To Use This Instead Of Related Skills

Use `task-monitor` for ADMLQ status and handoff checks.
Use `opt-analyst` for completed optresult ranking, value-added analysis, and constraint interpretation.
Use this skill when OPTQ itself is broken, ambiguous, or requires repair.

Typical triggers:

- XML stays in OPTQ and no `.result` or `.done.xml` appears after expected runtime.
- `.done.xml` exists but `.result` is missing, empty, stale, or only partially written.
- `.result.tmp` remains, variant results are not merged, or raw result waits for `*_neutBarraStyle` / `*_OPDEMEAN250` completion.
- `.log` / `.err` shows PySim, SSH, environment, NFS, PnL, simsummary, XML parse, module path, data path, or OptTest exceptions.
- Queue workers are not consuming configs, server worker counts look wrong, or a server was removed while work is in progress.
- A queue operation, XML/config repair, or OptTest code fix may be needed.

## Safety Contract

Start read-only. Do not move, delete, rename, resubmit, or mark OPTQ files done unless MCG explicitly confirms the exact target and expected effect.

Do not modify submitted training dpvcfgs to express baseline or benchmark changes. If the issue is a baseline/VA benchmark change, fix OPTQ/combocfg/benchmark references instead.

If changing a git repo, inspect `git status` first and create a checkpoint when possible. Keep user changes intact. The OptTest repo may already contain user edits; do not overwrite them.

If an operational fix affects live queue files, processes, or remote servers, report the exact paths/processes/servers before acting and wait for approval.

## Fault Workflow

1. Define incident scope:
   OPTQ dir, cfg XML name, nioname/niodir, generated `.opt.xml`, expected variants, result root, configure JSON, logdir, server list, and whether the OptTest manager is live.
2. Snapshot OPTQ state:
   raw `*.xml`, `*.done.xml`, `*.result`, `*.result.tmp`, `*.opt.xml`, `*.log`, `*.err`, extension configs/results such as `*_neutBarraStyle*` and `*_OPDEMEAN250*`, mtime, size, and current process list.
3. Read the relevant XML/config before interpreting symptoms:
   `Alpha.niodir`, `Alpha.dataname`, `delay`, `dateoffset`, `SNAPTIME`, `SAVENIO`, `SAVEPNL`, `MODULES`, template path, `cfgdir`, `logdir`, `pnl_cachedir`, `servers`, `debug`, `verbose`, and `simsummary`.
4. Classify one primary failure mode:
   `not consumed`, `worker/server unavailable`, `remote execution failed`, `xml/render failure`, `nio path/name invalid`, `module/env missing`, `pnl missing`, `summary/parser failure`, `partial result write`, `done/result ordering issue`, `variant generation failure`, `variant merge waiting`, `stale live state`, `OptTest code bug`, or `external filesystem/server issue`.
5. Prioritize earliest substantive evidence:
   Prefer the first traceback or PySim error in `.err` / manager log over later cleanup or merge messages.
6. Map state transitions:
   In OptTest v0.4, consumer writes `.result.tmp`, renames it to `.result`, then renames `.xml` to `.done.xml`. The producer merges variants only when each variant has non-empty `_<tag>.result`, matching `_<tag>.done.xml`, and no live `_<tag>.xml`.
7. Decide fix class:
   live operation requiring approval, XML/config correction requiring approval, NIO/input issue upstream, OptTest code bug, environment/server issue, or completed-result analysis that should switch to `opt-analyst`.

## Evidence Commands

Prefer targeted commands and summarize outputs:

```bash
find /path/to/NNOPTQ_zz500 -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %10s %f\n' | sort | tail -80
find /path/to/NNOPTQ_zz500 -maxdepth 1 -name '*<name>*' -printf '%TY-%Tm-%Td %TH:%TM %10s %f\n' | sort
tail -200 /path/to/file.xml.log
tail -200 /path/to/file.xml.err
tail -200 /path/to/opttest-manager.log
ps -ef | rg 'nnopttest|OptTest|runpysim|NNOPTQ'
python3 -m py_compile /dat/usercache/xiongzhang/projects/versions/OptTest/v0.4/src/manager/OptTest_v20250826.py
rg -n 'traceback|Exception|error|failed|result.tmp|done.xml|OptQCfg|_write_result|_move_file|_superRun_simple' /dat/usercache/xiongzhang/projects/versions/OptTest/v0.4/src
```

For XML inspection, use Python/lxml or `xmllint` when available; avoid ad hoc string edits for repairs.

Use `source ~/venv_lgb/bin/activate` if the default Python environment cannot import project dependencies.

## Repair Rules

- Keep repairs minimal and reversible.
- For live queue state fixes, ask MCG before moving/removing files or changing `.xml` / `.done.xml` / `.result` state.
- For XML/config fixes, edit the source OPTQ XML/config only after confirming whether it is still queued or already consumed.
- For OptTest code fixes, patch near the responsible layer:
  - queue discovery and variant merge: `src/manager/OptTest_v20250826.py`
  - XML variant generation and merge status: `src/core/optqcfg.py`
  - XML render, PnL dirs, result write: `src/core/optcfg.py`
  - remote execution and command capture: `src/core/executor.py`
- Do not hide a failed PySim run by creating a `.done.xml`; success requires valid result evidence.
- Do not claim the queue is healthy from `.done.xml` alone; check result size/content and variant merge state.
- If the issue is input NIO completeness or date alignment, switch to `nio-verifier` for the acceptance check.
- If the issue is result quality rather than runtime failure, switch to `opt-analyst`.

## Validation

Choose the narrowest validation that matches the fix:

- Read-only diagnosis: list state, logs, primary failure label, and exact evidence paths.
- XML/config repair: parse XML after edit and confirm expected filenames/state transitions.
- OptTest code fix: run focused syntax/unit-style checks available in the repo, at minimum `python3 -m py_compile` on touched Python files.
- Queue operation: re-snapshot the same file patterns and confirm the intended state changed without collateral changes.
- Result recovery: confirm non-empty `.result`, matching `.done.xml`, absence/presence of live `.xml` as expected, and summary readability.

## Report Format

Use this concise shape:

```text
Scope: <optq_dir/cfg/result/configure/server>
Primary failure: <one label>
Root cause: <specific cause or strongest evidence-backed hypothesis>
Evidence:
cfg: /abs/path/file.xml
done/result: /abs/path/file.done.xml / /abs/path/file.result
log/err: /abs/path/file.xml.log / /abs/path/file.xml.err
manager: /abs/path/manager.log
Fix:
<operation/config/code change and why>
Validation:
<commands and state after fix>
Needs MCG approval:
<only if live operation/destructive change/restart is needed>
```
