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
    async with aiofiles.open(trackers_file_path, 'a', encoding='utf-8') as f:
        for url in tqdm(urls, desc="处理 URL", unit="个"):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    html = await response.text()
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
    logger.info("准备 trackers 文件...")
    # 无论文件存在与否，都清空内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.truncate()  # 确保文件内容被清空

async def remove_duplicates(input_file, output_file):
    logger.info("正在去重...")
    seen = set()

    try:
        async with aiofiles.open(input_file, 'r', encoding='utf-8') as f_read:
            async for line in f_read:
                stripped_line = line.strip()
                if stripped_line and stripped_line not in seen:
                    seen.add(stripped_line)
                    async with aiofiles.open(output_file, 'a', encoding='utf-8') as f_write:
                        await f_write.write(stripped_line + '\n')
        logger.info("去重完成。")
    except aiofiles.ioform.Error as e:  # 捕获特定的文件 I/O 异常
        logger.error(f"去重过程中发生文件 I/O 错误: {e}")
    except Exception as e:
        logger.error(f"去重过程中发生其他错误: {e}")

async def main():
    await download_main_url()
    urls = read_urls()
    
    if not urls:
        logger.error("没有可处理的 URL，请检查 main_url.txt 文件。")
        return
    
    original_trackers_file_path = 'original_trackers.txt'
    
    prepare_trackers_file(original_trackers_file_path)

    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, original_trackers_file_path)

    await remove_duplicates(original_trackers_file_path, 'output_trackers.txt')
    await logger.shutdown()

    # 删除 main_url.txt 文件前的安全检查
    if os.path.exists('main_url.txt'):
        try:
            os.remove('main_url.txt')
            logger.info("main_url.txt 文件已删除。")
        except Exception as e:
            logger.error(f"删除 main_url.txt 文件时发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
