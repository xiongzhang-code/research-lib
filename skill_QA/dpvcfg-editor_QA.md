# dpvcfg-editor QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/dpvcfg-editor/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. onetrain config 转 freq30/frequent training

Q_agent 认为 MCG 常问：`这是freq30模板，帮我把这个onetrain config转化成freq30的dpvcfg`。关键词包括 `freq=30`、`modelDecayNum=2`、`di_delay=9`。

A_agent 回答：先读 XML，识别 `Port/Alpha`、`Modules/AlphaModule`、`OpNio2`、`Macros.SNAPTIME`、datacfg、脚本路径；如果改到脚本相关属性，先读 Python 脚本。按 frequent training 默认值改成 `freq=30`、`modelDecayNum=2`、`di_delay=9`。只改 cadence/runtime/mode 等必要项；改后重开 XML，并按需跑 compare、check_datacfg、test_livehist 或生成 smoke test。不能整块盲抄模板；遇到半转换文件要逐项 reconcile；不能改动策略身份、目标语义、universe、production path 等无关内容。

### Q2. freq30 config 改 onetrain

Q_agent 认为 MCG 常问：`把这个fq30改成onetrain跑一版`。关键词包括 `freq=99999`、`di_delay`、`modelDecayNum=1`、`modeldir/featuresidxdir/modelparamdir`。

A_agent 回答：skill 描述支持 onetrain/freq-train variants 转换；按 core workflow 读 XML、识别关键节点、检查脚本契约，然后把 cadence、decay、mode flags 等改回 onetrain 形态并验证。

无法处理：`SKILL.md` 只明确给了 onetrain -> frequent 的默认值，没有给 freq30 -> onetrain 的固定默认参数。如果没有已有 onetrain 模板、目标 onetrain 参数，或用户没有明确要恢复哪些字段，就无法可靠处理。

### Q3. 按 base/template 生成一批新 XML

Q_agent 认为 MCG 常问：`以xxx.xml为base，生成开关开和闭的样例，放到cfgqueue/...`。

A_agent 回答：先读 base/template XML，识别关键节点和路径；用结构化 XML 方式复制/改参数；只改请求区域，比如 loss/model knobs、路径 wiring、module linkage、output naming。生成后重开 XML 做检查，必要时跑 config generation smoke test。不能盲目复制大段模板；不能意外改策略语义、universe、production 路径；命名和输出目录要避免撞车。

### Q4. 生成多 phase / 多参数搜索 cfgqueue XML 批次

Q_agent 认为 MCG 常问：`生成phase1/phase2的xml`、`参数搜索方案生成一批xml`。关键词包括 `config_search.py`、`*.json`、`phase1/100000`、`phase2/133000`。

A_agent 回答：先读 plan JSON，或从现有 `phase*/<snaptime>/` 推断结构；默认保留 root plan JSON 加 phase 目录布局；用 `config_search.py` 生成 seed snaptime XML；其他 snaptime 用已有 rename tooling retarget；保持命名稳定。用户未要求时不 flatten、不改名；现有 phase 布局和 plan JSON 冲突时，先按实际文件核对。

### Q5. 100000 snaptime 目录复制/改名成 133000 等时间点

Q_agent 认为 MCG 常问：`把这个文件夹下.xml命名中100000都替换成133000`。

A_agent 回答：只有在 cfgqueue 多 phase 场景中，skill 明确提到“用已有 rename tooling retarget additional snaptimes”；因此应先找现有 rename 工具，再用它改 snaptime 相关 XML/目录。不能只做文件夹重命名而不改 XML 内部 `Macros.SNAPTIME`、路径、输出名等。

无法处理：如果没有已有 rename tooling，且任务要求纯目录复制/重命名规则，当前 workflow 没有完整规定。

### Q6. 检查/修正 XML 和 fselect01 脚本是否对齐

Q_agent 认为 MCG 常问：`常见的需要改两个地方 Modules/AlphaModule id=fselect01，另外一个是 Port/Alpha`。

A_agent 回答：读 XML，定位 linked script path、AlphaModule、OpNio2、SNAPTIME、datacfg；若 script-facing attributes 变化，必须读对应 Python 脚本；核对 XML 参数、路径、模块名、脚本读取字段是否一致；修正后重开 XML 验证。只修 XML/script contract 相关字段，不顺手重构脚本或大改策略逻辑。

### Q7. 训练脚本/配置改 production 可跑版本

Q_agent 认为 MCG 常问：`把训练脚本转换成production的版本`。

A_agent 回答：读 XML 和脚本，识别 production path、mode flags、runtime/cadence、datacfg、输出路径；只改生产运行必要项；保留策略身份和目标语义；验证可用性。只有在任务目标就是 production 化时，才可改 production wiring。

无法处理：如果没有说明 production 环境目标、路径、运行模式，无法凭空判断“production 可跑版本”。

### Q8. 给新脚本生成可运行测试 XML 并提交

Q_agent 认为 MCG 常问：`改完用xxx.xml作为模板改一个可运行的.xml，用superrunOpt.py -q semi提交`。

A_agent 回答：可生成测试 XML：读脚本契约，构造 linked AlphaModule/XML，设置 datacfg、SNAPTIME、OpNio2、输出名，做 smoke test。如果在 git repo 内，编辑前 checkpoint、验证后 commit；临时文件放 `/dat/workspace/xiongzhang/tmp`。

无法处理：本次 QA 任务要求不改文件，所以不能实际生成或提交。实际执行时再按 checkpoint/commit 流程处理。

### Q9. 检查 datacfg/snaptime 数据配置是否匹配

Q_agent 认为 MCG 常问：`check_datacfg一下这个datacfg多个snaptime`。

A_agent 回答：读 XML，识别 `Macros.SNAPTIME` 和 datacfg；运行或调用 `check_datacfg`；必要时核对 snaptime 目录布局。只检查/修正数据配置匹配关系，不改模型参数或策略逻辑。

### Q10. 在 XML 里加/改 OpNio2 dump

Q_agent 认为 MCG 常问：`可以采用OpNio2先dumpnio文件再测试风险暴露`。

A_agent 回答：读 XML，定位 `OpNio2`；按请求修改 dump 相关配置、路径或命名；重开 XML 验证结构，必要时 compare。只改 OpNio2/output naming 相关字段，避免影响 Alpha、universe、loss、训练 cadence。

### Q11. 围绕 risk/tvr/univ/group 限制生成实验 XML 变体

Q_agent 认为 MCG 常问：`以v0*.xml为base，生成带不带risk限制的xml，放到cfgqueue/.../tvrtest`。

A_agent 回答：从 base/template 读入，限定修改 risk、tvr、univ、group 相关参数，批量生成变体，保持命名稳定并做 smoke test。不要改无关模块；输出目录和命名要避免撞车；如果是多 phase 搜索，按 plan JSON 和 phase 布局生成。

无法处理：如果没有 base XML/template、参数网格或目标限制字段位置，无法可靠生成。

### Q12. 校对已有 dpvcfg 是否跑错目录、撞输出、残留旧 flag

Q_agent 认为 MCG 常问：`帮我review/检查这个dpvcfg有没有问题`。

A_agent 回答：读 XML，识别 script path、datacfg、SNAPTIME、output naming、mode flags、production/runtime path；检查路径 wiring、输出名冲突、旧 flag；按需用 compare、check_datacfg 或 smoke test 验证。这是 review/check 类任务；可以指出问题并做窄修，但不能借机重写大段 XML 或改策略语义。
