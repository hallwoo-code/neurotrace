# NeuroTrace 文献证据库修复方案

版本：v1.0  
日期：2026-09-28  
适用范围：Zotero 本地 ERP/EEG 文献库、候选证据卡、演示案例与金标评测  
当前阶段：从“候选发现库”修复为“可追溯、可人工核验、可用于 Demo 的冻结证据库”

## 实施状态（2026-09-28）

- 已完成：38 篇可读 PDF 冻结、PDF SHA-256、逐页短摘录机器匹配、`EvidenceCard` / `EvidenceRelation` 拆分、3 个 DemoCase、12 个 GoldCase 夹具，以及 5 篇缺 PDF 文献的扩展候选池。
- 已生成：`corpus_version.json`、`paper_records.json`、`evidence_schema_v2.json`、`evidence_relations.json`、`demo_cases.json`、`gold_cases.json` 与 `extended_candidates.csv`。
- 未完成且不可由自动处理替代：3 条 `anchor_confirmed` 人工锚点。所有当前卡片保持 `candidate`，自动定位但语义关联仍需确认的条目明确标作 `needs_manual_check`。

## 1. 修复结论

当前库已经完成首轮候选筛选和按页抽取，但尚未达到正式证据库验收条件。修复重点不是继续增加摘要数量，而是补齐以下闭环：

1. PDF 身份可验证：每篇论文有稳定文件标识和 SHA-256；
2. 原文锚点可复核：页码、章节和逐字摘录可以打开并匹配；
3. 事实与案件关系分离：论文观察结果不预先绑定为“支持/反证”，角色由具体问题决定；
4. 关键证据有人审：至少 3 条锚点达到 `anchor_confirmed`；
5. 演示问题可验收：3 条核心案例和 12 条金标案例具有预期判断、必找证据和不得漏掉的反证；
6. 语料可冻结：任何扩充产生新版本，不静默覆盖旧案件。

## 2. 当前基线与目标状态

| 项目 | 当前状态 | 修复目标 |
|---|---:|---:|
| 清单总数 | 40 | MVP 冻结 38–40 篇可读 PDF；扩展候选池独立维护 |
| 活跃条目 | 38 | 全部具有可读 PDF 或明确 `parse_failed/needs_manual_check` |
| 可读 PDF | 33 | 先补至 38，最多冻结 40 |
| 候选证据卡 | 38 | 核心文献每篇 2–4 张；普通文献至少 1 张 |
| 页码锚点 | 33 | 所有可用卡均有页码、章节和逐字原文 |
| PDF SHA-256 | 0 | 100% 覆盖冻结语料 |
| 人工确认锚点 | 0 | 首批至少 3 条；Demo 前建议 9–15 条 |
| 核心演示案例 | 只有报告描述 | 3 条结构化、可复跑案例 |
| 金标案例 | 0 | 12 条，含开发集与留出集 |
| 语料版本 | 无 | `CorpusVersion` 冻结并可追溯 |

## 3. 范围

### 3.1 本轮必须修复

- 冻结统一数据契约和证据角色枚举；
- 为 PDF 计算 SHA-256，并记录文件名、附件 key、解析状态；
- 修正非逐字摘录，增加章节和页码验证；
- 将 `EvidenceCard` 与 `EvidenceRelation` 拆分；
- 深化 8–12 篇核心文献的结果、条件和限制卡；
- 完成 3 条核心案例和至少 3 条人工确认锚点；
- 建立 12 条金标案例及最小评测记录；
- 补齐现有 5 篇缺 PDF 条目，或明确移出冻结语料；
- 形成新的冻结语料版本和修复验收报告。

### 3.2 本轮不做

- 不修改或清理 Zotero 原始条目；
- 不自动下载、联网补充论文；
- 不把未核验候选卡升级为正式引用；
- 不对 50–60 篇扩展池逐篇精审；
- 不进行完整统计功效、实验设计或科学真理裁决。

### 3.3 后续迭代

- 将扩展候选池增加到约 50–60 个去重题名；
- 增加语义检索、图表指针和自动页码跳转；
- 增加跨语料版本差异比较；
- 增加更多群体、模态和语言的平衡采样。

## 4. 核心产品决策

### 4.1 冻结一个统一枚举

证据关系统一使用以下五类：

- `direct_support`
- `conditional_support`
- `boundary`
- `counterevidence`
- `insufficient`

`PROJECT_MEMORY.md` 中旧的 `boundary_only`、`insufficient_evidence` 应在后续文档同步时改为上述枚举。读取旧数据时可做兼容映射，但新数据不得继续产生旧值。

### 4.2 证据卡与证据关系必须分离

当前 `evidence_cards.json` 把论文观察结果和“对某个问题的角色”放在同一对象中。角色实际上依赖具体问题，因此修复后：

- `EvidenceCard` 只保存论文事实、条件、原文锚点和解析状态；
- `EvidenceRelation` 连接某个案例、论断槽位和 EvidenceCard，并保存角色、理由和条件；
- 同一张卡可以在案例 A 中是 `direct_support`，在案例 B 中是 `boundary`。

### 4.3 数量分层

| 层级 | 规模 | 用途 | 人工要求 |
|---|---:|---|---|
| `demo_core` | 8–12 篇 | 现场演示和关键判断 | 关键锚点人工确认 |
| `mvp_corpus` | 38–40 篇可读 PDF | 本地召回、条件比对、反证检索 | 候选卡可机器抽取 |
| `extended_pool` | 约 50–60 篇 | 后续扩展和补充检索 | 只做去重与初筛 |

冻结语料只计算可读 PDF。缺 PDF 的记录可留在候选池，但不得计入“已入库 PDF 数”。

## 5. 目标数据模型

### 5.1 CorpusVersion

| 字段 | 必填 | 说明 |
|---|---|---|
| `corpus_version_id` | 是 | 例如 `neurotrace-corpus-2026-09-28-v2` |
| `created_at` | 是 | 冻结时间 |
| `paper_count` | 是 | 冻结且可读的 PDF 数量 |
| `manifest_sha256` | 是 | 清单文件哈希 |
| `extractor_version` | 是 | PDF 解析器/脚本版本 |
| `schema_version` | 是 | 数据契约版本 |
| `source_scope` | 是 | 允许的 Zotero 集合及子集合 |
| `previous_version_id` | 否 | 上一冻结版本 |
| `change_summary` | 是 | 新增、移除、修复和降级摘要 |

### 5.2 PaperRecord

| 字段 | 必填 | 说明 |
|---|---|---|
| `paper_id` | 是 | 版本内稳定 ID |
| `zotero_item_key` | 是 | Zotero 条目 ID |
| `bibtex_key` | 否 | BibTeX citation key；不得代替 item key |
| `attachment_key` | 是 | PDF 附件 key |
| `pdf_filename` | 是 | 本地 PDF 文件名 |
| `pdf_sha256` | 是 | 文件完整性校验 |
| `title/authors/year/venue/doi` | 是/条件必填 | 标准书目信息 |
| `population` | 否 | 研究群体概况 |
| `task_paradigm` | 否 | 任务/范式概况 |
| `erp_metrics` | 否 | N400、LPC、LPP、P600 等 |
| `parse_status` | 是 | `parsed/partial/failed/needs_manual_check` |
| `duplicate_family_id` | 否 | 同题、同 DOI 或疑似复用样本家族 |

### 5.3 EvidenceCard

| 字段 | 必填 | 说明 |
|---|---|---|
| `card_id` | 是 | 语料版本内唯一 ID |
| `paper_id` | 是 | 关联 PaperRecord |
| `pdf_sha256` | 是 | 必须与 PaperRecord 一致 |
| `page_number` | 是 | 1-based PDF 页码 |
| `printed_page_label` | 否 | 期刊印刷页码 |
| `section` | 是 | Abstract/Method/Results/Discussion 等 |
| `quote` | 是 | PDF 中逐字短摘录；不得重写 |
| `observed_finding` | 是 | 中文事实释义，不加入因果外推 |
| `study_conditions` | 是 | 群体、任务、材料、时间窗、ROI、条件比较、效应方向 |
| `limitations` | 是 | 关键边界或混淆 |
| `extraction_status` | 是 | `candidate/anchor_confirmed/decision_ready/rejected` |
| `verification_flag` | 是 | 页码、文字和哈希验证结果 |
| `parse_confidence` | 否 | 仅用于排序，不等于真值 |

### 5.4 EvidenceRelation

| 字段 | 必填 | 说明 |
|---|---|---|
| `relation_id` | 是 | 唯一 ID |
| `case_id` | 是 | 对应演示/金标/用户案件 |
| `card_id` | 是 | 对应 EvidenceCard |
| `claim_slot` | 是 | population/context/task/component/stage/direction 等 |
| `role` | 是 | 五类证据角色之一 |
| `conditions` | 是 | 角色成立所需条件 |
| `reason` | 是 | 可展示的简短归类理由 |
| `relation_status` | 是 | `candidate/confirmed/rejected` |

### 5.5 DemoCase / GoldCase

必须包含：

- 原始问题或假设；
- 槽位化论断；
- 预期 verdict；
- 必找关系；
- 不得漏掉的反证/边界；
- 当前证据判断；
- 允许的精炼假设；
- 人工锚点；
- 开发集/留出集标记。

## 6. 修复工作流

```text
Zotero 只读条目与附件
        ↓
标题 + DOI + 样本/材料家族去重
        ↓
生成 PaperRecord + PDF SHA-256
        ↓
逐页抽取 → 候选 EvidenceCard
        ↓
确定性检查：页码、逐字匹配、哈希、必填槽位
        ↓
人工核验关键锚点
        ↓
针对 Case 生成 EvidenceRelation
        ↓
综合判断、精炼假设与人工复核队列
        ↓
冻结 CorpusVersion + GoldCase + 验收报告
```

## 7. 分阶段修复任务

### P0-1：冻结数据契约

交付：`schema_v2.md` 或 JSON Schema。

- 统一证据角色枚举；
- 拆分 EvidenceCard 与 EvidenceRelation；
- 明确页码定义、空值规则和状态转换；
- 规定缺 PDF、解析失败和原文不匹配的降级逻辑；
- 将旧字段映射到新字段，保留兼容说明。

验收：任意卡片都能通过 Schema 校验；未知枚举或缺必填字段时必须失败。

### P0-2：建立 PDF 身份和语料版本

交付：`corpus_version.json`、修订后的 manifest。

- 为每个可读 PDF 计算 SHA-256；
- 增加 PDF 文件名、解析状态和语料版本；
- 对同题、同 DOI、疑似同样本论文分配 `duplicate_family_id`；
- 冻结 manifest，并计算 manifest 自身哈希。

验收：每张卡的 `pdf_sha256` 与 PaperRecord 一致；文件改变时卡片自动降级。

### P0-3：修复原文锚点

交付：修订后的 `evidence_cards.json`。

- 找出含方括号补词、省略重组或模型改写的 13 条摘录；
- 替换为连续、逐字、短摘录；
- 增加 `section`；
- 通过确定性文本匹配验证 quote 确实出现在指定 PDF 页；
- OCR 异常、表格或跨页摘录转 `needs_manual_check`。

验收：所有 `page_located` 卡的 quote 均能在指定页逐字匹配；否则不得保持可用状态。

### P0-4：人工确认首批锚点

交付：`human_verifications.jsonl`。

- 优先核验 Q1、Q2、Q3 中会改变结论的证据；
- 每条记录核验人、时间、动作、理由和核验时的 PDF 哈希；
- 至少 3 条升级到 `anchor_confirmed`；
- 被驳回卡进入 `rejected`，相关判断必须重新计算。

验收：3 个核心问题均至少有一个人工确认锚点；Demo 不读取未确认的关键结论作为正式依据。

### P0-5：建立 3 条核心演示案例

交付：`demo_cases.json`。

每题至少包含：

- 一条对“收缩后的具体论断”构成直接支持的关系；
- 一条条件或边界；
- 一条反证或不足证据；
- 当前 verdict；
- 不越过证据的精炼假设；
- 3–5 条人工核验卡，且总数不超过 8。

注意：如果原始宽泛问题没有直接支持，应将 verdict 设为 `insufficient/conditional`，并把直接支持限定到可成立的子论断，不能为了满足模板强行升级角色。

### P1-1：深化核心文献卡片

交付：核心文献每篇 2–4 张 EvidenceCard。

建议拆分为：

1. 主要结果卡；
2. 时间窗/ROI/条件卡；
3. 限制或替代解释卡；
4. 不显著结果或反证卡（如有）。

验收：8–12 篇核心文献的主要结论和关键限制不再依赖同一张摘要卡。

### P1-2：补齐 PDF 并平衡语料

优先补齐当前 5 篇缺 PDF 条目：

- `PML39LCM`
- `CNMC6QPE`
- `ACJAJ7ZB`
- `MTRD2WDW`
- `FETEEPSJ`

补齐后，当前活跃语料可达到 38 篇真实 PDF。若继续补到 40 篇，只选择能够改善以下不足的文献：

- 直接情绪/效价/唤醒度操纵；
- 情绪词或跨模态情绪 ERP；
- 儿童、老年、二语等群体边界；
- N400 阴性结果或 LPC/LPP 不一致结果。

不优先继续加入一般隐喻加工论文，因为当前语料已经偏重隐喻和 N400。

### P1-3：建立 12 条金标案例

交付：`gold_cases.json`、`benchmark_results.csv`。

- 覆盖直接支持、条件成立、反证、概念混淆、证据不足和格式异常；
- 至少保留 3–4 条作为留出集；
- 记录预期 verdict、关键卡、关键反证和允许表达；
- 跑一次端到端评测，记录 verdict、页码命中、反证检出和耗时。

验收：至少 10/12 条 verdict 正确；所有预设关键反证不得被放行为直接支持。

### P2：扩展候选池

当前去重后仍有约 49 个未进入清单的独立题名，其中启发式筛选约 24 个高相关、18 个已有 PDF。扩展时：

- 只进入 `extended_pool`，不直接覆盖冻结语料；
- 使用 DOI + 规范化标题 + 作者/年份 + 样本/材料复用四级去重；
- 为每个候选记录纳入/排除理由；
- 人工筛选后预计增加约 10–14 篇有价值文献；
- 形成新的 `CorpusVersion` 后，旧案件仍绑定旧版本。

## 8. 状态与降级规则

| 当前状态 | 允许操作 | 进入条件 | 禁止事项 |
|---|---|---|---|
| `candidate` | 展示、排序、请求核验 | 自动抽取完成 | 不得正式引用或自动放行 |
| `anchor_confirmed` | 用于核心案件判断 | 人工确认页码、逐字原文和角色关系 | PDF 哈希变化后继续使用 |
| `decision_ready` | 进入可导出 Casefile | 所有关键关系确认且无未处理反证 | 用户任意手动越过 Gate |
| `rejected` | 保留审计记录 | 原文不匹配、无关或抽取错误 | 重新参与判断 |
| `needs_manual_check` | 进入异常队列 | OCR、跨页、缺页、统计歧义 | 伪装为已定位证据 |

如果 PDF 哈希变化、页码打不开、quote 不匹配或必填槽位缺失，卡片必须降级到 `candidate` 或 `needs_manual_check`，相关案件进入 `review_required`。

## 9. 验收场景

### 场景 A：正常证据卡

- Given：PDF 可读，SHA-256 已登记；
- When：系统生成页码、章节和 quote；
- Then：quote 必须在该页逐字匹配，卡片状态为 `candidate`，并写入语料版本。

### 场景 B：模型改写原文

- Given：模型输出的 quote 含补词、重排或摘要化；
- When：确定性匹配失败；
- Then：卡片进入 `needs_manual_check`，不得进入正式 EvidenceRelation。

### 场景 C：关键反证存在

- Given：案件检索到已确认的 `counterevidence`；
- When：系统综合判断；
- Then：不得输出 `well_supported/citation_ready`，必须进入 `contested` 或条件化判断。

### 场景 D：PDF 被替换

- Given：附件 key 不变但 SHA-256 改变；
- When：核验组检查；
- Then：相关卡全部降级，旧案件保留旧版本快照，当前案件进入 `review_required`。

### 场景 E：扩充语料

- Given：新论文通过去重并有可读 PDF；
- When：进入扩展池或新冻结版本；
- Then：生成新 `CorpusVersion`，不得静默改变旧案件依赖的证据集合。

## 10. 两天执行顺序

### Day 1 上午：先修可信度

1. 冻结 Schema v2；
2. 计算 PDF 与 manifest 哈希；
3. 修复 13 条非严格逐字摘录；
4. 建立确定性页码/quote 匹配检查。

### Day 1 下午：先打通核心案例

1. 深化 8–12 篇核心文献；
2. 人工确认首批关键锚点；
3. 生成 3 条结构化 DemoCase；
4. 用一个案例跑通检索、关系判定、综合和重算。

### Day 2 上午：补齐语料与金标

1. 处理 5 篇缺 PDF；
2. 冻结 38–40 篇可读 PDF；
3. 建立 12 条金标；
4. 检查疑似样本/材料复用。

### Day 2 下午：验收与冻结

1. 跑 12 条评测；
2. 修复漏反证和错页码；
3. 冻结 CorpusVersion；
4. 生成验收报告、风险说明和 Demo 只读数据包。

## 11. 发布门槛

以下条件全部满足后，才可称为“符合 NeuroTrace 项目文献调研标准”：

- [ ] 冻结语料含 38–40 篇可读 PDF；
- [ ] 所有冻结 PDF 和 manifest 均有 SHA-256；
- [ ] 所有可用证据卡的页码、章节和逐字摘录通过确定性检查；
- [ ] 8–12 篇核心文献已深化为多张结果/边界卡；
- [ ] 至少 3 条关键锚点为 `anchor_confirmed`；
- [ ] 3 条核心演示案例可复跑，且包含支持、边界和反证/不足；
- [ ] 12 条金标案例中至少 10 条 verdict 正确；
- [ ] 所有预设关键反证均未被误放行为直接支持；
- [ ] EvidenceCard 与 EvidenceRelation 已分离；
- [ ] 证据角色和状态枚举在代码、数据与项目文档中一致；
- [ ] 语料版本、模型版本、Skill 版本和运行时间可追溯；
- [ ] 未完成功能均未被写成已完成事实。

## 12. 假设与待确认决策

### 已采用假设

- Zotero 继续作为只读书目与附件来源；
- 现有 3 个核心演示问题保持不变；
- 当前 5 篇缺 PDF 文献可以由用户后续补齐，系统不主动联网下载；
- 项目仍以 48 小时 MVP 为约束，不追求一次性精审全部扩展候选。

### 待确认

1. `mvp_corpus` 最终冻结 38 篇还是 40 篇；
2. 人工确认人是否只记录角色，还是还需记录姓名/标识；
3. 金标集采用 8 条开发 + 4 条留出，还是其他划分；
4. PDF 印刷页码是否作为必填，还是仅 PDF 页序必填；
5. 扩展候选池是否需要保留缺 PDF 条目。

这些决定不阻塞 P0 修复；未确认时按最保守规则执行：38 篇可读 PDF、匿名核验角色、8+4 划分、PDF 页序必填、缺 PDF 仅留在扩展候选池。

