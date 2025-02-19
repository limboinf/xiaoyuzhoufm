import streamlit as st
import torch
import time
import os
from pydub import AudioSegment

torch.classes.__path__ = []

from download import fetch_audio_file
from transcribe import transcribe_audio

st.title("xiaoyuzhou FM 播客下载与转录工具")

# 初始化会话状态
if "download_completed" not in st.session_state:
    st.session_state.download_completed = False
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "podcast_title" not in st.session_state:
    st.session_state.podcast_title = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None


def format_duration(seconds: float) -> str:
    """将秒数转换为可读的时分秒格式"""
    seconds = round(seconds)  # 四舍五入到整数秒
    
    hours = seconds // 3600
    remaining = seconds % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours}小时")
    if minutes > 0 or hours > 0:  # 如果有小时也显示分钟
        time_parts.append(f"{minutes}分")
    time_parts.append(f"{seconds}秒")
    
    return "".join(time_parts)

# 下载部分
download_expander = st.expander(
    "第一步：下载播客", expanded=not st.session_state.download_completed
)
with download_expander:
    url = st.text_input("请输入小宇宙播客链接：")

    if st.button("开始下载"):
        if url:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:

                def update_progress(progress):
                    progress_bar.progress(progress)
                    status_text.text(f"下载进度：{int(progress * 100)}%")

                st.session_state.audio_path, st.session_state.podcast_title = (
                    fetch_audio_file(url, update_progress)
                )
                st.session_state.download_completed = True
                status_text.text("下载完成！")
                st.success(f"成功下载播客：{st.session_state.podcast_title}")
            except Exception as e:
                st.error(f"下载失败：{str(e)}")
        else:
            st.warning("请输入有效的播客链接")

# 常驻显示下载后的音频播放器
if st.session_state.download_completed:
    st.text(st.session_state.podcast_title)
    # 获取音频时长
    audio = AudioSegment.from_file(st.session_state.audio_path)
    duration = audio.duration_seconds
    readable_duration = format_duration(duration)
    st.text(f"音频长度：{readable_duration}")
    st.text(f"音频大小：{os.path.getsize(st.session_state.audio_path) / 1024 / 1024:.2f} MB")
    st.audio(st.session_state.audio_path)

# 转录部分
transcribe_expander = st.expander(
    "第二步：转录音频", expanded=st.session_state.download_completed
)
with transcribe_expander:
    if st.session_state.download_completed:
        st.info("提示: 一分钟的音频大约需要10秒钟转录时间(不同设备转录时间不同)")

        # 设备选择
        device_options = ["CPU"]
        selected_device = st.selectbox("选择运行设备：", device_options)

        # 转换设备选择为程序可用的格式
        device_map = {"CPU": "cpu"}

        # 格式选择
        output_format = st.selectbox("选择输出格式：", ["txt", "srt"])

        if st.button("开始转录", disabled=st.session_state.get('is_transcribing', False)):
            try:
                status_text = st.empty()
                st.session_state.is_transcribing = True
                status_text.text("转录中...")

                # 设置输出文件名
                output_file = f"{st.session_state.podcast_title}.{output_format}"

                # 记录开始时间
                start_time = time.time()

                audio_length_minutes = duration / 60
                estimated_time = audio_length_minutes * 6  # 每分钟6秒的转录时间
                st.info(f"预计转录时间：{estimated_time/60:.2f} 分钟")

                # 开始转录
                transcribe_audio(
                    st.session_state.audio_path,
                    output_file,
                    output_format,
                    device_map[selected_device],
                )

                # 计算耗时
                elapsed_time = time.time() - start_time
                status_text.text("转录完成！")

                # 读取并显示转录结果
                with open(output_file, "r", encoding="utf-8") as f:
                    st.session_state.transcript = f.read()

                st.success(f"转录完成！耗时：{elapsed_time:.2f}秒")
                st.download_button(
                    label="下载转录文件",
                    data=st.session_state.transcript,
                    file_name=output_file,
                    mime="text/plain",
                )
                st.session_state.is_transcribing = False

            except Exception as e:
                st.error(f"转录失败：{str(e)}")
                st.session_state.is_transcribing = False
    else:
        st.info("请先完成播客下载")

# 转录结果显示
if st.session_state.transcript:
    st.subheader("转录文稿")
    st.text_area("转录预览", st.session_state.transcript, height=300)
