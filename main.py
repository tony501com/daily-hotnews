import os
import json
import time
import random
from datetime import datetime
from ddgs import DDGS
import trafilatura
import requests

OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_and_enrich():
    print("🚀 开始采集今日热点...")
    resp = requests.get("https://top.baidu.com/api/board?platform=wise&tab=realtime", 
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    cards = resp.json()['data']['cards'][0]['content'][0]['content'][:10]
    
    data = []
    for idx, item in enumerate(cards, 1):
        keyword = item.get('word', '')
        print(f"[{idx}/10] 处理: {keyword}")
        
        entry = {
            "rank": idx,
            "baidu_title": keyword,
            "baidu_desc": (item.get('desc') or '')[:80],
            "baidu_hot_index": f"{item.get('hotScore', 0):,}",
            "baidu_tag": item.get('tag', ''),
            "original_url": "",
            "source_site": "",
            "full_content": "（提取失败，请点击原文链接查看）"
        }
        
        try:
            time.sleep(1.5 + random.uniform(0.3, 0.8))
            with DDGS() as ddgs:
                hits = list(ddgs.text(keyword, max_results=1, region='cn-zh'))
            if hits:
                entry["original_url"] = hits[0].get('href', '')
                entry["source_site"] = hits[0].get('source', '未知')
                
                time.sleep(2.0 + random.uniform(0.3, 0.6))
                html = trafilatura.fetch_url(entry["original_url"])
                if html:
                    text = trafilatura.extract(html, include_comments=False, include_tables=False)
                    if text and len(text.strip()) > 150:
                        entry["full_content"] = text.strip()
        except Exception as e:
            print(f"  ⚠️ 跳过: {e}")
            
        data.append(entry)
    return data

def save_files(data):
    ts = datetime.now().strftime('%Y%m%d')
    
    # 1. 保存 JSON
    json_path = os.path.join(OUTPUT_DIR, "latest.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # 2. 生成适老 HTML
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日热点简报</title>
    <style>body{{font-family:"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f7fa;color:#111;margin:0;padding:20px;line-height:1.8;font-size:20px}}
    .wrap{{max-width:900px;margin:0 auto}}h1{{text-align:center;color:#0056b3;margin-bottom:5px}}
    .date{{text-align:center;color:#666;font-size:18px;margin-bottom:25px}}
    .card{{background:#fff;border-radius:12px;padding:24px;margin-bottom:25px;box-shadow:0 2px 8px rgba(0,0,0,0.08)}}
    .title{{font-size:24px;font-weight:bold;margin-bottom:8px}}.meta{{color:#555;font-size:18px;margin-bottom:15px;border-bottom:1px dashed #eee;padding-bottom:12px}}
    .content{{font-size:22px;line-height:2;white-space:pre-wrap;background:#fafafa;padding:15px;border-radius:8px}}
    .tag{{display:inline-block;background:#e6f0ff;color:#0056b3;padding:2px 8px;border-radius:4px;font-size:16px;margin-left:8px}}
    footer{{text-align:center;color:#888;font-size:16px;margin-top:30px}}</style></head><body>
    <div class="wrap"><h1>📰 每日热点全文简报</h1><div class="date">{datetime.now().strftime('%Y年%m月%d日 08:00 更新')}</div>"""
    
    for d in data:
        tag = f'<span class="tag">{d["baidu_tag"]}</span>' if d["baidu_tag"] else ''
        html_content += f"""<div class="card">
          <div class="title">#{d['rank']} {d['baidu_title']}{tag}</div>
          <div class="meta">🔥 {d['baidu_hot_index']} | 摘要: {d['baidu_desc']}<br>🌐 <a href="{d['original_url']}" target="_blank" style="color:#0056b3">点击查看原文</a></div>
          <div class="content">{d['full_content']}</div>
        </div>"""
        
    html_content += "<footer>💡 字体已调大，段落已优化。本页面由 GitHub Actions 自动生成 | 仅供长辈阅读</footer></div></body></html>"
    
    html_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✅ 文件已保存至 {OUTPUT_DIR}/ 目录")

if __name__ == "__main__":
    news_data = fetch_and_enrich()
    save_files(news_data)
