# 🎵 抖音视频下载器 Web 版

基于 [douyin-downloader](https://github.com/jiji262/douyin-downloader) 的 Web 界面版本。

## ✨ 功能特性

- 🎬 单视频下载（无水印）
- 🖼️ 图集下载
- 📁 合集批量下载
- 🎵 音乐下载
- 👤 用户主页批量下载
- 🌐 支持短链接自动解析

## 🚀 部署到 Vercel

### 1. 准备 GitHub 仓库

你需要先将此代码推送到你的 GitHub 账号：

```bash
# 1. 在 GitHub 上创建新仓库（不要初始化）
# 访问 https://github.com/new 创建名为 douyin-downloader 的仓库

# 2. 推送代码
cd douyin-downloader-fork
git remote remove origin
git remote add origin https://github.com/goddamn1999/douyin-downloader.git
git add .
git commit -m "Add web interface"
git push -u origin main
```

### 2. 部署到 Vercel

**方式一：使用 Vercel CLI**

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录并部署
vercel login
vercel --prod
```

**方式二：GitHub 自动部署**

1. 访问 [Vercel](https://vercel.com) 并登录
2. 点击 "Add New Project"
3. 导入你的 GitHub 仓库 `goddamn1999/douyin-downloader`
4. 点击 "Deploy"

### 3. 配置环境变量（可选）

如果你需要下载私密视频或大量内容，建议配置 Cookie：

1. 在 Vercel 项目设置中添加环境变量：
   - `DOUYIN_COOKIE`: 你的抖音登录 Cookie

2. 获取 Cookie 方法：
   - 登录抖音网页版
   - 打开浏览器开发者工具 (F12)
   - 找到 Application/Storage > Cookies
   - 复制 `sessionid` 或相关 cookie 值

## 📁 项目结构

```
.
├── api/
│   └── index.py          # FastAPI 后端 API
├── templates/
│   └── index.html        # Web 界面
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── app.js        # 前端逻辑
├── vercel.json           # Vercel 配置
├── requirements.txt      # Python 依赖
└── README.md
```

## 🔧 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行开发服务器
python api/index.py

# 3. 访问 http://localhost:8000
```

## ⚠️ 免责声明

本项目仅供学习研究使用，请遵守相关法律法规：
- 不要侵犯他人版权和隐私
- 不要用于商业用途
- 遵守抖音平台的使用条款

## 📝 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

## 🙏 致谢

基于 [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) 构建
