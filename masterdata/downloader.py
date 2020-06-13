import asyncio
import string
from urllib.parse import quote
from urllib.request import urlopen

import aiohttp

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4090.0 Safari/537.36 Edg/83.0.467.0 '}


def download_file(url, timeout=10):
    url = quote(url, safe=string.printable)
    return urlopen(url, timeout=timeout).read()


def download_files(urls, concurrency_limit=10, headers=None):
    async def async_download(sem, session: aiohttp.ClientSession, url):
        async with sem, session.get(url) as response:
            assert response.status == 200
            return await response.read()

    async def main():
        sem = asyncio.Semaphore(concurrency_limit)
        _headers = headers or DEFAULT_HEADERS
        async with aiohttp.ClientSession(headers=_headers) as session:
            tasks = [async_download(sem, session, url) for url in urls]
            res = asyncio.gather(*tasks)
            return await res

    return asyncio.get_event_loop().run_until_complete(main())
