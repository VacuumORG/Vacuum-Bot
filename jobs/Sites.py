import aiohttp
from bs4 import BeautifulSoup
from typing import List
import certifi
import ssl


def check_if_thor_job_is_expired(job_soup):
    return 'opacity-60p' in job_soup.attrs['class']


def check_if_thor_job_is_broken(job_soup):
    return 'min-height-180' in job_soup.attrs['class']


class Sites:
    def __init__(self) -> None:
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.headers = {'User-Agent': self.user_agent}

    async def _fetch_urls_async(self, urls: List[str], raise_exception: bool = False):
        # Foi necessário adicionar essa etapa de ssl pois usar apenas o aiohttp estava dando exception de certificação
        # Importante checar se essa solução é a ideal. Por enquanto resolveu o problema.
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        ret_response_content = dict()
        async with aiohttp.ClientSession(connector=conn) as session:
            for url in urls:
                async with session.get(url, headers=self.headers) as resp:
                    if raise_exception:
                        resp.raise_for_status()
                    resp_content = await resp.text()
                    ret_response_content[url] = resp_content
        return ret_response_content

    async def linkedin_jobs(self, search: str, cd: bool) -> List[dict]:
        cd = '?f_AL=true&' if cd else ''
        url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'

        resp_content = await self._fetch_urls_async([url])
        soup = BeautifulSoup(resp_content[url], 'html.parser')

        job_links = [link.get('href') for link in soup.find_all('a') if
                     link.get('href') and link.get('href').startswith('https://br.linkedin.com/jobs/view/')]

        job_link_content = await self._fetch_urls_async(job_links)
        jobs = []
        for link in job_links:
            soup = BeautifulSoup(job_link_content[link], 'html.parser')
            title = soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'})
            if title:
                jobs.append({'Job': title.get_text(strip=True), 'Apply': link})
        return jobs

    async def nerdin_jobs(self, search: str) -> List[dict]:
        url = f'https://www.nerdin.com.br/func/FVagaListar.php?F=HO&NomeEspeciPalavraChave={search}&PermiteTrabalhoRemoto=0'

        resp_content = await self._fetch_urls_async([url])
        soup = BeautifulSoup(resp_content[url], 'html.parser')

        job_links = ['https://www.nerdin.com.br/' + link.get('href') for link in soup.find_all('a', href=True)
                     if link.get('href').startswith('vaga/')]
        job_names = soup.select('span:nth-child(1) b')

        jobs = [{'Job': job_name.text, 'Apply': link} for link, job_name in zip(job_links, job_names)]
        return jobs

    async def thor_jobs(self, search: str) -> List[dict]:
        """
        Args:
            search (str): this string can only receive 3 parameters which are 'Júnior'/'Pleno'/'Sênior'.
        Returns:
            List[dict]: returns a dictionary list with the keys 'Job: str'/'Apply: str'/'Techs: list of str'.
        """
        url = f'https://programathor.com.br/jobs-city/remoto?expertise={search}'
        resp_content = await self._fetch_urls_async([url])
        soup = BeautifulSoup(resp_content[url], 'html.parser')
        jobs = soup.select('.cell-list')

        jobs = [job for job in jobs if not check_if_thor_job_is_broken(job) and not check_if_thor_job_is_expired(job)]

        jobs = [{'Job': job.find_all('h3')[0].get_text(),
                 'Apply': "https://programathor.com.br" + job.select('a')[0].attrs['href'],
                 'Techs': [tech.get_text() for tech in job.find_all('span', {'class': 'tag-list background-gray'})]} for
                job in jobs]

        return jobs
