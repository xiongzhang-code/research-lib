---
name: dpvcfg-editor
description: Use when creating, reviewing, comparing, or editing DynamicPV dpvcfg/datacfg XMLs, generating cfgqueue batches, converting onetrain/freq-train variants, or checking XML/script consistency. Uses dpvcfg-mcp and local DynamicPV validation tools.
---

# DPVCFG Editor

Announce: `I'm using dpvcfg-editor to inspect the XML/script contract, apply a narrow config edit, and validate the result.`

## Defaults

- cfgqueue root: `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue`
- DPV repo: `/dat/usercache/xiongzhang/projects/versions/DynamicPV/v4.3.3`
- fallback Python env: `source ~/venv_lgb/bin/activate`
- MCP entrypoint: `/dat/usercache/xiongzhang/research_lib/mcps/dpvcfg_mcp.py`

## Core Workflow

1. Read the target XML before editing.
2. Identify the tested `Port/Alpha`, linked `Modules/AlphaModule`, `OpNio2`, `Macros.SNAPTIME`, datacfg, and script path.
3. If script-facing attributes change, inspect the linked Python script before editing.
4. Keep edits limited to requested zones: cadence, decay, mode flags, loss/model knobs, path wiring, module linkage, or output naming.
5. Use structured XML parsing where practical. Preserve unrelated strategy identity, target semantics, universe, and production paths.
6. Validate by reopening the XML and, when relevant, running `dpvcfg-mcp.compare_dpvcfg`, `check_datacfg`, `test_livehist.py`, or a config generation smoke test.

## Frequent Training Shape

For onetrain to frequent-training conversion, default target values are:

- `freq=30`
- `modelDecayNum=2`
- `di_delay=9`

Do not blindly copy entire template blocks. Copy only required cadence/runtime settings and reconcile partially converted files.

## Multi-Phase cfgqueue Generation

1. Read the plan JSON first, or infer plan shape from existing phase directories.
2. Preserve layout by default: root plan JSON plus `phase*/<snaptime>/`.
3. Generate seed snaptime XMLs using `config_search.py`.
4. Retarget additional snaptimes with the existing rename tooling when present.
5. Keep naming stable unless the user asks to rename or flatten.

## Guardrails

- If the file is inside a git repo, create a git checkpoint before edits and commit after validation.
- If no repo exists, state that checkpoint/commit was skipped.
- Do not rewrite large XML sections for a narrow attribute change.
- Put temporary files under `/dat/workspace/xiongzhang/tmp`.
