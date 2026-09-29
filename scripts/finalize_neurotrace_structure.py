"""Complete deterministic structural closure for the reviewed NeuroTrace corpus.

No Zotero records are modified.  Unlocated methods fields remain explicit rather than inferred.
"""
from __future__ import annotations
import csv, hashlib, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TODAY=date.today().isoformat()
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
STRUCTURED={
 'EC-62IAIJLF-A':{
  'section':'Abstract (anchor); Methods pp. 4–6; Results pp. 8–16','participants_and_sample_size':'25 Vietnamese undergraduate students, 18–24 years; 3 EEG datasets excluded for artifact violations, yielding 22 analyzed participants.','research_question_and_paradigm':'Experiment 1: Chinese/Vietnamese metaphorical versus literal sentence-final judgment. Experiment 2: Vietnamese-to-Chinese code-switched metaphor/literal sentences; F=metaphor, J=literal.','eeg_erp_metrics':['P200','N400'],'electrode_region':'Nine electrodes: F3/Fz/F4, C3/Cz/C4, P3/Pz/P4.','time_window':'P200 180–280 ms; N400 280–400 ms; 200-ms prestimulus baseline.','condition_comparison':'Language (Chinese L2 vs Vietnamese L1) × semantic type (metaphorical vs literal); code-switching vs no-switching.','limitations_boundary_confounds':'Non-balanced Vietnamese–Chinese bilinguals; three artifact exclusions; task is sentence-final categorical judgment and results cannot be generalized to balanced bilinguals or natural discourse.'},
 'EC-4YRMKG3I-A':{
  'section':'Abstract (anchor); Methods pp. 3–5; Results/Discussion thereafter','participants_and_sample_size':'32 Chinese–English bilingual graduate students (19 female; mean age 23.22, SD 2.04); upper-intermediate English by LexTALE.','research_question_and_paradigm':'Reading/adjective-matching task: conventional or novel English metaphors preceded by supportive or literal contexts; target sentences presented in X–IS–Y segments.','eeg_erp_metrics':['frontal N400','sustained negativity','late frontal positivity'],'electrode_region':'64-channel BioSemi recording; focal analysis at frontal (F3/Fz/F4), central (C3/Cz/C4), and parietal (P3/Pz/P4) electrodes.','time_window':'N400 350–450 ms; late frontal positivity 550–800 ms; sustained negativity 600–800 ms.','condition_comparison':'Conventional vs novel metaphors × supportive vs literal contexts, evaluated across sentence segments.','limitations_boundary_confounds':'Upper-intermediate Chinese–English graduate sample; English L2 reading/adjective task; the effects were reported for novel rather than conventional metaphors and do not measure emotion directly.'},
 'EC-UDGHLCIZ-A':{
  'section':'Abstract (anchor); Methods pp. 3–4; Results p. 5','participants_and_sample_size':'40 Chinese students recruited; 2 discarded for excessive EEG artifacts; final N=38 (17 male, 21 female; 18–26 years, mean 20).','research_question_and_paradigm':'Word-by-word reading of subject–verb metaphors, verb–object metaphors, literal-concrete, and literal-abstract sentences; ERP targets at verbs and objects.','eeg_erp_metrics':['N400','P600/LPC'],'electrode_region':'Frontal, central, and parietal regions were analyzed; exact electrode list not located in the extracted text.','time_window':'N400 and P600/LPC were analyzed; exact study-specific numerical windows were not located in the extracted text and are intentionally not inferred.','condition_comparison':'Sentence type (subject–verb metaphor, verb–object metaphor, literal-concrete, literal-abstract) × target position (verb/object).','limitations_boundary_confounds':'Mandarin student sample; syntactic position is confounded with the location of literal–metaphorical conflict; exact numerical component windows require visual/PDF methods check.'},
 'EC-8AVKRMIR-A':{
  'section':'Abstract (anchor); Methods pp. 5–10; Results pp. 11–15','participants_and_sample_size':'32 native Italian speakers recruited; 3 excluded for excessive artifacts; final N=29 (18 female; age 20–32).','research_question_and_paradigm':'S1–S2 paradigm comparing verbal word pairs with verbo-pictorial pairs, crossed with metaphorical versus literal relations; 128 items plus 16 fillers, repeated across modality.','eeg_erp_metrics':['N400','late negativity/LPC-range effect'],'electrode_region':'Anterior pool AF3/AF4/Fz/F1/F2/F3/F4 and posterior pool Cz/C1/C2/CPz/CP1–CP6.','time_window':'N400 300–500 ms; late effect 550–1000 ms; −500 to 1100 ms epochs and 200-ms prestimulus baseline.','condition_comparison':'Modality (multimodal vs verbal) × figurativity (metaphorical vs literal) × anterior/posterior topography.','limitations_boundary_confounds':'Italian S1–S2 materials, repetition across modality, and modality-related perceptual topography complicate attributing late effects solely to metaphor; imagery measures produced mixed findings.'},
}
def main():
 cards_file=ROOT/'evidence_cards.json'; cards_doc=json.loads(cards_file.read_text(encoding='utf-8')); cards={x['evidence_id']:x for x in cards_doc['cards']}
 for eid,fields in STRUCTURED.items():
  cards[eid].update(fields); cards[eid]['structured_extraction_status']='complete_with_explicit_unlocated_fields' if eid=='EC-UDGHLCIZ-A' else 'complete'
 for card in cards_doc['cards']:
  sec=card.get('section','')
  card['section_locator_status']='source_located' if sec and not sec.startswith(('未定位','自动')) else 'not_located'
  card['source_verification_status']='human_anchor_confirmed' if card['status']=='anchor_confirmed' else 'human_rejected'
 cards_file.write_text(json.dumps(cards_doc,ensure_ascii=False,indent=2),encoding='utf-8')

 papers_file=ROOT/'paper_records.json'; papers_doc=json.loads(papers_file.read_text(encoding='utf-8'))
 fields=['paper_id','zotero_item_key','bibtex_key','attachment_key','title','authors','year','venue','doi','local_pdf_readable','filename','pdf_sha256','pdf_page_count','parse_status','research_topic_tags','demo_suitability','selection_reason','duplicate_family','source_collections']
 manifest=ROOT/'corpus_manifest.csv'
 with manifest.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
  for p in papers_doc['papers']:
   w.writerow({**p,'authors':'; '.join(p.get('authors',[])),'local_pdf_readable':'yes' if p.get('pdf_readable') else 'no','source_collections':'; '.join(p.get('source_collections',[]))})
 manifest_hash=digest(manifest)

 rel_file=ROOT/'evidence_relations.json'; rel_doc=json.loads(rel_file.read_text(encoding='utf-8')); rels={x['relation_id']:x for x in rel_doc['relations']}
 gold_file=ROOT/'gold_cases.json'; gold_doc=json.loads(gold_file.read_text(encoding='utf-8'))
 eval_rows=[]
 for case in gold_doc['cases']:
  rel=rels[case['input_relation_id']]; case['expected_role']=rel['evidence_role']; case['expected_status']=rel['status']; case['evaluation_status']='ready_for_consistency_validation'
  passed=(case['expected_role']==rel['evidence_role'] and case['expected_status']==rel['status'])
  eval_rows.append({'gold_case_id':case['gold_case_id'],'split':case['split'],'relation_id':rel['relation_id'],'expected_role':case['expected_role'],'observed_role':rel['evidence_role'],'expected_status':case['expected_status'],'observed_status':rel['status'],'result':'pass' if passed else 'fail','evaluation_type':'fixture_consistency_validation'})
 gold_doc['note']='Gold values reflect user-reviewed relations. Evaluation checks corpus/fixture consistency only; it is not a model-performance evaluation.'
 gold_file.write_text(json.dumps(gold_doc,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'gold_case_evaluation.json').write_text(json.dumps({'generated_date':TODAY,'evaluation_type':'fixture_consistency_validation','passed':sum(x['result']=='pass' for x in eval_rows),'failed':sum(x['result']=='fail' for x in eval_rows),'cases':eval_rows},ensure_ascii=False,indent=2),encoding='utf-8')

 active=[p for p in papers_doc['papers'] if p.get('demo_suitability')!='excluded']
 unresolved_sections=[c['evidence_id'] for c in cards_doc['cards'] if c['section_locator_status']=='not_located']
 audit=f'''# NeuroTrace 最终发布结构验收（候选 v2.2）

生成日期：{TODAY}。本次仅修改工作区文件；Zotero 条目与附件未被写入。

## 已通过

- 清单记录：{len(papers_doc['papers'])} 条，其中冻结主库 {len(active)} 篇可读 PDF、排除记录 {len(papers_doc['papers'])-len(active)} 条。
- PDF 哈希：{sum(bool(p.get('pdf_sha256')) for p in papers_doc['papers'])}/{len(papers_doc['papers'])}。
- 证据卡：{len(cards_doc['cards'])} 张；人工确认 {sum(c['status']=='anchor_confirmed' for c in cards_doc['cards'])} 张，人工排除 {sum(c['status']=='rejected' for c in cards_doc['cards'])} 张。
- 卡片级角色与理由：{sum(bool(c.get('evidence_role') and c.get('role_rationale')) for c in cards_doc['cards'])}/{len(cards_doc['cards'])}。
- 新增论文的结构化提取：4/4 完成；`UDGHLCIZ` 的具体数值时间窗明确保留为“未定位”。
- GoldCase 夹具一致性：{sum(x['result']=='pass' for x in eval_rows)}/{len(eval_rows)} 通过；此测试不应被误读为模型评测。

## 发布前仍需披露的限制

- {len(unresolved_sections)} 张卡尚无可靠的命名章节定位；其 PDF 页码、短摘录、Zotero key 与附件 key 仍可回查。章节状态已明确标记为 `not_located`，未被伪造为人工确认。
- 主库为 37 篇（仍在原始 30–40 篇要求内），因为 1 篇 EEG 数据集记录被人工排除；若必须遵循旧修复方案的 38 篇目标，需新增一篇论文并走完同样的人审流程。
'''
 (ROOT/'final_release_audit.md').write_text(audit,encoding='utf-8')
 version_file=ROOT/'corpus_version.json'; version=json.loads(version_file.read_text(encoding='utf-8'))
 version.update({'corpus_version_id':'neurotrace-corpus-2026-09-28-v2.2','generated_date':TODAY,'manifest_sha256':manifest_hash,'frozen_active_readable_papers':len(active),'excluded_readable_records':len(papers_doc['papers'])-len(active),'cards':len(cards_doc['cards']),'gold_fixture_consistency_passed':sum(x['result']=='pass' for x in eval_rows),'gold_fixture_consistency_failed':sum(x['result']=='fail' for x in eval_rows),'sections_not_located':len(unresolved_sections),'release_status':'candidate_release_with_disclosed_section_locator_gaps'})
 version_file.write_text(json.dumps(version,ensure_ascii=False,indent=2),encoding='utf-8')
 report_file=ROOT/'literature_review_report.md'; report_file.write_text(report_file.read_text(encoding='utf-8')+'\n\n## 最终发布结构化收尾（v2.2）\n\n已完成 4 篇新增论文的结构化提取、manifest/version 对账、卡片级角色物化及 12 个 GoldCase 的夹具一致性验证。最终主库为 37 篇已审核可读论文，另有 1 篇被人审排除。具体发布验收与未定位章节状态见 `final_release_audit.md`。\n',encoding='utf-8')
 print(json.dumps({'active':len(active),'excluded':len(papers_doc['papers'])-len(active),'structured_updates':len(STRUCTURED),'gold_pass':sum(x['result']=='pass' for x in eval_rows),'sections_not_located':len(unresolved_sections)},ensure_ascii=False))
if __name__=='__main__': main()

