# Unhandled Tasks Summary

- Source: QA audit across `research_lib/skills/*/SKILL.md`
- Date: 2026-06-10
- Rule used in this audit: if current workflow did not define enough steps, the item is recorded as `无法处理` instead of guessed.

## Summary

Most unsupported items are not “impossible”; they are boundary issues where the daily task belongs to another skill, needs a small MCP/skill enhancement, or needs MCG to choose a default policy. The cleanest structure is to keep the existing skill boundaries and add a few explicit cross-skill handoff rules plus small workflow extensions.

## All Unhandled Items Index

This section concentrates every item marked `无法处理` or equivalent in the per-skill QA files.

| Origin skill | Task | Type | Proposed resolution |
|---|---|---|---|
| `task-monitor` | Generate optcfg after NIO complete | Missing workflow | Add dry-run-first optcfg creation workflow or route to `optq-mcp`. |
| `task-monitor` | Track `superrunOpt_ADMLQ_*` submissions end-to-end | Missing workflow | Add trace flow for submitted cfg -> queue state -> NIO -> OPTQ. |
| `task-monitor` | firewall/solver-budget concrete details | Missing concrete patterns | Put detailed patterns in `diffsolver-operator`; `task-monitor` routes there. |
| `task-monitor` | consumer/scheduler liveness | Missing workflow | Add scheduler/consumer liveness checks. |
| `task-monitor` | freq30 -> onetrain conversion | Wrong owner | Route to `dpvcfg-editor`. |
| `dpvcfg-editor` | freq30 -> onetrain with no template/defaults | Needs policy/input | MCG chooses reverse defaults or require an onetrain template. |
| `dpvcfg-editor` | snaptime retarget when no rename tooling exists | Missing fallback | Add structured XML retarget fallback. |
| `dpvcfg-editor` | production conversion with no target env/path/mode | Needs input | Add required production target checklist. |
| `dpvcfg-editor` | generate and submit test XML during this QA audit | Out of scope for audit | Actual execution should be a separate edit task with checkpoint/commit. |
| `dpvcfg-editor` | generate risk/tvr/univ/group variants with no base/parameter grid/field locations | Needs input | Require base XML and parameter grid before generation. |
| `opt-analyst` | multi-snaptime average summary | Missing policy/workflow | Add `build_multi_snaptime_summary` aggregation policy. |
| `opt-analyst` | exact solver-internal risk/TVR conflict cause | Beyond evidence workflow | Keep evidence-level classification, or add solver-debug workflow if needed. |
| `nio-verifier` | risk exposure change | Wrong owner | Route to `opt-analyst`/`niupos`. |
| `nio-verifier` | VA candidate recommendation from poscorr + optresult | Wrong owner | Route to `opt-analyst`. |
| `nio-verifier` | datacfg multi-server/multi-snaptime enumeration | Missing workflow | Add datacfg parser -> completeness matrix helper. |
| `nio-verifier` | retry decision after ADMLQ done but NIO incomplete | Wrong owner | `nio-verifier` provides evidence; `task-monitor` uses `run_decider.py`. |
| `nio-verifier` | longshort/longindex vs baseline performance judgment | Wrong owner | Route to `opt-analyst`. |
| `diffsolver-operator` | submit configs via `superrunOpt` | Missing workflow / likely wrong owner | Keep runtime operator read-only or add explicit dry-run submission adapter. |
| `diffsolver-operator` | NIO completeness | Wrong owner | Route to `nio-verifier`/`task-monitor`. |
| `diffsolver-operator` | detailed optresult quality metrics | Partial workflow | Route detailed metrics to `opt-analyst`; keep runtime-vs-quality separation here. |
| `diffsolver-operator` | generate/modify XML | Wrong owner | Route to `dpvcfg-editor`. |
| `diffsolver-operator` | livehist/checkpoint debug | Wrong owner | Route to `nio-verifier`. |
| `diffsolver-operator` | SubmissionCheck conversion/validation | Wrong owner | Route to `submission-checker`. |
| `diffsolver-operator` | MCP self-check/restart/repair | Missing workflow | Add MCP healthcheck tooling only if MCG wants operational repair. |
| `submission-checker` | full cfgqueue productionization audit | Missing source adapter | Add cfgqueue artifact adapter or route config generation to `dpvcfg-editor`. |
| `submission-checker` | runpysim-specific path audit | Missing source adapter | Add runpysim artifact adapter. |
| `submission-checker` | standalone production naming audit | Missing rules/checker | Add naming checklist/checker from SubmissionCheck rules. |
| `submission-checker` | ADMLQ/diffsolver readiness for submission | Wrong owner | Queue/runtime readiness belongs to `task-monitor`/`diffsolver-operator`. |
| `submission-checker` | superrunOpt/OPTQ result quality | Wrong owner | Route to `opt-analyst`. |
| `submission-checker` | fixed-format production report | Missing template | Add report template if MCG wants stable output. |
| `workflow-miner` | actually apply skill/MCP updates | Deliberately read-only | Keep as recommendation-only or allow draft patches after confirmation. |

## Transfer To Existing Skill

These tasks should not be added wholesale to the skill where they appeared; they should be routed to an existing specialized skill.

| Origin skill | Unhandled task | Recommended owner | Proposed handling |
|---|---|---|---|
| `task-monitor` | freq=30 cfg 转 onetrain 后快速补跑/检查 | `dpvcfg-editor` | Add a handoff note in `task-monitor`: conversion is handled by `dpvcfg-editor`; `task-monitor` only monitors the resulting queue/NIO/OPTQ state. |
| `nio-verifier` | 风险暴露是否变化 | `opt-analyst` or `niupos` | `nio-verifier` can provide explicit NIO paths and poscorr evidence; exposure/BarraStyle interpretation should be `opt-analyst`/`niupos`. |
| `nio-verifier` | 综合 poscorr 和 optresult 选择 VA 候选 | `opt-analyst` | Keep `nio-verifier` limited to NIO/path/poscorr evidence; `opt-analyst` owns VA recommendation. |
| `nio-verifier` | ADMLQ done 但 NIO 不完整是否 retry | `task-monitor` | `nio-verifier` reports NIO incompleteness; `task-monitor` uses `run_decider.py` for retry truth. |
| `nio-verifier` | longshort/longindex 与基线表现同水平 | `opt-analyst` | Treat as performance/result judgment, not artifact verification. |
| `diffsolver-operator` | NIO 是否生成完整 | `nio-verifier` or `task-monitor` | `diffsolver-operator` reports runtime health; NIO completeness is checked by `nio-verifier`/`task-monitor`. |
| `diffsolver-operator` | 生成或修改 cfgqueue XML 给 diffsolver 跑 | `dpvcfg-editor` | `diffsolver-operator` can define comparison axes; `dpvcfg-editor` edits/generates XML. |
| `diffsolver-operator` | livehist / checkpoint debug | `nio-verifier` | Runtime logs stay in `diffsolver-operator`; artifact/debug tools are in `nio-verifier`. |
| `diffsolver-operator` | SubmissionCheck converter / validation | `submission-checker` | Keep production conversion and validation out of runtime operator. |
| `submission-checker` | ADMLQ/diffsolver 队列判断 | `task-monitor` or `diffsolver-operator` | `submission-checker` starts after source artifacts and production intent are clear. |
| `submission-checker` | superrunOpt/OPTQ 结果本身是否合格 | `opt-analyst` | `submission-checker` validates production conversion, not optresult quality. |

## Suggested Skill/MCP Enhancements

These are common enough in history and QA to justify small, explicit workflow additions.

### 1. `task-monitor`: optcfg creation workflow

Problem: `task-monitor` can confirm OPTQ handoff, but cannot generate optcfg.

Proposal:
- Add a dry-run-first `create_optcfg` handoff flow using `optq-mcp`.
- Inputs: source dpvcfg, resolved NIO path, `nioname`, target OPTQ, naming mode.
- Defaults: `nioname_YYMMDD-HHmmSS.xml`; `Alpha.niodir` is directory only.
- Safety: never write/submit unless user explicitly asks; dry-run prints target XML path and key fields.

Need MCG confirmation:
- Should same-name-as-dpvcfg ever be an automatic fallback, or remain explicit-only?

### 2. `task-monitor`: superrunOpt_ADMLQ tracking

Problem: common workflow asks to track configs submitted through `superrunOpt_ADMLQ_*`, but current skill lacks submission/trace rules.

Proposal:
- Add a trace flow: record submitted cfg list, queue family, source XML, consumed `.done.xml`, run output, NIO completeness, OPTQ handoff.
- Keep actual submission dry-run unless user explicitly requests execution.
- Support queues `semi`, `semi2`, `diffsol` as research queues, not production-risk queues.

Need MCG confirmation:
- Which `superrunOpt_ADMLQ_*` wrappers should be canonical for `semi`, `semi2`, and `diffsol` across clusters?

### 3. `task-monitor`: consumer/scheduler liveness

Problem: user often asks whether ADMLQ consumer/scheduler is alive, but current workflow only covers diffsolver worker count.

Proposal:
- Add scheduler liveness checks for `adml.py -c infodict_*.json`, recent `log/ADMLQ_*.log` timestamp, queue produce/consume movement, and retry/fail directory movement.
- Report as `blocked by runtime health` when scheduler/consumer is down or stale.

Need MCG confirmation:
- What stale threshold should be used by default: 10 minutes, 30 minutes, or queue-specific?

### 4. `task-monitor` and `diffsolver-operator`: firewall/solver-budget concrete log patterns

Problem: both skills mention firewall/solver budget, but `task-monitor` lacks concrete fields and `diffsolver-operator` only defines diagnosis generally.

Proposal:
- Put canonical log patterns into `diffsolver-operator`, and have `task-monitor` hand off detailed diffsolver health there.
- Include markers: firewall, `new_solver_failed`, `global solver budget exhausted`, solver lease active/stale, GPU unhealthy, `Simulation done` false-success.

Need MCG confirmation:
- Are there additional internal log markers that should be treated as hard failure vs warning?

### 5. `dpvcfg-editor`: freq30 -> onetrain defaults

Problem: onetrain -> frequent defaults are explicit, but reverse defaults are not.

Proposal:
- Add a reverse conversion profile.
- Candidate default based on history/Q_agent: `freq=99999`, `modelDecayNum=1`, and repo-specific/default `di_delay` only if a template or explicit user value exists.
- Safer default: require either an onetrain template or explicit reverse parameters.

Need MCG confirmation:
- Should `di_delay=3163` be a global default for freq30 -> onetrain, or only copied from an onetrain template?

### 6. `dpvcfg-editor`: snaptime retarget without rename tooling

Problem: current workflow depends on existing rename tooling.

Proposal:
- Add a structured XML retarget fallback in `dpvcfg-mcp`: update filename, `Macros.SNAPTIME`, `dumpName`, path components containing old snaptime, and any snaptime-tagged output names.
- Dry-run should list every field/path that would change.

Need MCG confirmation:
- Should this fallback update every occurrence of old snaptime in XML text, or only known safe fields?

### 7. `dpvcfg-editor`: production conversion target contract

Problem: “production 可跑版本” cannot be inferred without target env/path/mode.

Proposal:
- Add a required input checklist: production target root, script path policy, model path policy, flags to clear/set, and validation command.
- If missing, ask MCG instead of editing.

Need MCG confirmation:
- Do you want a standard production target profile in `research_lib/config/clusters/*.json`, or should production conversion always require explicit target paths?

### 8. `opt-analyst`: multi-snaptime average summary

Problem: common workflow asks for average summary across snaptimes, but no aggregation policy exists.

Proposal:
- Add `build_multi_snaptime_summary` to `optq-mcp`.
- Match by normalized candidate name.
- Default aggregation should report per-snaptime metrics, count of available snaptimes, simple mean, and missing snaptimes; no weighted average unless configured.

Need MCG confirmation:
- Should the default ranking use simple mean full-period `OPT`, worst-snaptime `OPT`, or a combined score such as mean minus missing penalty?

### 9. `nio-verifier`: datacfg multi-server/multi-snaptime matrix

Problem: current workflow can check explicit NIO paths but cannot enumerate datacfg multi-server/multi-snaptime outputs.

Proposal:
- Add `dpvcfg-mcp`/`nio-mcp` helper to parse datacfg entries into explicit expected NIO paths, then run `checknio` for each server x snaptime pair.
- Output a completeness matrix.

Need MCG confirmation:
- Which datacfg schema variants should be supported first?

### 10. `submission-checker`: cfgqueue/runpysim/superrunOpt boundary adapters

Problem: `submission-checker` can validate production artifacts, but does not know how to judge cfgqueue/runpysim/superrunOpt source-specific readiness.

Proposal:
- Add adapters that only resolve source artifacts into explicit cfg/model/NIO/production target inputs.
- Keep quality decisions outside `submission-checker`: opt quality to `opt-analyst`, queue completion to `task-monitor`, runtime health to `diffsolver-operator`.

Need MCG confirmation:
- Should source adapters live in `submission-checker`, or should they live in separate MCP wrappers and feed `submission-checker` only normalized artifact manifests?

### 11. `workflow-miner`: apply recommended updates

Problem: `workflow-miner` can recommend skill/MCP updates but cannot apply them.

Proposal:
- Keep `workflow-miner` read-only by design.
- Add a handoff convention: recommendation file -> MCG confirmation -> `skill-creator`/manual patch updates.

Need MCG confirmation:
- Should workflow-miner stay strictly read-only, or may it create draft patch files under `/dat/workspace/xiongzhang/tmp`?

## Recommended Next Structure

Recommended ownership:

- `workflow-miner`: read-only history mining and update proposals.
- `task-monitor`: queue state, retry truth via `run_decider.py`, NIO complete gating, OPTQ handoff, scheduler liveness.
- `diffsolver-operator`: diffsolver runtime health and experiment alignment, not XML editing or production validation.
- `dpvcfg-editor`: all XML/datacfg/script-contract edits and cfgqueue generation.
- `nio-verifier`: artifact verification: path, completeness, alignment, hist/live, checkpoint, poscorr.
- `opt-analyst`: optresult quality, VA, risk/TVR/BarraStyle, candidate decisions.
- `submission-checker`: production conversion, checkcfg, validation, hist/live evidence for submission, upload dry-run.

Recommended cross-skill handoff pattern:

1. If the task starts from “history/what do I usually do”, use `workflow-miner`.
2. If it asks “is queue/run done”, use `task-monitor` or `diffsolver-operator`.
3. If it asks “edit/generate XML”, use `dpvcfg-editor`.
4. If it asks “is NIO complete/aligned”, use `nio-verifier`.
5. If it asks “is result good / VA / risk / TVR”, use `opt-analyst`.
6. If it asks “can this become production submission”, use `submission-checker`.

## Questions For MCG

1. For freq30 -> onetrain, should `di_delay=3163` be a global default, or only copied from an onetrain template?
2. For multi-snaptime optresult ranking, should default ranking be simple mean full-period `OPT`, worst-snaptime `OPT`, or mean with missing-snaptime penalty?
3. For snaptime retarget fallback, should it update every occurrence of the old snaptime in XML text, or only known safe fields?
4. For source-to-submission adapters, do you prefer adapters inside `submission-checker`, or separate normalized artifact-manifest MCPs?
5. Should `workflow-miner` remain strictly read-only, or may it create draft patch files under `/dat/workspace/xiongzhang/tmp` after mining?
