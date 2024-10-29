import asyncio
import aiohttp
import os
from aiologger import Logger
from tqdm import tqdm
import aiofiles  # 使用 aiofiles 进行异步文件操作

# 创建一个异步日志记录器
logger = Logger.with_default_handlers(name='my_async_logger')

async def download_main_url():
    main_url = "https://raw.githubusercontent.com/phishinqi/phishinqi.github.io/refs/heads/main/assets/txt/trackers_url.txt"
    
    if os.path.exists('main_url.txt'):
        logger.info("main_url.txt 文件已存在，跳过下载。")
        return

    logger.info("正在下载 main_url.txt 文件...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(main_url) as res:
                res.raise_for_status()
                content = await res.text()

        async with aiofiles.open('main_url.txt', 'w', encoding='utf-8') as f:
            await f.write(content)
        logger.info("main_url.txt 文件下载完成。")
    except aiohttp.ClientError as e:
        logger.error(f"下载 main_url.txt 时发生网络错误: {e}")

async def fetch_and_write_trackers(session, urls, trackers_file_path):
    for url in tqdm(urls, desc="处理 URL", unit="个"):
        try:
            async with session.get(url) as res:
                res.raise_for_status()
                html = await res.text()
            async with aiofiles.open(trackers_file_path, 'a', encoding='utf-8') as f:
                await f.write(html + '\n')
        except aiohttp.ClientError as e:
            logger.error(f"处理 URL {url} 时发生网络错误: {e}")

def read_urls():
    logger.info("读取 URL 中...")
    with open('main_url.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def prepare_trackers_file(file_path):
    if os.path.exists(file_path):
        logger.info("original_trackers.txt 文件存在，正在清空内容...")
        with open(file_path, 'w', encoding='utf-8') as files:
            pass  # 清空文件内容
    else:
        logger.info("original_trackers.txt 文件不存在，正在创建...")
        with open(file_path, 'w', encoding='utf-8') as file_trackers:
            pass  # 创建空文件

async def remove_duplicates(input_file, output_file):
    logger.info("正在去重...")
    async with aiofiles.open(input_file, 'r', encoding='utf-8') as f_read:
        lines = await f_read.readlines()

    seen = set()
    line_count = 0  # 记录写入的行数

    async with aiofiles.open(output_file, 'w', encoding='utf-8') as f_write:
        for line in lines:
            stripped_line = line.strip()

            # 只写入非空行，并且未被记录的行
            if stripped_line and stripped_line not in seen:
                await f_write.write(line)  # 写入当前行
                seen.add(stripped_line)  # 添加到集合中以跟踪已见行
                line_count += 1  # 更新行计数

                # 每写入两行后添加一个空行
                if line_count % 2 == 0:
                    await f_write.write('\n')  # 写入一个空行

    logger.info("去重完成。")



async def main():
    await download_main_url()  # 下载 main_url.txt
    urls = read_urls()  # 读取 URL
    original_trackers_file_path = 'original_trackers.txt'
    prepare_trackers_file(original_trackers_file_path)  # 准备 original_trackers 文件
    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, original_trackers_file_path)  # 获取并写入 original_trackers
    await remove_duplicates(original_trackers_file_path, 'output_trackers.txt')  # 去重并保存输出文件
    await logger.shutdown()

    # 删除 main_url.txt 文件
    if os.path.exists('main_url.txt'):
        os.remove('main_url.txt')
        logger.info("main_url.txt 文件已删除。")


# 运行主函数
asyncio.run(main())
