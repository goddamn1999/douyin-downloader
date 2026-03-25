import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re
from pydantic import BaseModel

app = FastAPI(title="抖音视频下载器", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel 路径处理
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

# 挂载静态文件
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ParseRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    # 尝试读取模板文件
    if os.path.exists(TEMPLATE_PATH):
        try:
            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading template: {e}")
    
    # 如果模板不存在，返回内嵌页面
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>抖音视频下载器</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #333; margin-bottom: 10px; text-align: center; }
            p { color: #666; margin-bottom: 20px; text-align: center; }
            .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
            input {
                flex: 1;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 16px;
            }
            button {
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-size: 16px;
            }
            #result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 12px; display: none; }
            .code-block { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 抖音视频下载器</h1>
            <p>粘贴抖音链接，获取下载命令</p>
            <div class="input-group">
                <input type="text" id="url" placeholder="https://v.douyin.com/xxxxx">
                <button onclick="parse()">解析</button>
            </div>
            <div id="result"></div>
        </div>
        <script>
            async function parse() {
                const url = document.getElementById('url').value;
                const result = document.getElementById('result');
                result.style.display = 'block';
                result.innerHTML = '解析中...';
                
                try {
                    const res = await fetch('/api/parse', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url})
                    });
                    const data = await res.json();
                    
                    if (data.success) {
                        result.innerHTML = `
                            <h3>✅ 解析成功</h3>
                            <p>类型: ${data.data.type}</p>
                            <p>ID: ${data.data.id}</p>
                            <h4>下载命令：</h4>
                            <div class="code-block">
python run.py -u "${data.data.resolved_url}"
                            </div>
                            <p style="margin-top:10px;color:#666">请在本地运行此命令下载</p>
                        `;
                    } else {
                        result.innerHTML = '<p style="color:red">❌ ' + data.message + '</p>';
                    }
                } catch (e) {
                    result.innerHTML = '<p style="color:red">请求失败: ' + e.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/parse")
async def parse_video(request: ParseRequest):
    """解析抖音链接"""
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="链接不能为空")
        
        # 解析短链接
        resolved_url = url
        if "v.douyin.com" in url:
            try:
                import urllib.request
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                response = urllib.request.urlopen(req, timeout=10)
                resolved_url = response.geturl()
            except:
                pass
        
        # 提取 ID
        patterns = [
            (r'/video/(\d+)', 'video'),
            (r'/note/(\d+)', 'note'),
            (r'/gallery/(\d+)', 'gallery'),
            (r'/collection/(\d+)', 'collection'),
            (r'/mix/(\d+)', 'mix'),
            (r'/music/(\d+)', 'music'),
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
            raise HTTPException(status_code=400, detail="无法识别的链接格式")
        
        return {
            "success": True,
            "data": {
                "id": item_id,
                "type": item_type,
                "resolved_url": resolved_url,
                "title": f"抖音{item_type} - {item_id}",
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
