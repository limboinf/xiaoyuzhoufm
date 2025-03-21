# 小宇宙播客下载与转录工具

这是一个基于 Streamlit 开发的工具，可以帮助用户下载小宇宙播客音频并将其转录为文字。（个人自用）

## 功能特点

- 🎵 支持小宇宙播客音频下载
- 📝 音频转文字转录功能
- 🎯 支持导出 TXT 和 SRT 格式
- 💻 简洁直观的 Web 界面
- ⏱️ 实时显示下载和转录进度
- 📊 显示音频时长和文件大小信息

## 截图
<img src="https://raw.githubusercontent.com/limboinf/xiaoyuzhoufm/refs/heads/main/usage1.png" width="600"/>

<img src="https://raw.githubusercontent.com/limboinf/xiaoyuzhoufm/refs/heads/main/usage2.png" width="600"/>

## 安装说明

1. 克隆项目到本地：

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动应用：
```bash
streamlit run src/app.py
```

2. 在浏览器中打开显示的地址（通常是 http://localhost:8501）

3. 使用步骤：
   - 在输入框中粘贴小宇宙播客链接
   - 点击"开始下载"按钮下载音频
   - 选择转录设备（CPU）和输出格式（TXT/SRT）
   - 点击"开始转录"进行音频转文字
   - 下载生成的转录文件

## 注意事项

- 转录速度与设备性能相关，一分钟音频约需要 10 秒转录时间

## 技术栈

- Python
- Streamlit
- PyDub
- Torch
- Fast-Whisper

## Prompt
见prompt.txt, 配合 deepseek r1 对播客内容进行总结和分析，示例：

<img width="1191" alt="image" src="https://github.com/user-attachments/assets/d4c69b9a-e654-4ea6-8289-f973705f6a48" />

