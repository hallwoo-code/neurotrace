# NeuroTrace EvidenceCard 审核冻结记录

**审核日期：** 2026-09-29  
**对应实施步骤：** `NeuroTrace_PRD_v2.0_修复实施方案.md` 第 2 步“接入冻结语料”之前的 EvidenceCard 审核与冻结确认。  
**数据来源：** `02_数据与证据/evidence_cards.json`、`paper_records.json`、`evidence_schema_v2.json`、当前 Zotero 原始 PDF。  
**审核性质：** 只读核验；未修改 Zotero 条目、PDF、EvidenceCard 或语料版本。

## 1. 审核结论

| 检查项 | 结果 |
|---|---:|
| EvidenceCard 总数 / 唯一 ID | 48 / 48 |
| 对应的 Zotero 原始 PDF 哈希已复核 | 38 / 38 |
| 指定 PDF 页与原文摘录实时匹配 | 48 / 48 |
| 必填字段、论文映射、附件 key 与哈希映射有效 | 48 / 48 |
| 摘录完整性为完整句/完整列表项 | 48 / 48 |
| 可冻结为正式锚点（`anchor_confirmed`） | 47 / 48 |
| 保留人工拒绝记录 | 1 / 48 |

### 角色分布

| 角色 | 数量 |
|---|---:|
| `conditional_support` | 22 |
| `boundary` | 22 |
| `counterevidence` | 3 |
| `insufficient` | 1 |
| `direct_support` | 0 |

**冻结结论：** 47 张已人工确认的卡可以作为后续运行时的可核验候选证据；语料中没有 `direct_support`，因此任何产品结论只能使用条件化、边界或反证性表达，不能声称普适直接支持。

## 2. 唯一拒绝记录

| EvidenceCard | Paper / Zotero key | 当前状态 | 处理规则 |
|---|---|---|---|
| `EC-XCECFFQ4-A` | `NT-XCECFFQ4` / `XCECFFQ4` | `rejected`、`human_rejected` | 保留审计记录与原始 PDF；默认不得进入正式检索、综合、`citation_ready` 或导出依据。仅在人工复审后才可能恢复。 |

该卡的拒绝不是 PDF 缺失或摘录无法定位：其 PDF、哈希、页码和原文仍能复现。拒绝状态必须由运行时 Gate 优先处理，不能被“文本匹配成功”自动覆盖。

## 3. 运行时接入规则

1. 运行时应加载 `corpus_version.json` 与 `paper_records.json`，将当前语料版本固定为 `neurotrace-corpus-2026-09-28-v2.3`。
2. 默认检索集合只纳入状态为 `anchor_confirmed` / `human_anchor_confirmed` 的 47 张卡。
3. `EC-XCECFFQ4-A` 仅在审计视图或人工复审队列中展示，不参与自动综合。
4. 每次案件建立时保存 EvidenceCard、PDF SHA-256 和语料版本快照；文献更新后不得回写旧案件。
5. 每次正式导出前，对所用卡重新核验 PDF 哈希、页码范围和原文摘录；任一失败即降级至 `review_required`。

## 4. 交接给代码负责人的文件

- `02_数据与证据/corpus_version.json`
- `02_数据与证据/paper_records.json`
- `02_数据与证据/evidence_cards.json`
- `02_数据与证据/evidence_schema_v2.json`
- `02_数据与证据/evidence_relations.json`
- 已按 `attachment_key` 保存、并通过 SHA-256 验证的 38 份只读 PDF。
- `01_项目文档/NeuroTrace_文献原件核验与交接清单_20260929.md`
- 本文件。

代码接入验收应输出：48 张卡的总数、47 张可用卡、1 张拒绝卡、角色分布，以及任何哈希/页码/摘录校验失败的卡 ID。

## 5. 验证脚本说明

现有 `scripts/validate_final_release.py` 的逻辑与本次审核规则一致，但脚本将数据根目录假定为项目根目录；当前工作区将发布数据放在 `02_数据与证据/`，因此直接从项目根运行会报找不到 `evidence_cards.json`。

这属于脚本路径假设与当前目录结构不一致，**不是**证据卡或 PDF 数据失败。代码负责人应在接入时为验证器增加明确的 `--data-root` 参数，或将数据根目录作为配置传入；不得通过复制同名文件到项目根目录规避问题。

