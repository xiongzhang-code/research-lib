---
name: dpvcfg-editor
description: Use when rewriting or reviewing DynamicPV dpvcfg XMLs, especially converting one-train configs into frequent-training freq=30/modelDecayNum=2/di_delay=9 variants, aligning linked scripts and XML, turning training scripts/configs into production-ready versions, or generating cfgqueue multi-phase search plans and XML batches while preserving json plus phase directory layouts.
---

# DPVCFG Editor

Use this skill for DynamicPV config rewrites under `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue` and nearby production-like XMLs.

Announce at start: `I'm using the dpvcfg-editor skill to inspect the target XML, compare it with the right template, and make a narrow cfg/script conversion.`

## When this skill applies

Use this skill when the user asks to:

- rewrite or review dpvcfg XMLs under `cfgqueue`
- convert `onetrain` configs into frequent-training variants
- align XML and linked `fselect01` script changes
- turn recommended parameters into `.json + .xml`
- generate cfgqueue multi-phase parameter scans
- preserve existing `json + phase/{snaptime}` directory structure
- generate multiple snaptimes from a seed directory such as `100000 -> 133000`

## Core workflow

1. Read the target XML first.
2. If the request is to convert an `onetrain` config into a frequent-training version, read this reference template next:
   `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue/2026/04/10/nrhcr1_nzo_fq30_mdc2/nrhcr1_nzo_td14st510_fq30_huber_cache_100000.xml`
3. If the request touches the linked training script, read the `Modules/AlphaModule id="fselect01"` path and inspect that Python file before editing XML attributes that depend on script behavior.
4. Identify the edit zone before changing anything:
   - training cadence and decay: `freq`, `modelDecayNum`, `di_delay`, `midtraintimes`, `pred_delay`, `train_delay`
   - mode flags: `trainonce_flag`, `trainonly_flag`, `predictonly_flag`, `isBacktest`, `devTest`
   - loss/model knobs: `loss_type`, `predNdays`, `layerWidth`, `dropout`, `num_layers`, `num_heads`
   - path wiring: `modeldir`, `modelparamdir`, `featuresidxdir`, `cachedir`, `dataconfig`, `opdict`
   - module linkage: `Modules/AlphaModule`, `Port/Alpha mId`, and script path consistency
5. Make the smallest XML or script change set that satisfies the conversion.
6. Validate the edited config or script unless the user explicitly says to skip it.

## Multi-phase scan workflow

When the request is about cfgqueue parameter scans rather than one-off XML edits:

1. Read the root-level plan JSON first if it exists; otherwise inspect the target base XML and the current phase directory layout.
2. Preserve the current layout by default:
   - `<root>/<plan>.json`
   - `phase1/100000`, `phase1/133000`
   - `phase2/100000`, `phase2/133000`
3. Generate `100000` XMLs first from the root-level JSON via `config_search.py`.
4. If additional snaptimes are required, copy the seed directory and retarget it with `rename_dpvcfg.py`.
5. Keep naming stable across phases; for the current gpuf example prefer `dk_gpuf_seqout_td5_phase2.json`.
6. Read [references/multiphase_scan_workflow.md](references/multiphase_scan_workflow.md) before editing when the request involves multi-phase planning, JSON templates, or multi-snaptime generation.

## Frequent-training conversion rules

- Treat the freq-train target shape as:
  - `freq=30`
  - `modelDecayNum=2`
  - `di_delay=9`
- Do not blindly overwrite unrelated attributes from the template. Copy only the cadence and closely coupled runtime settings that are required for the conversion.
- Keep target definitions, universe settings, data paths, cache roots, and output namespaces aligned with the target strategy unless the user asks to replace them.
- When converting from an `onetrain` config, inspect whether `trainonce_flag`, `modeldir`, `modelparamdir`, `featuresidxdir`, and `id` naming still make sense for a frequent-training workflow.
- If the target XML already looks partially converted, reconcile it against the freq-train template instead of restarting from scratch.

## Production conversion rules

- When converting a training script or config toward production, compare against the nearest production-like XML or script pair, not just the nearest experiment file.
- Remove or reduce debug-only behavior only when it is clearly training-only or user-requested.
- Keep Python/XML contract aligned for every config-facing key added, removed, or renamed.
- Preserve the model family skeleton unless the user explicitly asks for architectural changes.
- Treat script path changes and `Port/Alpha` attribute changes as coupled edits.

## Review checklist

- `Modules/AlphaModule id="fselect01"` points to the intended script.
- `Port/Alpha mId` matches the module id.
- Strategy names should put the snaptime suffix at the very end. For example,
  prefer `..._v0slack_oldfirst_100000` over `..._100000_v0slack_oldfirst`;
  keep XML filename stem, `Port/Alpha id`, and `OpNio2 dumpName` aligned.
- When writing cfgqueue XMLs that will be submitted by `superrunOpt.py`, do
  not write an XML declaration with an encoding, such as
  `<?xml version='1.0' encoding='utf-8'?>`. The current
  `superrunOpt.py -> PysimConfig` path may parse from a Unicode string, and
  lxml raises `ValueError: Unicode strings with encoding declaration are not
  supported`. Prefer the repo's `PysimConfig` writer when practical; otherwise
  write XML without an XML declaration and validate that the first line starts
  with `<PySim`.
- `predNdays`, `targetNdays`, and loss-related attributes are consistent with the script.
- Training cadence fields are internally consistent after conversion.
- Output dirs and ids will not collide with unrelated existing runs.
- No stale training-only or predict-only flag remains by accident.
- If `OpNio2 scale2book=true` is used for validation/comparison, place it after required neutralization ops such as `OpGroupNeut`, or explicitly document that the dumped `NIODir` NIO is pre-neutralization and not the final evaluated object.

## Validation defaults

- Default runtime environment for DynamicPV validation:
  `source /home/xiongzhang/venv_lgb/bin/activate`
- Use the venv `python` for:
  - `dynamicpv/dpvdebug/test_livehist.py`
  - `tests/run_loss_livehist_matrix.py`
- Use the same venv for multi-phase generation helpers such as:
  - `/dat/usercache/xiongzhang/projects/DML_workspace/config_search.py`
  - `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue/2026/04/rename_dpvcfg.py`
- For generated cfgqueue XMLs, include a parse check that matches the submit
  path before handing them off. At minimum, verify there is no XML declaration
  with `head -n 1 <xml>` and parse one representative file through
  `dynamicpv.common.pysim_config.PysimConfig` from the environment used by
  `superrunOpt.py`.
- If a cfgqueue scan generates multiple XMLs and the user wants them submitted, default queue command:
  `source /home/xiongzhang/venv_lgb/bin/activate && python /home/xiongzhang/tools/superrunOpt.py -q semi <cfgpaths...>`

## Guardrails

- Preserve unrelated dirty worktree changes.
- Do not rewrite large XML sections when a narrow attribute edit is enough.
- Do not change strategy identity, target semantics, or production paths unless the request requires it.
- If the requested conversion conflicts with the linked script behavior, fix or flag the contract mismatch instead of forcing the XML through.
- For multi-phase scans, keep the user's existing JSON names and phase folder shape unless the user explicitly asks to rename or flatten them.
