import asyncio
import re
import ssl
from enum import Enum, auto
from typing import List

import aiohttp
import certifi
from bs4 import BeautifulSoup


class Seniority(Enum):
    JUNIOR = auto()
    SENIOR = auto()
    PLENO = auto()


## Temporary map
SENIORITY_LEVEL_MAP = {"Júnior": Seniority.JUNIOR, "Pleno": Seniority.PLENO, "Sênior": Seniority.SENIOR}

NERDIN_SENIORITY_MAP = {Seniority.JUNIOR: 3, Seniority.SENIOR: 1, Seniority.PLENO: 2}
NERDIN_PAGES_PER_SCRAPING_PROCESS = 4


def sanitize_job_title(job_title):
    job_title = job_title.strip()
    job_title = job_title.replace('\n', '')
    job_title = re.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        " ", job_title)
    return job_title


def create_nerdin_url(seniority_level: Seniority, page=0):
    base_url = "https://nerdin.com.br/func/FVagaListar.php?"
    home_office = 'UF=HO&'
    seniority = f'CodigoNivel={NERDIN_SENIORITY_MAP[seniority_level]}&'
    pagination = f'CodigoVagaProxima={(page - 1) * 50}&' if page else ''
    return base_url + home_office + seniority + pagination


def check_if_thor_job_is_expired(job_soup):
    return 'opacity-60p' in job_soup.attrs['class']


def check_if_thor_job_is_broken(job_soup):
    return 'min-height-180' in job_soup.attrs['class']


class Sites:
    def __init__(self) -> None:
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.headers = {'User-Agent': self.user_agent}

    async def _single_fetch(self, session, url, raise_exception: bool):
        print(f"Start fetching URL: {url}")

        async with session.get(url, headers=self.headers) as response:
            if response.status != 200:
                print(f"Fetch error | {response.status} | {url}")
                if raise_exception:
                    response.raise_for_status()
            print(f"Done fetching URL: {url}")
            return url, await response.text()

    async def _fetch_urls_async(self, urls: List[str], raise_exception: bool = False):
        # Foi necessário adicionar essa etapa de ssl pois usar apenas o aiohttp estava dando exception de certificação
        # Importante checar se essa solução é a ideal. Por enquanto resolveu o problema.
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        tasks = []
        async with aiohttp.ClientSession(connector=conn) as session:
            for url in urls:
                task = asyncio.create_task(self._single_fetch(session, url, raise_exception))
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            return dict(results)

    async def linkedin_jobs(self, search: str, cd: bool) -> List[dict]:
        search = f"TI {search}"
        cd = '?f_AL=true&' if cd else ''
        url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'

        resp_content = await self._fetch_urls_async([url])
        soup = BeautifulSoup(resp_content[url], 'html.parser')

        job_elements = soup.select_one('ul.jobs-search__results-list').select('li')
        jobs = []
        for job_element in job_elements:
            job_a = job_element.select_one('div a')
            job_link = job_a.get('href')
            job_title = job_a.select_one('span').text
            jobs.append({'Job': sanitize_job_title(job_title), 'Apply': job_link})
        return jobs

    async def nerdin_jobs(self, search: str) -> List[dict]:
        seniority_level = SENIORITY_LEVEL_MAP[search]
        jobs = []
        page = 0
        loop = True
        while loop:
            urls = [create_nerdin_url(seniority_level, page) for page in
                    range(page, page + NERDIN_PAGES_PER_SCRAPING_PROCESS)]
            responses = await self._fetch_urls_async(urls)

            for url, content in responses.items():
                soup = BeautifulSoup(content, 'html.parser')
                job_containers = soup.select("div.container")
                job_anchors = [x.select_one('a') for x in job_containers]
                jobs.extend([{'Job': sanitize_job_title(anchor.select_one('span:nth-child(1) b').text),
                              'Apply': 'https://www.nerdin.com.br/' + anchor.get('href')} for anchor in
                             job_anchors])
                if len(job_anchors) < 50:
                    loop = False
                    break
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

        jobs = [{'Job': sanitize_job_title(job.find_all('h3')[0].text),
                 'Apply': "https://programathor.com.br" + job.select('a')[0].attrs['href'],
                 'Techs': [tech.get_text() for tech in job.find_all('span', {'class': 'tag-list background-gray'})]} for
                job in jobs]

        return jobs
