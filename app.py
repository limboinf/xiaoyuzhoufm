import time
import streamlit as st
import requests
from bs4 import BeautifulSoup
from io import BytesIO

st.title('xiaoyuzhou FM Audio Download')

# 初始化session_state变量
if 'audio_buffer' not in st.session_state:
    st.session_state['title'] = None
    st.session_state['audio_buffer'] = None


def download_audio(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.xiaoyuzhoufm.com/'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 确保请求成功

    soup = BeautifulSoup(response.content, 'html.parser')

    # 获取音频文件的标题和下载地址
    title_tag = soup.find('meta', {'property': 'og:title'})
    audio_tag = soup.find('meta', {'property': 'og:audio'})

    if title_tag and audio_tag:
        title = title_tag['content']
        audio_url = audio_tag['content']

        # 流式下载音频文件
        with st.spinner(f'正在下载 {title}...'):
            audio_response = requests.get(audio_url, stream=True)
            audio_response.raise_for_status()

            # 尝试获取内容长度
            content_length = audio_response.headers.get('Content-Length')
            if content_length is not None:
                content_length = int(content_length)
                progress_bar = st.progress(0)
                status_text = st.empty()
                downloaded = 0
                start_time = time.time()

            # 创建一个缓冲区
            audio_buffer = BytesIO()
            for chunk in audio_response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉保持连接的新块
                    audio_buffer.write(chunk)
                    if content_length is not None:
                        downloaded += len(chunk)
                        progress = downloaded / content_length
                        progress_bar.progress(progress)

                        # 计算下载速度
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = downloaded / elapsed_time
                            # 将速度转换为 KB/s 并显示百分比和速度
                            speed_kb_s = speed / 1024
                            status_text.text(
                                f'已下载: {progress * 100:.2f}% - 速度: {speed_kb_s:.2f} KB/s')

            audio_buffer.seek(0)
            return audio_buffer, title
    return None


url = st.text_input("link:")


if url and st.button('下载音频'):
    # 当用户点击下载按钮时，执行下载
    audio_buffer, title = download_audio(url)
    st.session_state['title'] = title
    st.session_state['audio_buffer'] = audio_buffer


if st.session_state['title'] is not None:
    # 提供文件下载
    st.success(f"音频文件 {st.session_state['title']}.mp3 下载完成！")
    st.download_button(label="点击下载文件",
                       data=st.session_state['audio_buffer'],
                       file_name=f"{st.session_state['title']}.mp3",
                       mime="audio/mpeg")

    st.session_state['title'] = None
    st.session_state['audio_buffer'] = None