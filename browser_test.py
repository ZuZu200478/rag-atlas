from playwright.sync_api import sync_playwright
from pathlib import Path
import json
R=Path(__file__).parent
css=(R/'assets/style.css').read_text(encoding='utf-8')
results=[];errors=[]
def ck(x):assert x,'Assertion failed'
def load(page,name,frag=''):
 if frag:page.goto('about:blank#'+frag)
 s=(R/name).read_text(encoding='utf-8').replace('<link rel="stylesheet" href="assets/style.css">','<style>'+css+'</style>')
 page.set_content(s,wait_until='domcontentloaded')
def check(label,fn):
 try:fn();results.append({'test':label,'status':'PASS'})
 except Exception as e:results.append({'test':label,'status':'FAIL','error':str(e)[:350]})
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def fresh(width=1440,height=900):
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1);page.set_default_timeout(5000);page.on('pageerror',lambda e:errors.append(str(e)));return page
 h=fresh();check('首頁載入',lambda:(load(h,'index.html'),ck('讓 AI 的回答' in h.locator('h1').first.inner_text())));h.screenshot(path=str(R/'logs/home.png'),full_page=True)
 w=fresh();check('Wiki 首頁載入',lambda:(load(w,'wiki.html'),ck(w.locator('#wiki-content h1').inner_text()=='RAG 是什麼？')))
 check('Wiki 搜尋',lambda:(w.locator('#wiki-search').fill('忠實度'),ck(w.locator('#wiki-menu button').count()>=1)))
 check('Wiki 頁內連結',lambda:(w.evaluate("location.hash='evaluation'"),ck('品質' in w.locator('#wiki-content h1').inner_text()),ck(w.locator('.source-row').count()==3)))
 w.screenshot(path=str(R/'logs/wiki.png'),full_page=True)
 d=fresh();check('14張投影片',lambda:(load(d,'slides.html'),ck(d.locator('.slide').count()==14),ck(d.locator('.slide.active').count()==1)));d.screenshot(path=str(R/'logs/slide1.png'))
 check('下一張按鈕',lambda:(d.locator('#next').click(),ck('02 / 14' in d.locator('#counter').inner_text())))
 check('鍵盤切換',lambda:(d.keyboard.press('ArrowRight'),ck('03 / 14' in d.locator('#counter').inner_text())))
 deep=fresh();check('Hash 指定第10張',lambda:(load(deep,'slides.html','slide-10'),ck('10 / 14' in deep.locator('#counter').inner_text())))
 deep.screenshot(path=str(R/'logs/slide10.png'))
 check('教學頁引用',lambda:(ck(deep.locator('.slide.active .sources-small a').count()>=3),ck('S05' in deep.locator('.slide.active').get_attribute('data-source-ids'))))
 check('互動問答',lambda:(d.evaluate('show(11)'),d.locator('.slide.active .quiz-options button[data-correct="true"]').click(),ck('正確' in d.locator('#quiz-result').inner_text())))
 check('跳至最後',lambda:(d.keyboard.press('End'),ck('14 / 14' in d.locator('#counter').inner_text()),ck(d.locator('#next').is_disabled())));d.screenshot(path=str(R/'logs/slide14.png'))
 g=fresh();check('工作流程 QA',lambda:(load(g,'workflow.html'),ck(g.locator('.audit-table tbody tr').count()==7),ck(g.locator('tbody .status-fail').count()==1)));g.screenshot(path=str(R/'logs/workflow.png'),full_page=True)
 wm=fresh(390,844);check('行動版 Wiki',lambda:(load(wm,'wiki.html'),ck(wm.locator('#wiki-content h1').is_visible())))
 dm=fresh(390,844);check('行動版簡報',lambda:(load(dm,'slides.html'),ck(dm.locator('.slide.active').is_visible())));dm.screenshot(path=str(R/'logs/mobile-slide1.png'))
 b.close()
summary={'tested_on':'2026-11-22','browser':'Chromium headless, DOM set_content (local file and HTTP navigation blocked by sandbox)','total':len(results),'pass':sum(x['status']=='PASS' for x in results),'fail':sum(x['status']=='FAIL' for x in results),'results':results,'javascript_errors':errors}
(R/'logs/browser_tests.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
