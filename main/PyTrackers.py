import asyncio
import aiohttp
import os
from aiologger import Logger
from tqdm import tqdm
import aiofiles

logger = Logger.with_default_handlers(name='my_async_logger')

async def download_main_url():
    main_url = "https://raw.githubusercontent.com/phishinqi/phishinqi.github.io/refs/heads/main/assets/txt/trackers_url.txt"
    
    if os.path.exists('main_url.txt'):
        logger.info("main_url.txt 文件已存在，跳过下载。")
        return

    logger.info("正在下载 main_url.txt 文件...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(main_url) as response:
                response.raise_for_status()
                content = await response.text()

        async with aiofiles.open('main_url.txt', 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info("main_url.txt 文件下载完成。")
    except aiohttp.ClientError as e:
        logger.error(f"下载 main_url.txt 时发生网络错误: {e}")

async def fetch_and_write_trackers(session, urls, trackers_file_path):
    for url in tqdm(urls, desc="处理 URL", unit="个"):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

            async with aiofiles.open(trackers_file_path, 'a', encoding='utf-8') as f:
                await f.write(html + '\n')
        except aiohttp.ClientError as e:
            logger.error(f"处理 URL {url} 时发生网络错误: {e}")

def read_urls():
    logger.info("读取 URL 中...")
    if not os.path.exists('main_url.txt'):
        logger.error("main_url.txt 文件不存在，无法读取 URL。")
        return []

    with open('main_url.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def prepare_trackers_file(file_path):
    if os.path.exists(file_path):
        logger.info("original_trackers.txt 文件存在，正在清空内容...")
        with open(file_path, 'w', encoding='utf-8'):
            pass
    else:
        logger.info("original_trackers.txt 文件不存在，正在创建...")

    with open(file_path, 'w', encoding='utf-8'):
        pass

async def remove_duplicates(input_file, output_file):
    logger.info("正在去重...")
    seen = set()

    async with aiofiles.open(input_file, 'r', encoding='utf-8') as f_read:
        async for line in f_read:
            stripped_line = line.strip()
            if stripped_line and stripped_line not in seen:
                async with aiofiles.open(output_file, 'a', encoding='utf-8') as f_write:
                    await f_write.write(stripped_line + '\n')
                seen.add(stripped_line)

    logger.info("去重完成。")

async def main():
    await download_main_url()
    urls = read_urls()
    original_trackers_file_path = 'original_trackers.txt'
    
    prepare_trackers_file(original_trackers_file_path)

    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, original_trackers_file_path)

    await remove_duplicates(original_trackers_file_path, 'output_trackers.txt')
    await logger.shutdown()

    if os.path.exists('main_url.txt'):
        os.remove('main_url.txt')
        logger.info("main_url.txt 文件已删除。")

if __name__ == "__main__":
    asyncio.run(main())
