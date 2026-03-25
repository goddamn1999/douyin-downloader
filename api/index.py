from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head><title>抖音视频下载器</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px;">
    <h1>🎵 抖音视频下载器</h1>
    <input id="url" placeholder="粘贴抖音链接" style="width:100%;padding:10px;margin:10px 0;">
    <button onclick="parse()" style="padding:10px 20px;">解析</button>
    <div id="result"></div>
    <script>
        async function parse() {
            const url = document.getElementById('url').value;
            const res = await fetch('/api/parse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url})
            });
            const data = await res.json();
            document.getElementById('result').innerHTML = data.success 
                ? `<p>类型: ${data.data.type}</p><p>ID: ${data.data.id}</p>`
                : '<p>解析失败</p>';
        }
    </script>
</body>
</html>
'''

@app.route("/")
def home():
    return HTML

@app.route("/api/parse", methods=["POST"])
def parse():
    data = request.get_json()
    url = data.get("url", "").strip()
    
    if not url:
        return jsonify({"success": False, "message": "链接不能为空"})
    
    patterns = [
        (r'/video/(\d+)', 'video'),
        (r'/note/(\d+)', 'note'),
    ]
    
    for pattern, itype in patterns:
        match = re.search(pattern, url)
        if match:
            return jsonify({
                "success": True,
                "data": {
                    "id": match.group(1),
                    "type": itype,
                    "resolved_url": url,
                }
            })
    
    return jsonify({"success": False, "message": "无法识别的链接"})

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})
