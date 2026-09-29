# NeuroTrace 文献原件核验与跨电脑交接清单

**核验日期：** 2026-09-29  
**目的：** 完成 PRD v2.0 修复路线的第一步：确认冻结语料的 Zotero 原始 PDF 可用，并提供不在同一电脑操作时的文件移交清单。  
**核验方式：** 通过 Zotero 本地 API 逐条读取 `paper_records.json` 中的 `zotero_item_key` 与 `attachment_key`；检查附件文件存在，并逐一计算 SHA-256 与冻结记录比对。未修改 Zotero 条目、附件或 PDF。

## 1. 核验结论

| 项目 | 结果 |
|---|---:|
| `paper_records.json` 中的预期论文记录 | 38 |
| 预期 Zotero PDF 附件 | 38 |
| 已定位的本地原始 PDF | 38 / 38 |
| SHA-256 与冻结记录一致 | 38 / 38 |
| 缺失附件 | 0 |
| 哈希不一致附件 | 0 |

**结论：** 所有预期原件均已存在于当前电脑的 Zotero storage，未触发“到 Zotero 查找替代附件”的补救分支。

## 2. 当前来源与使用规则

- 当前 Zotero 原件按其附件 key 位于类似路径：`C:\Users\24467\Zotero\storage\<attachment_key>\<filename>.pdf`。
- 单条论文与附件的权威映射位于 `02_数据与证据/paper_records.json`：`zotero_item_key` 是文献条目 ID，`attachment_key` 是 PDF 附件 ID，两者不可混用。
- PDF 哈希、页数、文件名和可读性字段同样以 `paper_records.json` 为准；不要以文件名推断记录身份。
- `XCECFFQ4` 在历史文献筛选中为人工排除记录；其 PDF 仍应随审计交接包保留，但运行时默认检索范围须依照 `corpus_version.json` 的活动库定义。
- 移交副本必须只读使用；不得覆盖、重命名原 Zotero 附件，也不得通过新文件静默替换同一 `attachment_key` 的 PDF。

## 3. 跨电脑交接包清单

接收方应获得下列内容，并保持目录内相对关系。PDF 可放在独立的只读目录；**不得**把个人 Zotero storage 路径写死进应用代码。

### A. 必交证据与版本文件

- [ ] `02_数据与证据/corpus_version.json`
- [ ] `02_数据与证据/corpus_manifest.csv`
- [ ] `02_数据与证据/paper_records.json`
- [ ] `02_数据与证据/evidence_cards.json`
- [ ] `02_数据与证据/evidence_relations.json`
- [ ] `02_数据与证据/gold_cases.json`
- [ ] `02_数据与证据/gold_case_evaluation.json`
- [ ] `01_项目文档/final_release_audit.md`

### B. 必交 PDF 原件

- [ ] 与 `paper_records.json` 的 38 个 `attachment_key` 一一对应的 38 份 PDF 原件。
- [ ] 每份 PDF 保留原始字节内容；接收方不得重新“打印为 PDF”、压缩、OCR 覆盖或改写元数据。
- [ ] 每份 PDF 旁保留其 `attachment_key`；推荐结构：`pdfs/<attachment_key>/<原始文件名>.pdf`。
- [ ] 若交接渠道不支持目录结构，另附一个 `attachment_key → 相对 PDF 路径` 的映射表；该表可从 `paper_records.json` 生成。

### C. 实施与验收依据

- [ ] `01_项目文档/NeuroTrace_PRD_v2.0.md`
- [ ] `01_项目文档/NeuroTrace_PRD_v2.0_修复实施方案.md`
- [ ] 本文件 `NeuroTrace_文献原件核验与交接清单_20260929.md`

## 4. 接收方验收步骤

1. 读取 `paper_records.json`，确认记录数为 38。
2. 对每条记录，按 `attachment_key` 在交接 PDF 目录定位唯一文件。
3. 计算 PDF 的 SHA-256，并与 `pdf_sha256` 完全比对；任何不一致均标记为 `hash_mismatch`，不得进入正式证据链。
4. 用 PDF 解析器验证文件可读、页数与 `pdf_page_count` 一致；不支持 OCR 的扫描件须按 PRD 降级。
5. 加载 `corpus_version.json`，确认活动语料范围、排除记录和版本号；不得只凭目录中存在 PDF 就自动加入运行时检索。
6. 随机抽取至少 5 张 `evidence_cards.json` 卡，确认其 `paper_id`、页码和原文摘录可在交接 PDF 中复现。
7. 验收完成后，生成接收方自己的“路径映射清单”；该清单只记录部署目录相对路径，不记录个人电脑的用户目录。

## 5. 交接完成判定

下列条件同时满足，才可将该证据包交给代码负责人接入运行时：

- 38 / 38 PDF 可定位；
- 38 / 38 SHA-256 匹配；
- 语料版本与记录文件完整；
- 活动库与排除项明确；
- 接收方已完成路径映射，且应用只读取其部署侧只读目录；
- 至少 5 张证据卡完成页码与原文抽检。

若任一项失败，运行时只能将相关证据标为不可用或 `review_required`，不得改用样例卡冒充正式证据。

