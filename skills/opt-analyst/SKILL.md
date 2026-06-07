---
name: opt-analyst
description: Use when analyzing OPTQ or optresult outputs, ranking NIO candidates, comparing candidates with baselines, checking risk/exposure/turnover constraints, or deciding value added from BarraStyle and raw/neut/OPT evidence. Uses optq-mcp and nio-mcp.
---

# Opt Analyst

Announce: `I'm using opt-analyst to inspect optresult evidence, compare candidates, and turn the ranking into concrete keep/revise/retest decisions.`

## Defaults

- OPTQ: `/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500`
- optresult root: `/dat/usercache/xiongzhang/opttest/optresult/ZZ500`
- dpvcfg root: `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue`
- MCP entrypoints:
  - `/dat/usercache/xiongzhang/research_lib/mcps/optq_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py`

## Workflow

1. Resolve exact result files and matching XML/NIO names before ranking.
2. For batch summaries, use `optq-mcp.build_opt_summary` or existing `.summary` files.
3. Treat full-period `OPT` as the primary decision surface. Use `raw`, `neutBarraStyle`, `OPDEMEAN250`, cost, turnover, and BarraStyleCNTR exposures as supporting evidence.
4. For value-added tests, compare candidate position correlation with the baseline first. Use `/dat/pysimrelease/pysim-5.0.0/tools/niupos2025 basenio -l <explicit niopaths> -o 1024`.
5. Shortlist low-corr/high-OPT or high-corr/high-OPT candidates, then compare combo result deltas to the baseline.
6. End with concrete `keep`, `revise`, `neutralize`, `combine`, `rerun`, or `skip` recommendations.

## Hard Constraint Check

When asked whether constraints are satisfied:

1. Read matching opt XML/config before interpreting result metrics.
2. Capture hard/soft mode, bound values, slack flags, risk delay, TVR mode, universe/group/risklist fields, and tested NIO.
3. Build a table: configured constraint, observed metric, result file, classification.
4. Classify each constraint as `satisfied`, `violated`, `not measurable`, or `likely not encoded as hard`.
5. For turnover, distinguish net TVR from split-leg TVR and `tvrboth`/`legstate` mechanisms.

## Guardrails

- Do not pass a bare directory after `niupos2025 -l`; expand to explicit NIO paths.
- Do not claim value added from standalone OPT alone; compare against baseline/combo evidence.
- Do not edit opt XMLs or NIO definitions unless the user explicitly asks.
