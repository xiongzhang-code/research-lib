# submission-checker QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/submission-checker/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. 生产提交转换

Q_agent 认为 MCG 常问：`把这个 ADMLQ / superrunOpt 结果转成 production submission`。

A_agent 回答：解析源实验 cfg/model/NIO 和目标生产路径，检查 cfg 身份、脚本、model paths、dumpName、SNAPTIME、命名要求；先跑 `submission-mcp.production_converter` dry-run，意图明确后再 `dry_run=false`。不能隐式上传或覆盖生产产物；保留源实验产物。

### Q2. 生产 cfg 校验

Q_agent 认为 MCG 常问：`帮我检查这个生产 XML 能不能提交`。

A_agent 回答：先生成 `generate_checkcfg`，再跑 `production_validate`。通过或只剩明确可解释 warning 才算完成；生产路径/模型路径不清时先停。

### Q3. cfgqueue XML 生产化检查

Q_agent 认为 MCG 常问：`这个 cfgqueue 生成的一批 XML 能不能上生产？`

A_agent 回答：如果 cfgqueue XML 已被解析成明确的生产 cfg/checkcfg 目标，可按 `generate_checkcfg` + `production_validate` 做校验。

无法处理：skill 没写 cfgqueue 批量/XML 队列专项规则。若要求完整 cfgqueue 生产化审计，当前 workflow 不足。

### Q4. runpysim 产物提交前路径校验

Q_agent 认为 MCG 常问：`这个 runpysim 结果路径对不对，能不能做 submission check？`

A_agent 回答：可检查源 cfg、linked script、model paths、dumpName、SNAPTIME、NIO 与目标生产路径是否明确，并通过 production validation 间接验证。

无法处理：skill 没写 runpysim 专项产物路径规则。若要求 runpysim 专用路径规范审计，当前 workflow 不足。

### Q5. hist/live NIO 对比

Q_agent 认为 MCG 常问：`帮我比一下 hist 和 live NIO 有没有断层`。

A_agent 回答：用 `compare_hist_live_nio`，必要时再用 `nio-mcp.checknio`。不能有 unexplained alignment break；有对齐异常必须明确解释或停下。

### Q6. 新生成 NIO 完整性检查

Q_agent 认为 MCG 常问：`这个新 NIO 提交前帮我 checknio 一下`。

A_agent 回答：当提交依赖新 NIO 时，用 `nio-mcp.checknio` 检查完整性。只有在 submission 依赖该 NIO 时是验收条件；若 NIO 来源或预期区间不明，需要先解析。

### Q7. 本地模型上传前验证

Q_agent 认为 MCG 常问：`这个 localmodel 能不能 upload？`

A_agent 回答：先完成转换和 `production_validate`，通过后才考虑 `upload_localmodel`；上传默认 dry-run。不能从隐式请求直接上传；不能覆盖生产产物。

### Q8. 生产提交命名规范检查

Q_agent 认为 MCG 常问：`这个 cfg/model 命名是不是 production 要求的？`

A_agent 回答：在转换前检查 source cfg identity、dumpName、SNAPTIME 和 required production naming。

无法处理：skill 没定义独立命名规范清单或专门命名检查器。若要求单独完整命名规范审计，当前 workflow 不足。

### Q9. 从 ADMLQ/diffsolver 结果判断是否能进入提交检查

Q_agent 认为 MCG 常问：`这个 diffsolver / ADMLQ 结果能不能走 SubmissionCheck？`

A_agent 回答：无法处理。submission-checker 没有 ADMLQ/diffsolver 队列判断 workflow。

### Q10. superrunOpt 输出转生产前检查

Q_agent 认为 MCG 常问：`superrunOpt 出来的这个 opt 结果帮我做 submission validation`。

A_agent 回答：如果 superrunOpt 输出已经给出明确 cfg/model/NIO 和目标生产路径，可按生产提交转换前检查：解析源产物、检查路径/命名/SNAPTIME，再 dry-run converter。

无法处理：skill 没写 superrunOpt 专项判断规则。若要求判断 superrunOpt/OPTQ 结果本身是否合格，当前 workflow 不足。

### Q11. 生产提交报告整理

Q_agent 认为 MCG 常问：`给我一份这个 submission check 的结果摘要`。

A_agent 回答：可把转换结果、checkcfg、production_validate、hist/live NIO 对比、checknio 结果整理为提交前证据；临时报告放 `/dat/workspace/xiongzhang/tmp`。

边界：skill 只给了临时报告位置和验收标准，没定义固定报告模板。能做基础整理；若要求特定格式模板，无法处理。

### Q12. 判断某请求是否不该用 submission-checker

Q_agent 认为 MCG 常问：`帮我看 ADMLQ 队列跑完没、diffsolver worker 正不正常`。

A_agent 回答：看请求是否属于转换实验产物到生产提交、生成 checkcfg、验证生产 cfg/model、hist/live NIO 对比、本地模型上传。ADMLQ/diffsolver 队列判断、cfgqueue 专项生产化审计、runpysim 专项路径规则、superrunOpt 结果合格性判断、独立命名规范审计，都不应只靠 submission-checker；这些按当前 workflow 无法处理。
