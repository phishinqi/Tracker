import asyncio
import aiohttp
import os
from aiologger import Logger

# 创建一个异步日志记录器
logger = Logger.with_default_handlers(name='my_async_logger')

async def download_main_url():
    main_url = "https://raw.githubusercontent.com/phishinqi/phishinqi.github.io/refs/heads/main/assets/txt/trackers_url.txt"
    logger.info("正在下载 main_url.txt 文件...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(main_url) as res:
                res.raise_for_status()  # 检查响应状态
                content = await res.text()
        
        with open('main_url.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info("main_url.txt 文件下载完成。")
    except aiohttp.ClientError as e:
        logger.error(f"下载 main_url.txt 时发生网络错误: {e}")

async def fetch_and_write_trackers(session, urls, trackers_file_path):
    for url in urls:
        logger.info(f"正在处理 URL: {url}")
        try:
            async with session.get(url) as res:
                res.raise_for_status()  # 检查响应状态
                html = await res.text()
            with open(trackers_file_path, 'a', encoding='utf-8') as f:
                f.write(html + '\n')
            logger.info("处理完成。")
        except aiohttp.ClientError as e:
            logger.error(f"处理 URL {url} 时发生网络错误: {e}")

def read_urls():
    logger.info("读取 URL 中...")
    with open('main_url.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def prepare_trackers_file(file_path):
    if os.path.exists(file_path):
        logger.info("trackers.txt 文件存在，正在清空内容...")
        with open(file_path, 'w', encoding='utf-8') as files:
            pass  # 清空文件内容
    else:
        logger.info("trackers.txt 文件不存在，正在创建...")
        with open(file_path, 'w', encoding='utf-8') as file_trackers:
            pass  # 创建空文件

def remove_duplicates(input_file, output_file):
    logger.info("正在去重...")
    with open(input_file, 'r', encoding='utf-8') as f_read:
        lines = f_read.readlines()

    with open(output_file, 'w', encoding='utf-8') as f_write:
        seen = set()
        blank_line_needed = False

        for line in lines:
            stripped_line = line.strip()
            if stripped_line not in seen or not stripped_line:
                if blank_line_needed and stripped_line:
                    f_write.write('\n')  # 添加一个空白行
                seen.add(stripped_line)
                f_write.write(line)  # 写入当前行
                blank_line_needed = not stripped_line  # 如果当前行是空行，则下一次不需要添加空白行
            else:
                blank_line_needed = True  # 如果当前行是重复的，标记为需要空白行

    logger.info("去重完成。")

async def main():
    await download_main_url()  # 下载 main_url.txt
    urls = read_urls()  # 读取 URL
    trackers_file_path = 'trackers.txt'
    prepare_trackers_file(trackers_file_path)  # 准备 trackers 文件
    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, trackers_file_path)  # 获取并写入 trackers
    remove_duplicates('trackers.txt', 'output_trackers.txt')  # 去重
    await logger.shutdown()

# 运行主函数
asyncio.run(main())
