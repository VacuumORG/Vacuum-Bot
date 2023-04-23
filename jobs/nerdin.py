import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # espera 5 segundos antes de prosseguir
            await asyncio.sleep(5)
            html = await response.text()
            return html

url = 'https://www.nerdin.com.br/vagas?UF=HO&PalavraChave=desenvolvedor'

loop = asyncio.get_event_loop()
html = loop.run_until_complete(fetch(url))

# analisa o HTML com BeautifulSoup


soup = BeautifulSoup(html, 'html.parser')

# encontra a div com a classe 'divListaVagas'
div_vagas = soup.find('div', {'id': 'divListaVagas'})

# imprime o conteúdo da div encontrada
print(div_vagas)
