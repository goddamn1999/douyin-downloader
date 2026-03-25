const API_BASE = window.location.origin;

async function downloadVideo() {
    const urlInput = document.getElementById('videoUrl');
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('请输入抖音视频链接');
        return;
    }
    
    // 显示加载状态
    showLoading();
    setButtonLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResult(data);
        } else {
            showError(data.message || '解析失败，请检查链接是否正确');
        }
    } catch (error) {
        showError('请求失败，请稍后重试');
        console.error(error);
    } finally {
        setButtonLoading(false);
    }
}

function showResult(data) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('result').style.display = 'block';
    
    const video = data.data;
    
    // 设置封面
    document.getElementById('cover').src = video.cover || '/static/images/default-cover.jpg';
    
    // 设置标题
    document.getElementById('title').textContent = video.title || '无标题';
    
    // 设置作者
    document.getElementById('author').textContent = `👤 ${video.author || '未知作者'}`;
    
    // 设置描述
    document.getElementById('desc').textContent = video.desc || '';
    
    // 设置下载链接
    const videoBtn = document.getElementById('downloadVideo');
    const audioBtn = document.getElementById('downloadAudio');
    
    if (video.video_url) {
        videoBtn.href = `/api/download?url=${encodeURIComponent(video.video_url)}&filename=${encodeURIComponent(video.title || 'video')}.mp4`;
        videoBtn.style.display = 'inline-block';
    } else {
        videoBtn.style.display = 'none';
    }
    
    if (video.audio_url) {
        audioBtn.href = `/api/download?url=${encodeURIComponent(video.audio_url)}&filename=${encodeURIComponent(video.title || 'audio')}.mp3`;
        audioBtn.style.display = 'inline-block';
    } else {
        audioBtn.style.display = 'none';
    }
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'block';
    document.getElementById('errorMsg').textContent = message;
}

function showLoading() {
    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
}

function setButtonLoading(loading) {
    const btn = document.getElementById('downloadBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    btn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoading.style.display = loading ? 'inline' : 'none';
}

// 回车键提交
document.getElementById('videoUrl').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        downloadVideo();
    }
});
