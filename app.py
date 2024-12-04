"""
小宇宙FM音频下载器
此脚本用于下载小宇宙FM平台的音频文件。使用Streamlit构建Web界面，
支持进度显示和下载速度实时更新。
"""

import time
import streamlit as st
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# 设置应用标题
st.title('xiaoyuzhou FM Audio Download')

# 初始化session_state变量，用于存储下载的音频数据和标题
if 'audio_buffer' not in st.session_state:
    st.session_state['title'] = None
    st.session_state['audio_buffer'] = None


def download_audio(url):
    """
    下载音频文件的主要函数
    
    Args:
        url (str): 小宇宙FM单集的URL地址
        
    Returns:
        tuple: (BytesIO, str) 包含音频数据的缓冲区和音频标题
        None: 如果下载失败
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.xiaoyuzhoufm.com/'
    }

    # 发送HTTP请求获取页面内容
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 确保请求成功

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 从页面元数据中提取音频标题和URL
    title_tag = soup.find('meta', {'property': 'og:title'})
    audio_tag = soup.find('meta', {'property': 'og:audio'})

    if title_tag and audio_tag:
        title = title_tag['content']
        audio_url = audio_tag['content']

        # 开始下载音频文件，显示进度条
        with st.spinner(f'正在下载 {title}...'):
            audio_response = requests.get(audio_url, stream=True)
            audio_response.raise_for_status()

            # 获取文件大小用于显示下载进度
            content_length = audio_response.headers.get('Content-Length')
            if content_length is not None:
                content_length = int(content_length)
                progress_bar = st.progress(0)
                status_text = st.empty()
                downloaded = 0
                start_time = time.time()

            # 创建内存缓冲区存储音频数据
            audio_buffer = BytesIO()
            # 分块下载音频文件
            for chunk in audio_response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉保持连接的新块
                    audio_buffer.write(chunk)
                    if content_length is not None:
                        # 更新下载进度和速度
                        downloaded += len(chunk)
                        progress = downloaded / content_length
                        progress_bar.progress(progress)

                        # 计算并显示下载速度
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = downloaded / elapsed_time
                            speed_kb_s = speed / 1024
                            status_text.text(
                                f'已下载: {progress * 100:.2f}% - 速度: {speed_kb_s:.2f} KB/s')

            audio_buffer.seek(0)
            return audio_buffer, title
    return None


# 创建URL输入框
url = st.text_input("link:")


# 当点击下载按钮时执行下载操作
if url and st.button('下载音频'):
    audio_buffer, title = download_audio(url)
    st.session_state['title'] = title
    st.session_state['audio_buffer'] = audio_buffer


# 如果下载完成，显示下载按钮
if st.session_state['title'] is not None:
    st.success(f"音频文件 {st.session_state['title']}.mp3 下载完成！")
    st.download_button(label="点击下载文件",
                       data=st.session_state['audio_buffer'],
                       file_name=f"{st.session_state['title']}.mp3",
                       mime="audio/mpeg")

    # 下载完成后清理session状态
    st.session_state['title'] = None
    st.session_state['audio_buffer'] = None