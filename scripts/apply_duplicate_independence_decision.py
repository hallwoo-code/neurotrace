"""Record the user's independence decision for the two scientific-metaphor studies."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TODAY=date.today().isoformat()
def main():
 p=ROOT/'paper_records.json'; d=json.loads(p.read_text(encoding='utf-8'))
 for x in d['papers']:
  if x['zotero_item_key'] in {'M256T5QC','KGUAISW6'}:
   x['duplicate_family']='related_topic_independent_study_user_confirmed'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 cp=ROOT/'evidence_cards.json'; cd=json.loads(cp.read_text(encoding='utf-8')); cards={x['evidence_id']:x for x in cd['cards']}
 for eid in ('EC-M256T5QC-A','EC-KGUAISW6-A'):
  cards[eid]['duplicate_independence']='independent_user_confirmed'; cards[eid].setdefault('human_review',{})['duplicate_independence_review']={'reviewed_on':TODAY,'reviewer':'user','decision':'I','note':'用户确认：两篇研究独立；综合时保留主题/团队相近说明。'}
 cp.write_text(json.dumps(cd,ensure_ascii=False,indent=2),encoding='utf-8')
 vp=ROOT/'corpus_version.json'; v=json.loads(vp.read_text(encoding='utf-8')); v['duplicate_independence_update']={'date':TODAY,'papers':['M256T5QC','KGUAISW6'],'decision':'independent_user_confirmed'}; vp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(v['duplicate_independence_update'],ensure_ascii=False))
if __name__=='__main__': main()

