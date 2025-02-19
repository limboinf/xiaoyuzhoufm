import argparse
from faster_whisper import WhisperModel

from datetime import timedelta


def format_timestamp(seconds):
    """将秒转换为 SRT 时间格式：HH:MM:SS,mmm"""
    millisec = int((seconds - int(seconds)) * 1000)
    return str(timedelta(seconds=int(seconds))) + f",{millisec:03d}"


def generate_srt(segments):
    """将转录片段转换为 SRT 格式"""
    srt = []
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        srt.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt)


def generate_txt(segments):
    """将转录片段转换为纯文本格式"""
    return "\n".join(segment.text.strip() for segment in segments)


def transcribe_audio(audio_path, output_file, output_format="txt", device_option='cpu'):
    print(f"audio path: {audio_path}, output file: {output_file}, output format: {output_format}, device option: {device_option}")

    # 根据设备设置计算类型：GPU 使用 float16，其它使用 int8
    compute_type = "float16" if device_option == "cuda" else "int8"

    # 加载 faster‑whisper 模型，指定模型大小为 "base"
    model = WhisperModel("base", device=device_option, compute_type=compute_type)
    print("Whisper 模型已加载。")

    # 使用 faster‑whisper 进行音频转录，beam_size 设置为 5
    segments, info = model.transcribe(audio_path, beam_size=5)
    print("音频转录完成。")
    print("检测到语言：%s (概率: %f)" % (info.language, info.language_probability))

    # 根据输出格式生成内容
    if output_format.lower() == "srt":
        content = generate_srt(segments)
    else:  # 默认为 txt 格式
        content = generate_txt(segments)

    # 将内容保存到文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

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
    args = parser.parse_args()

    transcribe_audio(args.input, args.output, args.format, args.device)
