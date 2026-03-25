from flask import Flask, request, jsonify
import re

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>抖音视频下载器</title>
<style>
body{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;justify-content:center;align-items:center;margin:0;padding:20px}
.container{background:white;border-radius:20px;padding:40px;max-width:600px;width:100%}
h1{color:#333;text-align:center}
input{width:100%;padding:15px;border:2px solid #ddd;border-radius:12px;margin:10px 0;box-sizing:border-box}
button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;cursor:pointer}
#result{margin-top:20px;padding:20px;background:#f8f9fa;border-radius:12px;display:none}
.code{background:#1e1e1e;color:#d4d4d4;padding:15px;border-radius:8px;font-family:monospace;margin-top:10px}
</style></head>
<body>
<div class="container">
<h1>🎵 抖音视频下载器</h1>
<input type="text" id="url" placeholder="粘贴抖音链接">
<button onclick="parse()">解析</button>
<div id="result"></div>
</div>
<script>
async function parse(){
const url=document.getElementById('url').value.trim();
if(!url){alert('请输入链接');return;}
const result=document.getElementById('result');
result.style.display='block';result.innerHTML='解析中...';
try{
const res=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
const data=await res.json();
if(data.success){
result.innerHTML=`<h3>✅ 解析成功</h3><p>类型:${data.type}</p><p>ID:${data.id}</p><div class="code">python run.py -u "${data.url}"</div>`;
}else{result.innerHTML='<p style="color:red">❌ '+data.message+'</p>';}
}catch(e){result.innerHTML='<p style="color:red">请求失败</p>';}
}
</script>
</body></html>'''

@app.route('/')
def home():
    return HTML

@app.route('/api', methods=['POST'])
def parse():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'message': '链接不能为空'})
    patterns = [(r'/video/(\d+)', 'video'), (r'/note/(\d+)', 'note')]
    for pattern, itype in patterns:
        match = re.search(pattern, url)
        if match:
            return jsonify({'success': True, 'id': match.group(1), 'type': itype, 'url': url})
    return jsonify({'success': False, 'message': '无法识别的链接'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})
