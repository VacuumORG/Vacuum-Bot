import asyncio
import ssl
from typing import List

import aiohttp
import certifi

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
HEADERS = {'User-Agent': USER_AGENT}


async def do_single_fetch(session, url, raise_exception: bool):
    print(f"Start fetching URL: {url}")

    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Fetch error | {response.status} | {url}")
            if raise_exception:
                response.raise_for_status()
        print(f"Done fetching URL: {url}")
        return url, await response.text()


async def fetch_urls(urls: List[str], raise_exception: bool = False):
    # Foi necessário adicionar essa etapa de ssl pois usar apenas o aiohttp estava dando exception de certificação
    # Importante checar se essa solução é a ideal. Por enquanto resolveu o problema.
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    tasks = []
    async with aiohttp.ClientSession(connector=conn) as session:
        for url in urls:
            task = asyncio.create_task(do_single_fetch(session, url, raise_exception))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return dict(results)