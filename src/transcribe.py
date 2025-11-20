import argparse
from faster_whisper import WhisperModel
from datetime import timedelta
import os
import time
from functools import lru_cache


@lru_cache(maxsize=8)
def get_whisper_model(model_size="turbo", device="cpu", compute_type="int8"):
    """获取 Whisper 模型，使用 LRU 缓存避免重复加载"""
    print(f"加载 Whisper 模型 ({model_size}) 到 {device}...")
    start_time = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    load_time = time.time() - start_time
    print(f"模型加载完成，耗时 {load_time:.2f} 秒")
    return model


def format_timestamp(seconds):
    """将秒转换为 SRT 时间格式：HH:MM:SS,mmm (优化版)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisec = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisec:03d}"


def generate_srt(segments):
    """将转录片段转换为 SRT 格式 (流式处理，减少内存使用)"""
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        yield f"{i}\n{start_time} --> {end_time}\n{text}\n"


def generate_txt(segments):
    """将转录片段转换为纯文本格式"""
    return "\n".join(segment.text.strip() for segment in segments)


def transcribe_audio(audio_path, output_file, output_format="txt", device_option=None, beam_size=5, show_progress=True):
    """使用 faster-whisper 模型进行音频转录 (优化版)"""
    start_time = time.time()
    
    if show_progress:
        print(f"音频路径: {audio_path}")
        print(f"输出文件: {output_file}")
        print(f"输出格式: {output_format}")
        print(f"设备选项: {device_option or 'auto'}")
        print(f"Beam size: {beam_size}")
    
    # 获取文件大小用于进度显示
    audio_size = os.path.getsize(audio_path)
    if show_progress:
        print(f"音频文件大小: {audio_size / (1024*1024):.2f} MB")
    
    # 根据设备设置计算类型：GPU 使用 float16，其它使用 int8
    compute_type = "float16" if device_option == "cuda" else "int8"
    
    # 获取缓存的模型
    model = get_whisper_model("turbo", device_option, compute_type)
    
    # 使用 faster-whisper 进行音频转录
    if show_progress:
        print("开始音频转录...")
    
    segments, info = model.transcribe(audio_path, beam_size=beam_size)
    
    if show_progress:
        print("音频转录完成！")
        print(f"检测到语言：{info.language} (概率: {info.language_probability:.3f})")
        
        # 估算处理时间
        processing_time = time.time() - start_time
        audio_duration = info.duration
        speed_ratio = audio_duration / processing_time if processing_time > 0 else 0
        print(f"音频时长: {audio_duration:.2f} 秒")
        print(f"处理耗时: {processing_time:.2f} 秒")
        print(f"处理速度: {speed_ratio:.2f}x 实时")
    
    # 根据输出格式生成内容
    if output_format.lower() == "srt":
        content = "\n".join(generate_srt(segments))
    else:  # 默认为 txt 格式
        content = "\n".join(segment.text.strip() for segment in segments)
    
    # 将内容保存到文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    if show_progress:
        print(f"转录文本已保存到文件：{output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用 faster‑whisper 模型进行音频转录。")
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入音频文件的路径，例如：audio_files/episode_audio.mp3"
    )
    parser.add_argument(
        "-o", "--output",
        default="transcription_output.txt",
        help="转录文本的输出文件路径，默认为 transcription_output.txt"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "srt"],
        default="txt",
        help="输出文件格式，支持 txt（纯文本）或 srt（字幕文件格式），默认为 txt"
    )
    parser.add_argument(
        "-d", "--device",
        default=None,
        help="指定使用的设备，例如：cuda、cpu 或 mps（MPS 可能因部分算子不支持而自动回退使用 CPU）"
    )
    parser.add_argument(
        "-b", "--beam-size",
        type=int,
        default=5,
        help="beam search 大小，默认为 5，值越大质量越好但速度越慢"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="不显示进度信息"
    )
    args = parser.parse_args()

    transcribe_audio(args.input, args.output, args.format, args.device, args.beam_size, not args.no_progress)
