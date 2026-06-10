# Research Skills

Skill directories in this folder follow the Codex skill layout:

```text
skill-name/
  SKILL.md
```

Implemented skills:

- `task-monitor`: ADMLQ job state, retry/fail routing, NIO completeness, OPTQ handoff.
- `admlq-debugger`: ADMLQ fault root-cause workflow, runtime/config repair guardrails, AutoDML evidence checks.
- `optq-debugger`: OPTQ/OptTest fault root-cause workflow, live queue repair guardrails, result-state evidence checks.
- `dpvcfg-editor`: DynamicPV XML/datacfg editing, cfgqueue generation, conversion checks.
- `opt-analyst`: OPTQ/optresult analysis, value-added checks, hard-constraint evidence.
- `nio-verifier`: NIO acceptance, tratio/date/snaptime/live-hist/checkpoint checks.
- `diffsolver-operator`: ADMLQ_diffsolver runtime, GPU health, solver lease monitoring.
- `submission-checker`: production conversion, validation, checkcfg, hist/live checks.
- `workflow-miner`: session/history mining for workflow summaries and future updates.

To install a skill for Codex discovery, copy or symlink its directory into the active
Codex skills directory. Keep local edits in this `research_lib` copy if you want a
project-owned source of truth.
