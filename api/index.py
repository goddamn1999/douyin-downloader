from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re
import json
import os
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="抖音视频下载器", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路径处理（Vercel 环境）
BASE_DIR = Path(__file__).parent.parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

# 只在目录存在时挂载静态文件
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class ParseRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    try:
        index_file = templates_dir / "index.html"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error loading index: {e}")
    
    # 备用页面
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head><title>抖音视频下载器</title></head>
    <body>
        <h1>🎵 抖音视频下载器</h1>
        <p>API 服务运行正常</p>
        <p>访问 <a href="/api/health">/api/health</a> 检查状态</p>
    </body>
    </html>
    """)

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
                "message": "链接解析成功！请在本地运行下载命令。",
                "cover": "https://via.placeholder.com/200",
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0", "service": "douyin-downloader"}

# Vercel 入口 - 导出 app
# 注意：不要在这里运行 uvicorn，Vercel 会处理
