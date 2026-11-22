"""Deterministic source/Wiki/slide QA. This validates provenance, not factual entailment."""
from pathlib import Path
from collections import Counter
import json, argparse
P=Path(__file__).parent
src=json.loads((P/'data/sources.json').read_text(encoding='utf-8'))
wiki=json.loads((P/'data/wiki_pages.json').read_text(encoding='utf-8'))
slides=json.loads((P/'data/slides.json').read_text(encoding='utf-8'))
sp={x['id']:x for x in src};wp={x['id']:x for x in wiki}
issues=[]
def ck(condition,why):
 if not condition:issues.append(why)
 return bool(condition)
checks={}
checks['sources_min_5']=ck(len(src)>=5 and all((P/'sources'/f"{s['id']}.md").exists() for s in src),'少於 5 篇來源或缺少摘要文件')
checks['source_unique']=ck(len(sp)==len(src) and all(s['url'].startswith('https://') for s in src),'來源 ID 重複或網址無效')
checks['wiki_source_links']=ck(all(p['sources'] and set(p['sources']).issubset(sp) and set(p['related']).issubset(wp) and (P/'wiki'/f"{p['id']}.md").exists() for p in wiki),'Wiki 來源／related 連結遺失')
checks['slide_wiki_refs']=ck(all(d['wiki'] and set(d['wiki']).issubset(wp) for d in slides),'投影片使用未知 Wiki ID')
checks['slide_source_refs']=ck(all(d['sources'] and set(d['sources']).issubset(sp) for d in slides),'投影片使用未知來源 ID')
# The evaluation slide MUST include direct evidence for the Faithfulness definition.
# This is a claim-level obligation, beyond the looser page-to-source crosswalk.
requirements={'evaluation':{'S05'},'pipeline':{'S04'},'references':set(sp)}
fail=[]
for d in slides:
 supported=set().union(*(wp[p]['sources'] for p in d['wiki'] if p in wp)) if d['wiki'] else set()
 required=requirements.get(d['kind'],set())
 if not set(d['sources']).issubset(supported) or not required.issubset(d['sources']):
  fail.append({'slide':d['id'],'cited':d['sources'],'supported_by_wiki':sorted(supported),'required_evidence':sorted(required)})
checks['slide_grounding']=ck(not fail,'source-to-slide claim mapping fails: '+json.dumps(fail,ensure_ascii=False))
checks['html_generated']=ck(all((P/f).exists() for f in ['index.html','wiki.html','slides.html','workflow.html']) and (P/'slides.html').read_text(encoding='utf-8').count('class="slide ') == len(slides),'HTML 缺少或張數不一致')
result={'stage':'deterministic audit','date':'2026-11-22','stats':{'source_count':len(src),'wiki_page_count':len(wiki),'slide_count':len(slides)},'checks':checks,'all_pass':all(checks.values()),'issues':issues,'mapping_issues':fail,'note':'source metadata and crossreferences are tested; semantic correctness requires human review'}
print(json.dumps(result,ensure_ascii=False,indent=2))
arg=argparse.ArgumentParser();arg.add_argument('--save');args=arg.parse_args()
if args.save:(P/args.save).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(0 if result['all_pass'] else 1)
