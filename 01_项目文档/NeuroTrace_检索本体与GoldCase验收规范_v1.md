# NeuroTrace 检索本体与 GoldCase 验收规范

**版本：** v1.0  
**日期：** 2026-09-29  
**对应步骤：** PRD 修复实施方案第 5–6 步。  
**配套文件：** `02_数据与证据/retrieval_profile_v1.json`、`02_数据与证据/gold_cases_runtime_v1.json`。

## 1. 交付结论

- 已定义中英双语检索本体、10 个案件槽位、概念混淆关系、澄清触发条件和本地混合检索约束。
- 已新增 12 条“完整案件”GoldCase；它们不同于旧 `gold_cases.json` 的单卡关系夹具。
- GoldCase 划分为 8 条 development、4 条 holdout，覆盖条件支持、条件遗漏、反证、相邻概念、证据不足、格式异常和越权输入。
- 当前语料没有 `direct_support` 卡，因此“直接支持”类别明确标为语料覆盖缺口；不得伪造此类金标或声称该类别已通过。

## 2. 检索与判断规则

1. 只能从 `runtime_corpus_contract_v1.json` 规定的 47 张可用本地卡中召回；拒绝卡仅可在审计/人工复审场景显示。
2. 默认返回 8–15 张候选卡，排序应综合别名词、槽位匹配、语义相似度、锚点状态与反证优先级。
3. 发现高相关 `counterevidence` 时，必须单独展示并阻止无条件正向结论。
4. 情绪、唤醒度、效价、情绪共鸣和情绪调节是相邻但不可自动等同的概念；触发澄清时最多提问两项并说明原因。
5. N400、LPC/LPP/P600 与晚期负波不能因都属于 ERP 晚期/语义成分而自动合并。
6. 模型输出只可生成 EvidenceRelation、理由与条件；哈希、页码、状态和 Casefile 资格由确定性 Gate 决定。

## 3. GoldCase 验收口径

| 层级 | 当前可验证内容 | 不可宣称内容 |
|---|---|---|
| 结构验收 | 12 条案例字段完整、卡 ID 存在、卡状态合格、development/holdout 划分正确 | 模型检索/判断已正确 |
| 检索回归 | 实现后每案召回 `must_retrieve_evidence_ids`，并单独呈现规定角色 | 仅命中标题即代表科学结论正确 |
| 模型评测 | 实现后比较预期 verdict、必现反证、澄清和安全拒绝行为 | 旧 fixture consistency 是模型性能 |
| PRD 完整金标 | 未来新增人工确认的 `direct_support` 卡后，补足直接支持类别 | 当前语料已覆盖直接支持 |

## 4. 必须达到的实现后指标

- 12 / 12 GoldCase 的输入、预期 verdict、允许表述和必召回卡均能被评测器读取。
- 8 / 8 development 与 4 / 4 holdout 划分固定；调参不得使用 holdout 的预期输出。
- 每个反证案必须召回并展示至少一张 `counterevidence` 卡；若遗漏，计入严重误放行风险。
- `GCR-11` 必须进入 `clarification_needed`，不能直接生成科研结论。
- `GCR-12` 必须拒绝联网/系统文件请求，且不调用外部检索。
- 当前直接支持覆盖率报告为 `0 / 1 required category`，属于数据缺口，不能标记为通过。

## 5. 代码负责人调用顺序

```text
load runtime_corpus_contract_v1.json
  → load retrieval_profile_v1.json
  → load gold_cases_runtime_v1.json
  → parse_claim_slots()
  → retrieve_evidence()
  → compare_conditions() + seek_counterevidence()
  → evaluate GoldCase assertions
```

实现后，输出必须包含每案的候选卡 ID、命中卡 ID、反证命中、预测 verdict、最终状态、步骤时延和错误；不得只输出“12/12 通过”。
