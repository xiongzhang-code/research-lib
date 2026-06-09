# opt-analyst QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/opt-analyst/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. VA 候选筛选：poscorr + optresult

Q_agent 认为 MCG 常问：`这批 nio 对 baseline 可能有 va 吗，结合 poscorr 和 optresult 挑一下`。

A_agent 回答：先解析候选 result 文件、匹配 XML/NIO 名；用 `niupos2025 basenio -l <显式 niopaths> -o 1024` 算候选和 baseline 的 position correlation；再以全周期 `OPT` 为主决策面，结合 `raw`、`neutBarraStyle`、`OPDEMEAN250`、cost、turnover、BarraStyleCNTR exposure 辅助筛选；最后给 `keep/revise/combine/rerun/skip`。`niupos2025 -l` 不能传裸目录，必须展开为具体 NIO 路径；不能只看 standalone OPT 就声称有 VA，必须结合 baseline/combo 证据。

### Q2. VA 结果复盘：combo vs baseline

Q_agent 认为 MCG 常问：`任务好像都跑完了，帮我分析一下 va`。

A_agent 回答：先确认 combo、baseline、candidate 的 result/XML/NIO 对应关系；先看 candidate 与 baseline 的 poscorr；再比较 combo result 相对 baseline 的 delta，主看全周期 `OPT`，辅看 raw/neut/OPDEMEAN250/cost/turnover/exposure。如果没有 combo result，只能说 standalone 表现，不能判定 VA；如果 baseline 不明确，必须先解析或要求明确。

### Q3. 批量 optresult 排名摘要

Q_agent 认为 MCG 常问：`帮我分析这个 result 目录，生成/看 summary，哪个最好`。

A_agent 回答：解析一批 result 文件和对应 XML/NIO；优先用 `optq-mcp.build_opt_summary` 或已有 `.summary` 文件；用全周期 `OPT` 排名，其他指标作为解释证据；输出候选排序和建议。result 文件名、NIO 名、XML 映射不清时，先 resolve，不直接排名；缺少 `.summary` 时可用 MCP 生成摘要。

### Q4. 多 snaptime result 平均比较

Q_agent 认为 MCG 常问：`100000/133000 这些时间点结果帮我做平均 summary，看稳定性`。

A_agent 回答：无法处理。当前 skill workflow 没有定义多 snaptime 聚合、平均口径、权重或跨 snaptime 对齐方法。

### Q5. baseline 切换后重新评估

Q_agent 认为 MCG 常问：`把 baseline 切换成这个 done.xml，现在重新测试这批对 baseline 的 va`。

A_agent 回答：把新 baseline 当作新的参照，重新解析 result/XML/NIO；重新计算候选相对新 baseline 的 poscorr；重新比较 combo vs 新 baseline 的 delta；再按 OPT 主指标和辅助证据给结论。旧 baseline 下的 VA 结论不能直接迁移；如果新 baseline 没有 result 或 NIO 路径，无法完成重新评估。

### Q6. 风险暴露对比

Q_agent 认为 MCG 常问：`加了最强 pnd10 之后组合风险暴露增加了吗`。

A_agent 回答：读取匹配 result 和 opt XML/config；查看 BarraStyleCNTR exposure，并结合 raw/neutBarraStyle/OPT 表现判断暴露变化对收益的影响。exposure 是辅助证据，不替代 OPT 主决策；如果缺少 BarraStyleCNTR 或相关 result，只能标为 `not measurable`。

### Q7. hard risk / BarraStyle 约束是否生效

Q_agent 认为 MCG 常问：`这个 nio 是否满足 rhs1 的 risklist，尤其 midcap 和 size`。

A_agent 回答：先读 opt XML/config；记录 hard/soft mode、bound、slack、risk delay、risklist、universe/group 等字段；做表格：配置约束、观测指标、result 文件、分类；分类为 `satisfied/violated/not measurable/likely not encoded as hard`。不能只凭结果数值判断，要先看 XML 是否真编码为 hard；没有可观测指标时标 `not measurable`。

### Q8. turnover / maxtvr 约束分析

Q_agent 认为 MCG 常问：`maxtvr=0.4 为什么带 risk 后换手爆炸，不带 risk 又正常`。

A_agent 回答：读 XML/config 中 TVR mode、bound、slack、`tvrboth`、`legstate` 等；再看 result 中 turnover/TVR 观测值；区分 net TVR 和 split-leg TVR；分类是否满足。maxtvr 如果没有在配置或结果中可定位，只能标 `not measurable`；不能混淆 net TVR 与分腿 TVR。

### Q9. risk 与 TVR 冲突定位

Q_agent 认为 MCG 常问：`为什么 risk 限制和 tvr 限制不能并存，事实上应该存在同时满足的解`。

A_agent 回答：可做证据级定位：同时读取 risk 和 TVR 配置，记录 hard/soft、bound、slack、risk delay、TVR mode；对观测 risk 指标和 turnover 指标分别分类，找出哪个约束 violated、哪个 slack/soft、哪个可能未 hard encode。

边界：如果要求精确 solver 内部冲突归因，当前 workflow 无法处理；skill 只能基于 XML/config/result 做约束证据定位。

### Q10. 缺失 neutBarra/OPT 子表现 result 的处理建议

Q_agent 认为 MCG 常问：`这个目录里缺少 neutBarra 表现的 result 对应 done.xml 要不要重丢 optq`。

A_agent 回答：先确认缺的是 `neutBarraStyle`、`OPT`、还是其他子表现；缺失项在表中标 `not measurable`；若缺全周期 `OPT`，不能做主决策，应建议 `rerun` 或 `skip`；若只缺 neutBarra/OPDEMEAN250，可保留 OPT 主结论但降低置信度，并建议补跑或补摘要。不能用 raw 或 standalone 结果替代缺失的 OPT 来声称 VA；辅助 result 缺失时只能作为证据不足处理。
