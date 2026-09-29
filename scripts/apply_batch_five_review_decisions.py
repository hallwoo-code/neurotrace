"""Apply user decisions for manual-review batch five; retain one overlap audit."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TODAY=date.today().isoformat()
DECISIONS={
 'EC-IRH47UG6-A':('B','boundary'),'EC-JH5U3XYU-A':('A','conditional_support'),
 'EC-KGUAISW6-A':('A','conditional_support'),'EC-KMNAMCKJ-A':('B','boundary'),
 'EC-B5F5XG3T-A':('A','conditional_support')}
def main():
 p=ROOT/'evidence_cards.json'; d=json.loads(p.read_text(encoding='utf-8')); cards={x['evidence_id']:x for x in d['cards']}
 for eid,(decision,role) in DECISIONS.items():
  c=cards[eid]; c['status']='anchor_confirmed'; c['verification_flag']='human_confirmed'; c['human_review']={'reviewed_on':TODAY,'reviewer':'user','decision':decision,'assigned_evidence_role':role,'note':'用户人工复核确认；角色仅适用于所述任务、样本、比较和时间窗。'}
 cards['EC-KGUAISW6-A']['duplicate_independence']='needs_manual_check'
 cards['EC-KGUAISW6-A']['human_review']['note']+=' 与 EC-M256T5QC-A 的样本独立性仍待核。'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 vp=ROOT/'corpus_version.json'; v=json.loads(vp.read_text(encoding='utf-8')); v['human_anchor_confirmed']=sum(x['status']=='anchor_confirmed' for x in d['cards']); v['batch_five_manual_review']={'date':TODAY,'confirmed':5,'duplicate_independence_pending':['EC-KGUAISW6-A','EC-M256T5QC-A']}; vp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'updated':5,'confirmed':v['human_anchor_confirmed'],'duplicate_pending':True},ensure_ascii=False))
if __name__=='__main__': main()

