"""Print compact source-layout context for cards missing section/page labels."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def compact(lines): return [re.sub(r'\s+',' ',x).strip() for x in lines if re.sub(r'\s+',' ',x).strip()]
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 cards=json.loads((ROOT/'evidence_cards.json').read_text(encoding='utf-8'))['cards']
 requested=set(sys.argv[1:])
 selected=[x for x in cards if x.get('section_locator_status')=='not_located']
 if requested:
  selected=[x for x in selected if x['evidence_id'] in requested or x['zotero_item_key'] in requested]
 for c in selected:
  pages=json.loads((ROOT/'.neurotrace_work'/'pages'/f"{c['zotero_item_key']}.json").read_text(encoding='utf-8'))
  text=next(x['text'] for x in pages if x['pdf_page']==c['pdf_page']); lines=compact(text.splitlines())
  seed=' '.join(c['original_quote'].split()[:4]); pos=next((i for i,x in enumerate(lines) if seed.lower() in x.lower()),-1)
  around=lines[max(0,pos-5):pos+7] if pos>=0 else []
  print(json.dumps({'id':c['evidence_id'],'pdf_page':c['pdf_page'],'head':lines[:7],'around':around,'tail':lines[-7:]},ensure_ascii=False))
if __name__=='__main__': main()

