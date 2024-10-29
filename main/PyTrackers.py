import asyncio
import aiohttp
import os
from aiologger import Logger
from tqdm import tqdm
import aiofiles
from urllib.parse import urlparse

# 定义常量
MAIN_URL_FILE = 'main_url.txt'
ORIGINAL_TRACKERS_FILE = 'original_trackers.txt'
OUTPUT_TRACKERS_FILE = 'output_trackers.txt'
MAIN_URL = "https://raw.githubusercontent.com/phishinqi/phishinqi.github.io/refs/heads/main/assets/txt/trackers_url.txt"

logger = Logger.with_default_handlers(name='my_async_logger')

def is_valid_url(url):
    """检查 URL 是否有效"""
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

async def download_main_url():
    """下载主 URL 文件，如果已存在则跳过，并检查 URL 格式"""
    if not is_valid_url(MAIN_URL):
        logger.error(f"无效的 URL {MAIN_URL}，请检查。")
        return

    if os.path.exists(MAIN_URL_FILE):
        logger.info(f"{MAIN_URL_FILE} 文件已存在，跳过下载。")
        return

    logger.info(f"正在下载 {MAIN_URL_FILE} 文件...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(MAIN_URL) as response:
                response.raise_for_status()
                content = await response.text()

        async with aiofiles.open(MAIN_URL_FILE, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info(f"{MAIN_URL_FILE} 文件下载完成。")
    except aiohttp.ClientError as e:
        logger.error(f"下载 {MAIN_URL} 时发生网络错误: {e}")

async def read_urls():
    """读取 URL 列表"""
    if not os.path.exists(MAIN_URL_FILE):
        logger.error(f"{MAIN_URL_FILE} 文件不存在！")
        return []

    async with aiofiles.open(MAIN_URL_FILE, 'r', encoding='utf-8') as f:
        urls = await f.readlines()
    return [url.strip() for url in urls if url.strip()]

async def prepare_trackers_file(file_name):
    """准备 trackers 文件，删除旧文件（如果存在）并创建新文件"""
    if os.path.exists(file_name):
        os.remove(file_name)
        logger.info(f"已删除旧的 {file_name} 文件。")
    
    async with aiofiles.open(file_name, 'w', encoding='utf-8') as f:
        await f.write("")  # 创建空文件

async def fetch_and_write_trackers(session, urls, output_file):
    """异步下载 trackers 并写入文件"""
    logger.info("正在下载 trackers...")
    contents = []
    
    for url in tqdm(urls, desc="下载中", unit="个"):
        try:
            async with session.get(url, timeout=30) as response:  # 增加超时时间
                response.raise_for_status()
                content = await response.text()
                contents.append(content)
        except aiohttp.ClientError as e:
            logger.error(f"下载 {url} 时发生网络错误: {e}")
    
    # 一次性写入下载的内容
    if contents:
        async with aiofiles.open(output_file, 'a', encoding='utf-8') as f_write:
            await f_write.write('\n'.join(contents) + '\n')

async def remove_duplicates(input_file, output_file):
    """从输入文件中移除重复行并写入输出文件"""
    logger.info("正在去重...")
    seen = set()

    try:
        async with aiofiles.open(input_file, 'r', encoding='utf-8') as f_read:
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f_write:
                processed_lines = 0
                async for line in f_read:
                    processed_lines += 1
                    stripped_line = line.strip()
                    if stripped_line and stripped_line not in seen:
                        seen.add(stripped_line)
                        await f_write.write(stripped_line + '\n')
                    if processed_lines % 1000 == 0:
                        logger.info(f"已处理 {processed_lines} 行")
                        
        logger.info("去重完成。")
        
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"文件处理错误: {e}")
    except Exception as e:
        logger.error(f"去重过程中发生错误: {e}")

async def main():
    """主程序执行入口"""
    await download_main_url()
    urls = await read_urls()
    
    if not urls:
        logger.error("没有可处理的 URL，请检查 main_url.txt 文件。")
        return
    
    await prepare_trackers_file(ORIGINAL_TRACKERS_FILE)

    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, ORIGINAL_TRACKERS_FILE)

    await remove_duplicates(ORIGINAL_TRACKERS_FILE, OUTPUT_TRACKERS_FILE)
    await logger.shutdown()

    # 删除 MAIN_URL_FILE 文件前的安全检查
    try:
        if os.path.exists(MAIN_URL_FILE):
            os.remove(MAIN_URL_FILE)
            logger.info(f"{MAIN_URL_FILE} 文件已删除。")
    except OSError as e:
        logger.error(f"删除 {MAIN_URL_FILE} 文件时发生错误: {e}")

asyncio.run(main())  # 使用 asyncio.run 运行主程序



