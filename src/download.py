import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
from tqdm import tqdm


def fetch_audio_file(url, progress_callback=None):
    print(f"downloading {url}")
    # 设置Selenium的Chrome浏览器选项
    start_time = time.time()
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
    chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
    # 添加新的选项以提高稳定性
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # 不指定Service，让Selenium自动查找chromedriver（需确保chromedriver在环境变量中）
    driver = webdriver.Chrome(options=chrome_options)
    end_time = time.time()
    print(f"driver init time: {end_time - start_time} seconds")
    # # 设置页面加载超时时间
    # driver.set_page_load_timeout(30)
    # # 设置脚本执行超时时间
    # driver.set_script_timeout(60)

    try:
        # 加载目标网页
        print("正在加载页面...")
        driver.get(url)
        end_time = time.time()
        print(f"page load time: {end_time - start_time} seconds")

        # 1. 获取播客标题
        #   - 如果 class 名称中包含较多动态信息（如 "jsx-399326063 title"），
        #     建议用 XPATH 的方式做部分匹配，避免以后 class 变化导致抓取失败。
        #   - 例如: //h1[contains(@class,'title')]
        title_element = driver.find_element(By.XPATH, "//h1[contains(@class,'title')]")
        podcast_title = title_element.text
        print("播客标题:", podcast_title)

        # 2. 查找网页中的 <audio> 标签，获取音频 URL
        audio_element = driver.find_element(By.TAG_NAME, "audio")
        audio_url = audio_element.get_attribute("src")
        if not audio_url:
            print("网页中未找到音频文件。")
            return

        # 3. 下载音频文件
        response = requests.get(audio_url, stream=True, verify=False)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        
        os.makedirs("audio_files", exist_ok=True)
        audio_path = os.path.join("audio_files", f"{podcast_title}-episode_audio.mp3")

        if total_size > 0:
            downloaded = 0
            with open(audio_path, 'wb') as audio_file:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    audio_file.write(data)
                    if progress_callback:
                        progress = (downloaded / total_size)
                        progress_callback(progress)
            
            print(f"音频文件已保存到 {audio_path}")
            return audio_path, podcast_title
        else:
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(response.content)
            print(f"音频文件已保存到 {audio_path}")
            return audio_path, podcast_title

    finally:
        driver.quit()

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="下载小宇宙播客音频文件")
#     parser.add_argument(
#         "-u", "--url",
#         type=str,
#         help="播客页面 URL",
#         required=True
#     )
#     args = parser.parse_args()
#     fetch_audio_file(args.url)

