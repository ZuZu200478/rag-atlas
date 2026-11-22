import json,pathlib,datetime,re
R=pathlib.Path(__file__).parent
S=[
 {'id':'S01','publisher':'NeurIPS 2020 / Lewis et al.','title':'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks','url':'https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html','type':'研究論文','date':'2020','takeaways':['RAG 讓語言生成結合模型內部知識與外部可檢索的知識。','原始研究提出將檢索器與生成器整合的架構；本文只使用其基本思想，不照搬模型實驗數值。'],'supports':['RAG基本定義','檢索與生成結合']},
 {'id':'S02','publisher':'Amazon Web Services','title':'What is Retrieval-Augmented Generation (RAG)?','url':'https://aws.amazon.com/what-is/retrieval-augmented-generation/','type':'技術說明','date':'持續更新','takeaways':['RAG 在回答前加入外部可信資料，協助模型參考組織或領域知識。','典型用途包含以企業內部文件回答問題；並非每次都要重新訓練模型。'],'supports':['生活比喻','企業與校園應用']},
 {'id':'S03','publisher':'IBM','title':'What is Retrieval-Augmented Generation (RAG)?','url':'https://www.ibm.com/think/topics/retrieval-augmented-generation','type':'技術說明','date':'持續更新','takeaways':['將檢索內容加入提示詞，再由 LLM 組織回答，可改善資訊相關性。','RAG 有助於降低幻覺風險，但不能保證完全正確。'],'supports':['RAG優點','幻覺與限制']},
 {'id':'S04','publisher':'Microsoft Learn','title':'Retrieval augmented generation (RAG) and indexes in Microsoft Foundry','url':'https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation','type':'官方技術文件','date':'持續更新','takeaways':['線上 RAG 可分 Retrieve → Augment → Generate。','索引可支援關鍵字、語意、向量與混合檢索，文件標題與 URL 有助來源追溯。','資料切塊、Embedding、搜尋設定會影響檢索品質；需要權限與隱私控管。'],'supports':['三步驟','索引','檢索策略','錯誤定位']},
 {'id':'S05','publisher':'Ragas','title':'Faithfulness — Ragas Documentation','url':'https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/','type':'官方評估文件','date':'持續更新','takeaways':['Faithfulness 衡量生成回答的主張是否受提供的檢索上下文支持。','可將回答拆為可檢查的主張，再逐一比較證據；較高分代表與檢索上下文更一致。'],'supports':['回答忠實度','品質評估']},
 {'id':'S06','publisher':'LangChain Documentation','title':'Learn — LangChain / LangGraph','url':'https://docs.langchain.com/oss/python/learn','type':'官方教學入口','date':'持續更新','takeaways':['官方教學包含語意搜尋、RAG Agent 與自訂 LangGraph RAG Agent。','RAG 可採分階段檢索與生成，也能擴充為具多個節點的工作流程。'],'supports':['RAG的建置路徑','Agent和RAG的關係']},
]
P=[
 {'id':'intro','title':'RAG 是什麼？','topic':'核心概念','lead':'檢索增強生成（Retrieval-Augmented Generation）把「先找資料」和「再由 LLM 回答」結合。','bullets':['一般 LLM 可能不知道尚未納入訓練的新資訊與私有文件。','RAG 把外部資料作為回答當下的參考，讓回答更有依據。','它改善的是「取得與使用知識」的流程，不等於把新資料重新訓練進模型。'],'example':'例如學生問「這學期實驗室借用規定？」：系統先找到公告，再用公告回答。','sources':['S01','S02','S03'],'related':['retrieve','prompt','limits']},
 {'id':'prepare','title':'建立知識庫：資料、切塊與索引','topic':'核心流程','lead':'使用者發問以前，先讓文件變得容易被搜尋。','bullets':['蒐集可靠的 PDF、公告、網頁或規章，保留標題與來源。','將長篇文件依語意或段落切成較小的 chunk。','可建立關鍵字索引或產生 Embedding 向量並寫入向量索引。'],'example':'30 頁的借用手冊，不必每次整本塞進提示詞；可以先切成「借用時間」「設備注意事項」等段落。','sources':['S02','S04'],'related':['retrieve','embedding','intro']},
 {'id':'embedding','title':'Embedding 與向量檢索','topic':'重要術語','lead':'Embedding 將文字映射為數值向量，便於比較語意相似性。','bullets':['「教室能借到幾點？」與「空間開放時間」的字詞不同，但語意可能相近。','向量檢索在語意接近的情況下有幫助；精確編號或專有名詞也常需關鍵字檢索。','混合檢索可同時利用關鍵字與向量訊號。'],'example':'問「申請門禁」也可能檢索到標題寫「實驗室出入權限」的段落。','sources':['S04'],'related':['prepare','retrieve']},
 {'id':'retrieve','title':'Retrieve：先找到證據','topic':'核心流程','lead':'問題進來後，檢索器從索引找出可能回答問題的相關片段。','bullets':['根據問題進行關鍵字、向量或混合檢索。','選取少量相關段落（例如 top-k）；必要時重新排序。','若檢索不到足夠資料，應先回報不足，而不是憑空補完。'],'example':'「實驗室週日能進去嗎？」→ 找到「開放時間與權限」規定的片段。','sources':['S04','S06'],'related':['embedding','prompt','limits']},
 {'id':'prompt','title':'Augment + Generate：根據資料回答','topic':'核心流程','lead':'把問題、取回的片段與回答規則放進提示詞，再請 LLM 作答。','bullets':['Augment：把檢索到的依據放到模型可見的上下文。','Generate：要求模型依據上下文整理答案，並標示來源。','若來源沒有說明，就明確告知「目前資料不足」。'],'example':'規定片段寫「週日不開放」→ 回答「依據場地管理公告，週日不開放」，並附公告名稱。','sources':['S01','S03','S04'],'related':['retrieve','evaluation','limits']},
 {'id':'compare','title':'RAG、一般聊天與微調的差別','topic':'概念比較','lead':'三者可互補，但處理問題的機制不同。','bullets':['一般聊天：主要依賴對話上下文與模型既有能力，不會自動知道校內新公告。','RAG：在回答時查外部文件，適合資料經常更新、需要追溯來源的場景。','微調：透過額外訓練影響模型行為或領域表現，通常不是用來頻繁同步每篇公告的首選。'],'example':'校務 FAQ 更新頻繁，優先考慮更新知識庫；若要固定輸出格式，可另外評估提示設計或微調。','sources':['S01','S02','S03'],'related':['intro','prepare']},
 {'id':'limits','title':'RAG 仍然可能答錯','topic':'品質控制','lead':'檢索增加可用資訊，但不是保證正確的開關。','bullets':['資料本身過期或相互矛盾：答案可能跟著錯。','切塊不當或檢索失敗：模型看不到關鍵證據。','即使有證據，模型仍可能誤解、擴大推論或漏掉限制條件。'],'example':'找到去年規定卻回答今年的開放時間，就是「資料版本檢查」沒做好。','sources':['S03','S04'],'related':['prepare','retrieve','evaluation']},
 {'id':'evaluation','title':'如何檢查 RAG 的品質','topic':'品質控制','lead':'要分開檢查「找得對不對」與「答得有沒有根據」。','bullets':['來源完整性：標題、網址、日期或版本是否保留。','檢索相關性：取回片段能否回答問題。','忠實度 Faithfulness：答案中的主張是否能從檢索內容推得。','可用性：初學者看得懂嗎？引用能否點回原始文件？'],'example':'答案：「週日可借用」但證據只寫「平日 9–17 時」→ 不能從證據推得，判為不忠實。','sources':['S04','S05','S06'],'related':['prompt','limits']},
 {'id':'applications','title':'日常實際應用：校園知識助理','topic':'實作情境','lead':'以課務公告、實驗室規章或報帳文件建立可查詢的校園助手。','bullets':['輸入：校內可信公告、規範文件，並記錄更新時間。','查詢：學生用自然語言提問；系統找對應段落。','回答：整理重點並附文件來源；資料不足時提示詢問承辦人。','維護：新規定進來就更新知識庫並回歸測試。'],'example':'不再對著 20 份 PDF 猜「核銷屬於材料費還是雜支」；以現行核銷要點為準。','sources':['S02','S03','S04','S06'],'related':['intro','prepare','evaluation']},
]
D=[
 {'id':'s01','eyebrow':'RAG / 101','title':'讓 AI 先找資料，再回答','sub':'Retrieval-Augmented Generation｜檢索增強生成','kind':'cover','wiki':['intro'],'sources':['S01','S02']},
 {'id':'s02','eyebrow':'01 / WHY','title':'為什麼直接問 LLM 還不夠？','sub':'遇到最新、專屬或需要查證的資訊，模型可能猜測。','kind':'problem','wiki':['intro','limits'],'sources':['S02','S03']},
 {'id':'s03','eyebrow':'02 / CONCEPT','title':'RAG 到底是什麼？','sub':'RAG = Retrieval（檢索） + Augmented（增強） + Generation（生成）','kind':'definition','wiki':['intro'],'sources':['S01','S02','S03']},
 {'id':'s04','eyebrow':'03 / PIPELINE','title':'三步驟：找 → 放 → 答','sub':'Retrieve → Augment → Generate','kind':'pipeline','wiki':['retrieve','prompt'],'sources':['S01','S04']},
 {'id':'s05','eyebrow':'04 / BEFORE Q&A','title':'先建好知識庫，才能有效查資料','sub':'文件 → 清理與切塊 → 建索引','kind':'index','wiki':['prepare','embedding'],'sources':['S02','S04']},
 {'id':'s06','eyebrow':'05 / SEARCH','title':'搜尋不一定只看關鍵字','sub':'關鍵字、語意向量、混合搜尋','kind':'search','wiki':['embedding','retrieve'],'sources':['S04']},
 {'id':'s07','eyebrow':'06 / LIVE EXAMPLE','title':'一起拆解一則校園提問','sub':'「週日可以使用實驗室嗎？」','kind':'example','wiki':['applications','retrieve','prompt'],'sources':['S02','S04']},
 {'id':'s08','eyebrow':'07 / DIFFERENCES','title':'RAG ≠ 重新訓練模型','sub':'一般 LLM、RAG、微調，各自擅長不同任務','kind':'compare','wiki':['compare'],'sources':['S01','S02','S03']},
 {'id':'s09','eyebrow':'08 / CAUTIONS','title':'找到資料，也還是可能答錯','sub':'錯誤來源可能是文件、檢索，也可能是生成。','kind':'risks','wiki':['limits'],'sources':['S03','S04']},
 {'id':'s10','eyebrow':'09 / QUALITY','title':'怎麼知道答案有沒有根據？','sub':'先查找得對不對，再查回答是否忠實','kind':'evaluation','wiki':['evaluation'],'sources':['S04','S05','S06']},
 {'id':'s11','eyebrow':'10 / BUILD','title':'做一個小型 RAG 的 5 個步驟','sub':'從可信文件出發，不必一次做成大型系統。','kind':'checklist','wiki':['prepare','retrieve','prompt','evaluation'],'sources':['S02','S04','S05','S06']},
 {'id':'s12','eyebrow':'11 / QUIZ','title':'你真的看懂 RAG 了嗎？','sub':'選擇哪一個流程最合理','kind':'quiz','wiki':['retrieve','prompt'],'sources':['S04']},
 {'id':'s13','eyebrow':'12 / SUMMARY','title':'帶走這三件事','sub':'先找證據、依據作答、再做檢查。','kind':'summary','wiki':['intro','limits','evaluation'],'sources':['S01','S03','S04','S05']},
 {'id':'s14','eyebrow':'REFERENCES','title':'本簡報使用的 6 份知識來源','sub':'可由每張投影片右下角回到 Wiki 與原始資料。','kind':'references','wiki':['intro','evaluation'],'sources':['S01','S02','S03','S04','S05','S06']},
]
for folder in ('data','sources','wiki','logs','assets'): (R/folder).mkdir(exist_ok=True)
(R/'data'/'sources.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data'/'wiki_pages.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data'/'slides.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
for s in S:
 t=f"# {s['title']}\n\n- 來源代號：{s['id']}\n- 發布者：{s['publisher']}\n- 類型：{s['type']}\n- 日期：{s['date']}\n- 原始網址：{s['url']}\n- 整理日期：2026-11-22\n\n## 經查核後的重點整理（非原文全文）\n"+''.join('\n- '+x for x in s['takeaways'])+'\n\n## 對應知識\n'+''.join('\n- '+x for x in s['supports'])+'\n\n> 本檔是依原始來源建立的整理筆記。著作權屬原作者，請由上述網址閱讀全文。\n'
 (R/'sources'/f'{s["id"]}.md').write_text(t,encoding='utf-8')
for p in P:
 t=f"# {p['title']}\n\n分類：{p['topic']}\n\n{p['lead']}\n\n## 重點\n"+''.join('\n- '+b for b in p['bullets'])+f"\n\n## 例子\n{p['example']}\n\n## 資料來源\n"+''.join(f'\n- [{x}](../sources/{x}.md)' for x in p['sources'])+"\n\n## 延伸閱讀（Wiki）\n"+''.join(f'\n- [[{x}]]' for x in p['related'])+'\n'
 (R/'wiki'/f'{p["id"]}.md').write_text(t,encoding='utf-8')
logs=[{'time':'2026-11-22','stage':'DISCUSS','action':'先確定範圍：以非技術初學者理解 RAG 核心流程為目標；排除模型訓練公式與平台安裝細節。','result':'outline agreed as working scope; user may customize' }]
for i,s in enumerate(S,1): logs.append({'time':'2026-11-22','stage':'INGEST','source_id':s['id'],'action':'檢視來源概要→萃取可查證重點→寫入來源摘要→更新 Wiki 知識對應','result':'created sources/'+s['id']+'.md','fact_count':len(s['takeaways'])})
logs.append({'time':'2026-11-22','stage':'SYNTHESIZE','action':'整合重複主題成 9 個互相連結的 Wiki 概念頁，並映射 14 張簡報。','result':'9 pages / 14 slides'})
(R/'logs'/'ingestion.jsonl').write_text(''.join(json.dumps(l,ensure_ascii=False)+'\n' for l in logs),encoding='utf-8')
print('sources',len(S),'wiki_pages',len(P),'slides',len(D))
