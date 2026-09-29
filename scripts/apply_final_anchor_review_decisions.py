"""Apply the final nine core boundary-anchor decisions and materialize card roles."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TODAY=date.today().isoformat()
UPDATES={
 'EC-WRJA7MMA-A-B':('B','boundary',1,'Abstract','stimulus emotionality and task demand co-determine the extent to which emotion- and semantic-related neural resources are recruited during metaphor comprehension.'),
 'EC-8XBDTNCB-A-B':('A','conditional_support',10,'Discussion','Incongruent emotional words elicited robust N400 and LPC effects in both groups.'),
 'EC-FM494I2T-A-B':('B','boundary',3,'Introduction, 1.3 The current study','The current study leveraged the LPP to index emotional reactivity and regulation among an older adult sample.'),
 'EC-PFPR5ENP-A-B':('B','boundary',1,'Introduction','both the onset and duration vary with type of stimulus and task demands.'),
 'EC-9473VCG3-A-B':('B','boundary',4,'Review section: Complementary techniques to study emotion word processing','ERP research revealed inconsistent results in the field due to the employment of obsolete measurement systems, little control of the experimental material.'),
 'EC-ATKC5SQC-A-B':('B','boundary',1,'Abstract','the interaction between the more automatic and controlled processing of emotional stimuli.'),
 'EC-9PIPX6I5-A-B':('B','boundary',1,'Abstract','These findings highlight the need for further investigation, particularly regarding the LPC/P600 window.'),
 'EC-ZL2RBLSC-A-B':('A','conditional_support',1,'Abstract','after explaining the meanings of conventional metaphors, they elicited increased N400 and reduced LPC.'),
 'EC-8HE4L22P-A-B':('B','boundary',9,'Discussion: N400 characteristics','N400s thus are modality-dependent but not modality-specific.'),
}
def main():
 cp=ROOT/'evidence_cards.json'; doc=json.loads(cp.read_text(encoding='utf-8')); cards={x['evidence_id']:x for x in doc['cards']}
 for eid,(decision,role,page,section,quote) in UPDATES.items():
  c=cards[eid]; c['pdf_page']=page; c['section']=section; c['original_quote']=quote; c['status']='anchor_confirmed'; c['verification_flag']='human_confirmed'; c['machine_anchor']={'matched':True,'method':'user_selected_replacement_anchor','semantic_alignment':'human_confirmed'}; c['human_review']={'reviewed_on':TODAY,'reviewer':'user','decision':decision,'assigned_evidence_role':role,'note':'用户人工复核确认；角色仅适用于该原文所述的任务、样本、比较与时间窗。'}
 # Initial requirements ask for a card-level role/rationale. Keep relations too, but
 # materialize the reviewer-approved role so every card is self-contained.
 for c in doc['cards']:
  review=c.get('human_review',{}); role=review.get('assigned_evidence_role','insufficient')
  c['evidence_role']=role; c['role_rationale']=review.get('note','未获人审确认；不可作为最终主张依据。')
 cp.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
 vp=ROOT/'corpus_version.json'; v=json.loads(vp.read_text(encoding='utf-8')); v['human_anchor_confirmed']=sum(x['status']=='anchor_confirmed' for x in doc['cards']); v['human_rejected']=sum(x['status']=='rejected' for x in doc['cards']); v['final_anchor_review_update']={'date':TODAY,'updated_cards':len(UPDATES),'manual_anchor_review_status':'complete','card_level_roles_materialized':len(doc['cards'])}; vp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
 q='''# NeuroTrace 人工核验队列（v2，锚点审核完成）

## 已完成

- 48 张证据卡已完成首轮人工角色判断：47 张 `anchor_confirmed`，1 张 `rejected`。
- 三个 DemoCase 的 12 条核心关系均已有经人工确认的页码锚点。
- `M256T5QC` 与 `KGUAISW6` 已由用户确认可作为独立研究保留；综合时仍标注其主题与作者团队相近。

## 仍需人工或深度提取的收尾项

1. 为 `62IAIJLF`、`4YRMKG3I`、`UDGHLCIZ`、`8AVKRMIR` 补齐样本量、电极区、时间窗和条件比较；这些新增论文已有页码锚点与角色，但尚未完成完整方法/结果结构化。
2. 逐项补齐仍标为“未定位”的章节名与印刷页码；页码锚点已经存在，章节标签是最终可读性与人工回查的补充。
3. 对 12 个 GoldCase 运行一次评测并写入实际结果；当前仅有夹具定义。
4. 冻结最终 manifest：`XCECFFQ4` 已人审排除，需补入或正式不计入一篇替代候选，以保持修复方案的 38 篇冻结目标（原始 30–40 篇目标下，37 篇仍在范围内）。
'''
 (ROOT/'manual_review_queue.md').write_text(q,encoding='utf-8')
 print(json.dumps({'confirmed':v['human_anchor_confirmed'],'rejected':v['human_rejected'],'roles_materialized':len(doc['cards'])},ensure_ascii=False))
if __name__=='__main__': main()

