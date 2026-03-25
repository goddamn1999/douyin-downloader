from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import re

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return HTMLResponse(content="""
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
    """)

@app.post("/api/parse")
async def parse_video(request: ParseRequest):
    try:
        url = request.url.strip()
        if not url:
            return {"success": False, "message": "链接不能为空"}
        
        resolved_url = url
        patterns = [
            (r'/video/(\d+)', 'video'),
            (r'/note/(\d+)', 'note'),
            (r'/user/([^/?\u0026]+)', 'user'),
        ]
        
        item_id = None
        item_type = None
        
        for pattern, itype in patterns:
            match = re.search(pattern, resolved_url)
            if match:
                item_id = match.group(1)
                item_type = itype
                break
        
        if not item_id:
            return {"success": False, "message": "无法识别的链接"}
        
        return {
            "success": True,
            "data": {
                "id": item_id,
                "type": item_type,
                "resolved_url": resolved_url,
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
