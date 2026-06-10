---
name: admlq-debugger
description: Use when an AutoDML ADMLQ or ADMLQ_diffsolver queue is failing, stuck, repeatedly retrying, routing tasks to failed, not consuming source cfgs, not producing complete NIOs, or appears to need a root-cause fix in queue/runtime/config code. Also use when debugging live ADMLQ incidents that may require reading /dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2.
---

# ADMLQ Debugger

Announce: `I'm using admlq-debugger to locate the ADMLQ fault, separate live-queue symptoms from root cause, and apply the smallest safe fix.`

## Default Paths

- AutoDML repo: `/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2`
- ADMLQ root: `/dat/usercache/xiongzhang/projects/DML_workspace`
- Standard NIO checker: `/dat/usercache/xiongzhang/projects/DML_workspace/tools/checknio.py -s 20220101`
- AutoDML guide: `/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2/docs/AI_ADML_GUIDE.md`
- Retry truth source: `autodml/runtime/run_decider.py`
- Runtime routing: `autodml/runtime/scheduler.py`, `autodml/runtime/worker.py`, `autodml/runtime/retry_policy.py`
- Queue state: `autodml/runtime/queue_store.py`, `logdir/*.runtime_state.json`, `logdir/*.producer.last_error.log`

## When To Use This Instead Of Task Monitor

Use `task-monitor` for status classification and acceptance checks.
Use this skill when the state is broken or ambiguous and the task is to find the cause and fix it.

Typical triggers:

- source XML stays in `ADMLQ_*` or becomes `*.done.xml` but no generated run progresses
- jobs accumulate in `*_mulworkdir_retry` or `*_mulworkdir_failed`
- `runtime_state.json` heartbeat, queue size, worker count, or producer errors look wrong
- scheduler/worker/gpu allocation/retry routing behavior appears buggy
- NIO exists but ADMLQ keeps retrying or fails to hand off
- diffsolver queue is stuck because of workers, GPU/firewall, solver leases, or skip-only cycles

## Safety Contract

Start read-only. Do not kill processes, restart schedulers, move queue files, clear retry metadata, submit OPTQ, or edit a live `infodict*.json` unless MCG explicitly confirms the exact target and expected effect.

If changing a git repo, first inspect `git status` and create a checkpoint commit when possible. Keep user changes intact.

If an operational fix is needed, report the exact paths/processes/queues affected before acting.

## Fault Workflow

1. Define the incident scope:
   `infodict path`, project name/index, `cfgdir`, source cfg, generated cfg, nioname, target queue family, and whether the scheduler is live.
2. Read `/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2/docs/AI_ADML_GUIDE.md` if the queue topology or safety boundary is unclear.
3. Snapshot queue state:
   source XML and `*.done.xml`, `*_mulworkdir`, `*_mulworkdir_done`, `*_mulworkdir_retry`, `*_mulworkdir_failed`, sibling `*.xml.log`, `*.xml.err`, `*.retry.json`, `runtime_state.json`, and `producer.last_error.log`.
4. Classify one primary failure mode:
   `producer stopped`, `worker stopped`, `worker capacity/GPU blocked`, `source routing bug`, `mode plugin shard bug`, `remote execution failure`, `runtime patch failure`, `retry policy/routing bug`, `NIO incomplete`, `terminal model/script failure`, `downstream OPTQ issue`, or `external server/access failure`.
5. For retry/done/failed routing, call or inspect `autodml/runtime/run_decider.py`; treat `decide_run_outcome()` and NIO completeness logic as the source of truth.
6. For NIO questions, extract `OpNio2.dumpPath`, `dumpName`, `delay`, `dateoffset`, and `SNAPTIME`; run the standard checknio command. Full-period `tratio=1` is the strict complete gate.
7. If logs show multiple errors, prioritize the earliest substantive failure over finalization stack traces.
8. Decide the fix class:
   live operation requiring confirmation, cfg/infodict correction requiring confirmation, model script issue outside AutoDML, or AutoDML code bug that can be patched.

## Evidence Commands

Prefer targeted commands and keep outputs summarized:

```bash
find /path/to/ADMLQ_family -maxdepth 1 -type f | wc -l
find /path/to/ADMLQ_family_mulworkdir_retry -maxdepth 1 -name '*.xml' | head
tail -200 /path/to/logdir/project.log
tail -200 /path/to/logdir/project.producer.last_error.log
python3 /dat/usercache/xiongzhang/projects/DML_workspace/tools/checknio.py /abs/path/file.N,6656f -s 20220101
```

For AutoDML code investigation:

```bash
rg -n "runtime_state|retry|decide_run_outcome|producer|consumer|gpu|failed" /dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2/autodml
pytest -q tests/test_run_decider.py
pytest -q tests/test_autodml_refactor.py -k "retry or scheduler or worker"
```

Use `source ~/venv_lgb/bin/activate` if the default Python environment cannot import project dependencies.

## Repair Rules

- Live queue operations need explicit MCG approval.
- Code fixes should be minimal, mode-neutral unless the bug is mode-specific, and covered by focused tests.
- Put mode-specific XML generation or shard naming fixes in `autodml/modes/<mode>/plugin.py`.
- Put retry/done/fail routing fixes near `run_decider.py`, `worker.py`, `scheduler.py`, or `retry_policy.py`.
- Do not mark source `*.done.xml` as success; generated shard state and NIO completeness decide success.
- Do not route incomplete NIO to OPTQ as a fix for ADMLQ.

## Report Format

Use this concise shape:

```text
Scope: <infodict/project/cfgdir/source/generated/nioname>
Primary failure: <one label>
Root cause: <specific cause or strongest evidence-backed hypothesis>
Evidence:
cfg: /abs/path/file.xml
log: /abs/path/file.xml.log
err: /abs/path/file.xml.err
retry: /abs/path/file.xml.retry.json
runtime: /abs/path/project.runtime_state.json
Fix:
<operation/config/code change and why>
Validation:
<checknio/tests/log state after fix>
Needs MCG approval:
<only if live operation/destructive change/restart is needed>
```
