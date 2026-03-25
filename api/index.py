from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re
import json
import os
import sys
import asyncio
import subprocess
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import tempfile
import shutil

app = FastAPI(title="抖音视频下载器", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = Path(__file__).parent.parent / "static"
templates_dir = Path(__file__).parent.parent / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ParseRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    type: str = "video"  # video, note, collection, music, user


def resolve_short_url(url: str) -> str:
    """解析短链接到完整链接"""
    if "v.douyin.com" in url:
        try:
            import urllib.request
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0')
            response = urllib.request.urlopen(req, timeout=10)
            return response.geturl()
        except:
            pass
    return url


def extract_id(url: str) -> tuple:
    """从链接中提取 ID 和类型"""
    patterns = [
        (r'/video/(\d+)', 'video'),
        (r'/note/(\d+)', 'note'),
        (r'/gallery/(\d+)', 'gallery'),
        (r'/collection/(\d+)', 'collection'),
        (r'/mix/(\d+)', 'mix'),
        (r'/music/(\d+)', 'music'),
        (r'/user/([^/?\u0026]+)', 'user'),
    ]
    
    for pattern, item_type in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), item_type
    
    return None, None


@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = templates_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>抖音视频下载器</h1><p>Web界面加载失败</p>")


@app.post("/api/parse")
async def parse_video(request: ParseRequest):
    """解析抖音视频链接"""
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="链接不能为空")
        
        # 解析短链接
        resolved_url = resolve_short_url(url)
        
        # 提取 ID
        item_id, item_type = extract_id(resolved_url)
        
        if not item_id:
            raise HTTPException(status_code=400, detail="无法识别的链接格式，请检查链接")
        
        # 构建下载器命令
        # 这里我们创建一个临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            config_content = f"""link:
  - {resolved_url}
path: ./downloads
mode:
  - {item_type if item_type != 'gallery' else 'note'}
number:
  {item_type}: 0
thread: 3
retry_times: 3
proxy: ""
database: false
progress:
  quiet_logs: true
cookies:
  msToken: ""
  ttwid: ""
  odin_tt: ""
  passport_csrf_token: ""
  sid_guard: ""
browser_fallback:
  enabled: false
"""
            f.write(config_content)
            config_path = f.name
        
        # 尝试调用下载器获取信息
        # 注意：由于 Vercel 是无服务器环境，实际下载需要在本地或其他环境
        # 这里返回解析结果，告诉用户如何使用
        
        return {
            "success": True,
            "data": {
                "id": item_id,
                "type": item_type,
                "resolved_url": resolved_url,
                "title": f"抖音{item_type} - {item_id}",
                "message": "链接解析成功！由于服务器限制，请使用本地版本下载。",
                "download_command": f"python run.py -c config.yml -u \"{resolved_url}\"",
                "cover": f"https://p3-pc.douyinpic.com/img/placeholder.jpg",
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@app.post("/api/download-info")
async def get_download_info(request: DownloadRequest):
    """获取视频下载信息"""
    try:
        resolved_url = resolve_short_url(request.url)
        item_id, item_type = extract_id(resolved_url)
        
        if not item_id:
            raise HTTPException(status_code=400, detail="无法识别的链接")
        
        # 返回下载命令和说明
        return {
            "success": True,
            "data": {
                "id": item_id,
                "type": item_type,
                "url": resolved_url,
                "commands": {
                    "single": f"python run.py -u \"{resolved_url}\"",
                    "with_config": f"# 1. 复制配置文件\\ncp config.example.yml config.yml\\n\\n# 2. 编辑 config.yml 添加你的链接\\n\\n# 3. 运行\\npython run.py -c config.yml"
                },
                "docker": f"docker build -t douyin-downloader . && docker run -v $(pwd)/downloads:/app/Downloaded douyin-downloader"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/proxy-download")
async def proxy_download(url: str = Query(...), filename: Optional[str] = Query(None)):
    """代理下载文件（如果允许跨域下载）"""
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(url, headers=headers)
            
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            return StreamingResponse(
                response.iter_bytes(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename or "download"}"'
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0"}


# Vercel 入口
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
