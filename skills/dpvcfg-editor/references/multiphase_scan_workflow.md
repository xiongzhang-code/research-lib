# Multi-Phase Scan Workflow

Use this reference when the user wants recommended parameters turned into root-level JSON plans plus generated phase XML directories, especially under:

- `/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue`
- existing strategy folders that already use `phase1`, `phase2`, and snaptime subdirectories

## Default contract

Preserve the current structure by default:

```text
<strategy-root>/
  <plan-phase1>.json
  <plan-phase2>.json
  phase1/
    100000/
    133000/
  phase2/
    100000/
    133000/
```

Preferred defaults for the current gpuf seqout case:

- `.../td5/dk_gpuf_seqout_td5_phase1.json`
- `.../td5/dk_gpuf_seqout_td5_phase2.json`
- `.../td5/phase1/100000/*.xml`
- `.../td5/phase1/133000/*.xml`
- `.../td5/phase2/100000/*.xml`
- `.../td5/phase2/133000/*.xml`

Do not invent a new layout if the strategy folder already follows this pattern.

## Naming pattern

Use root-level JSON plan files and phase-local XML directories:

- plan JSON lives at the strategy root, not inside `phaseN/<snaptime>`
- each plan targets one phase
- each phase keeps one subdirectory per snaptime

For the current example, use `dk_gpuf_seqout_td5_phase2.json` as the canonical phase2 plan name.

## JSON skeleton for `config_search.py`

Use a root-level plan JSON with:

- `base_config`
- `output_dir`
- `flat_output`
- `Modules.AlphaModule`
- `phases[].name`
- `phases[].display_params`
- `phases[].configs[]`

Minimal skeleton:

```json
{
  "plans": [
    {
      "base_config": "/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue/2026/04/24/dragonknight_nzo_td5_onetrain_cache_100000.xml",
      "output_dir": "dk_gpuf_seqout/phase2",
      "flat_output": true,
      "Modules": {
        "AlphaModule": {
          "id": "fselect01",
          "path": "/dat/usercache/xiongzhang/projects/versions/DynamicPV/v4.3.3/testmodule/nn20260323/fselect01_mlp01_v20260404_pnd_cache01_gpuf_seqout.py"
        }
      },
      "phases": [
        {
          "name": "phase2",
          "display_params": ["gpuf_modes", "predNdays"],
          "configs": [
            {"name": "gpuf_last_std_slope_pnd3", "gpuf_modes": "last,std,slope", "predNdays": "3"}
          ]
        }
      ]
    }
  ]
}
```

Notes:

- `output_dir` should stay phase-relative to the strategy root inside the JSON.
- When generating into a specific snaptime directory, prefer passing `--output-dir` on the command line.
- Keep config names concise and stable because they become XML filename suffixes and `Alpha id` suffixes.

## Default generation order

1. Inspect the strategy root, existing phase directories, and the nearest matching plan JSON.
2. Write or update the root-level phase JSON.
3. Generate `phaseN/100000` first.
4. If more snaptimes are needed, copy `100000` into the target snaptime directory.
5. Run `rename_dpvcfg.py` on the copied XMLs to retarget the snaptime and rename files.
6. Verify both filenames and internal `SNAPTIME` values.

## Default commands

Activate the default environment first:

```bash
source ~/venv_lgb/bin/activate
```

Generate XMLs from a root-level plan:

```bash
python3 /dat/usercache/xiongzhang/projects/DML_workspace/config_search.py <plan.json> --output-dir <phase>/<snaptime>
```

Replicate a seed snaptime directory:

```bash
cp -r <phase>/100000 <phase>/133000
```

Retarget copied XMLs:

```bash
python3 /dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue/2026/04/rename_dpvcfg.py <phase>/133000/*.xml --snaptime 133000
```

## Verification checklist

After generation, verify:

- the plan JSON is still at the strategy root
- generated XMLs are under `phaseN/<snaptime>`
- filenames end with the target snaptime
- `Macros SNAPTIME` inside copied XMLs matches the target snaptime
- the linked `Modules/AlphaModule id="fselect01"` path is still the intended script
- `display_params` in the JSON still match the intended scan dimensions

Useful checks:

```bash
find <strategy-root>/phase2/100000 -maxdepth 1 -type f | sort
find <strategy-root>/phase2/133000 -maxdepth 1 -type f | sort
grep -n 'SNAPTIME' <phase>/133000/<one-config>.xml
```

## Current worked example

Current canonical example:

```text
/dat/usercache/xiongzhang/projects/DML_workspace/cfgqueue/2026/04/24/dk_gpuf_seqout/td5/
  dk_gpuf_seqout_td5_phase1.json
  dk_gpuf_seqout_td5_phase2.json
  phase1/100000/*.xml
  phase1/133000/*.xml
  phase2/100000/*.xml
  phase2/133000/*.xml
```

For this example:

- phase JSONs stay at the `td5` root
- `phase2/100000` is generated first from `dk_gpuf_seqout_td5_phase2.json`
- `phase2/133000` is created by copying `phase2/100000`
- `rename_dpvcfg.py` is then used to retarget all copied XMLs to `133000`

## Operational defaults

- Use `~/venv_lgb/bin/activate` by default.
- Use `/dat/workspace/xiongzhang/tmp` for temporary files.
- Keep the workflow narrow and readable.
- Preserve existing JSON names and phase layout unless the user explicitly asks to restructure them.
