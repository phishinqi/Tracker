import asyncio
import aiohttp
import os

# 检查网络连接
async def check_internet_connection(session):
    try:
        await session.head('https://www.google.com', timeout=5)
        return True
    except aiohttp.ClientConnectionError:
        return False

# 异步下载 main_url.txt
async def download_main_url():
    if not await check_internet_connection(aiohttp.ClientSession()):
        print("网络连接不可用，请检查您的网络设置。")
        return
    url_file_path = os.getcwd()
    print("当前文件路径：", url_file_path)
    url_path = os.path.join(url_file_path, 'main_url.txt')
    if os.path.exists(url_path):
        print("main_url.txt 文件已存在。")
    else:
        print("main_url.txt 文件不存在，正在下载...")
        main_url = "https://raw.githubusercontent.com/phishinqi/phishinqi.github.io/main/assets/txt/trackers_url.txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(main_url) as response:
                with open(url_path, 'wb') as out_file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        out_file.write(chunk)
            print("main_url.txt 文件下载完成。")

# 异步读取 URL 并写入 trackers.txt
async def fetch_and_write_trackers(session, urls, trackers_file_path):
    for url in urls:
        print(f"正在处理 URL: {url}")
        try:
            async with session.get(url) as res:
                html = await res.text()
            with open(trackers_file_path, 'a') as f:
                f.write(html + '\n')
            print("处理完成。")
        except aiohttp.ClientError as e:
            print(f"处理 URL {url} 时发生网络错误: {e}")

# 读取 main_url.txt 文件内容并输出 URL 列表
def read_urls():
    print("读取 URL 中...")
    with open('main_url.txt', 'r') as f:
        urls = [line.strip('\n') for line in f if line.strip('\n')]
    return urls

# 检查并创建 trackers.txt 文件
def prepare_trackers_file(file_path):
    if os.path.exists(file_path):
        print("trackers.txt 文件存在，正在清空内容...")
        with open(file_path, 'w') as files:
            pass  # 清空文件内容
    else:
        print("trackers.txt 文件不存在，正在创建...")
        with open(file_path, 'w') as file_trackers:
            pass  # 创建空文件
# 添加空白行
def remove_duplicates(input_file, output_file):
    print("正在去重...")
    with open(input_file, 'r') as f_read:
        lines = f_read.readlines()

    with open(output_file, 'w') as f_write:
        seen = set()
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            # 如果行不为空且未被见过，或者列表中的第一个元素，写入文件
            if stripped_line not in seen or i == 0:
                seen.add(stripped_line)
                f_write.write(line)
                # 如果当前行不是列表中的最后一个元素且下一个行不为空，则添加一个空白行
                if i < len(lines) - 1 and lines[i + 1].strip():
                    f_write.write('\n')

    print("去重完成。")

# 主函数
async def main():
    await download_main_url()
    urls = read_urls()
    trackers_file_path = os.path.join(os.getcwd(), 'trackers.txt')
    prepare_trackers_file(trackers_file_path)
    async with aiohttp.ClientSession() as session:
        await fetch_and_write_trackers(session, urls, trackers_file_path)
    remove_duplicates('./trackers.txt', './output_trackers.txt')

if __name__ == "__main__":
    asyncio.run(main())
