
import requests
import re
import json
import os

def clean_surrogates(obj):
    """递归清理字符串中的代理对字符，保留可打印字符"""
    if isinstance(obj, str):
        return obj.encode('utf-8', 'ignore').decode('utf-8')
    elif isinstance(obj, list):
        return [clean_surrogates(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_surrogates(v) for k, v in obj.items()}
    else:
        return obj

# 1. 获取网页数据
url = "https://top.baidu.com/board?tab=realtime"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)
response.encoding = "utf-8"
html = response.text

# 2. 提取注释中的 JSON 数据
pattern = r'<!--s-data:({.*?})-->'
match = re.search(pattern, html, re.DOTALL)
if not match:
    print("未找到数据")
    exit()

OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


json_str = match.group(1)
data = json.loads(json_str)

# 3. 定位热搜列表（前5条）
cards = data.get('data', {}).get('cards', [])
hot_items = []
for card in cards:
    hot_items.extend(card.get('content', []))
hot_items = hot_items[:30]

# 4. 提取需要的字段：appUrl, query, word, desc
filtered_items = []
for item in hot_items:
    filtered = {
        "appUrl": item.get("appUrl", ""),
        "query": item.get("query", ""),
        "word": item.get("word", ""),
        "desc": item.get("desc", "")
    }
    filtered_items.append(filtered)

# 5. 清理代理对字符（递归处理所有字段）
filtered_items_clean = clean_surrogates(filtered_items)

# 6. 保存为 JSON 文件（只包含四个字段）
json_path = os.path.join(OUTPUT_DIR, "latest.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(filtered_items_clean, f, ensure_ascii=False, indent=2)

print("已保存 hot_data.json（仅含 appUrl, query, word, desc）")

# 7. 生成老年人友好的 HTML 文件（使用同样的 cleaned 数据）
html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>百度热搜榜 - 大字版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background-color: #f5f7fa; font-family: 'Segoe UI', 'Roboto', 'Noto Sans', system-ui, sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { font-size: 2rem; text-align: center; color: #1e3c72; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #ff9800; display: inline-block; width: auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .update-time { color: #666; font-size: 1.1rem; margin-top: 8px; }
        .card { background: white; border-radius: 20px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: transform 0.2s; border-left: 8px solid #ff9800; }
        .card:hover { transform: scale(1.01); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
        .card-index { display: inline-block; background: #ff9800; color: white; font-weight: bold; font-size: 1.3rem; width: 40px; height: 40px; line-height: 40px; text-align: center; border-radius: 50%; margin-right: 12px; }
        .card-title { font-size: 1.6rem; font-weight: 600; color: #1e3c72; margin-bottom: 12px; display: flex; align-items: center; flex-wrap: wrap; }
        .query { font-size: 1.2rem; color: #0a5b8c; background: #e8f0fe; padding: 8px 12px; border-radius: 30px; margin: 12px 0; word-break: break-all; }
        .query-label { font-weight: bold; color: #004d73; }
        .appurl { margin: 12px 0; font-size: 1.1rem; }
        .appurl a { color: #ff9800; text-decoration: none; background: #fff3e0; padding: 6px 12px; border-radius: 30px; display: inline-block; word-break: break-all; }
        .appurl a:hover { background: #ffe0b3; text-decoration: underline; }
        .desc { background: #f9f9fc; padding: 16px; border-radius: 16px; margin-top: 16px; font-size: 1.2rem; line-height: 1.5; color: #2c3e50; border-left: 4px solid #ff9800; }
        .desc-label { font-weight: bold; color: #e67e22; margin-bottom: 6px; font-size: 1.1rem; }
        footer { text-align: center; margin-top: 30px; color: #888; font-size: 0.9rem; }
        @media (max-width: 600px) { body { padding: 12px; } .card-title { font-size: 1.3rem; } .desc { font-size: 1rem; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📰 百度热搜榜 · 大字版</h1>
        <div class="update-time">🕒 数据更新时间：""" + f"{response.headers.get('Date', '刚刚')}" + """</div>
    </div>
    <div id="hot-list"></div>
    <footer>🔍 点击链接可查看详情 | 适合长辈阅读的大字界面</footer>
</div>
<script>
    const hotData = """ + json.dumps(filtered_items_clean, ensure_ascii=False) + """;
    const container = document.getElementById('hot-list');
    if (hotData.length === 0) {
        container.innerHTML = '<p style="text-align:center;font-size:1.5rem;">暂无数据</p>';
    } else {
        let html = '';
        hotData.forEach((item, idx) => {
            const indexNum = idx + 1;
            const word = item.word || '无标题';
            const query = item.query || '';
            const appUrl = item.appUrl || '';
            const desc = item.desc || '暂无描述';
            html += `
                <div class="card">
                    <div class="card-title">
                        <span class="card-index">${indexNum}</span>
                        <span>${escapeHtml(word)}</span>
                    </div>
                    <div class="query">
                        <span class="query-label">🔎 搜索词：</span> ${escapeHtml(query)}
                    </div>
                    <div class="appurl">
                        📎 <a href="${escapeHtml(appUrl)}" target="_blank" rel="noopener noreferrer">点击查看详情 🔗</a>
                    </div>
                    <div class="desc">
                        <div class="desc-label">📖 详情描述</div>
                        ${escapeHtml(desc)}
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        }).replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, function(c) {
            return c;
        });
    }
</script>
</body>
</html>"""

# 写入 index.html 前再次清理整个字符串中的代理对
html_content_clean = html_content.encode('utf-8', 'ignore').decode('utf-8')

html_path = os.path.join(OUTPUT_DIR, "index.html")
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content_clean)

print("已生成 index.html，请用浏览器打开查看（适合老年人阅读，desc 在每个卡片底部）")
