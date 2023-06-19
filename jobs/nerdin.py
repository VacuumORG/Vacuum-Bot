from typing import List

from bs4 import BeautifulSoup

from enums import JobLevel
from jobs.async_url_fetch import fetch_urls
from jobs.utils import sanitize_job_title

## Temporary map
JOB_LEVEL_MAP = {JobLevel.Junior: 3, JobLevel.Senior: 1, JobLevel.Pleno: 2}
PAGES_PER_SCRAPING_LOOP = 4
MAX_JOB_OPEN_DAYS = 30 * 6  # 6 months


def create_search_url(job_level: JobLevel, page=0):
    base_url = "https://nerdin.com.br/func/FVagaListar.php?"
    home_office = 'UF=HO&'
    job_level = f'CodigoNivel={JOB_LEVEL_MAP[job_level]}&'
    pagination = f'CodigoVagaProxima={(page - 1) * 50}&' if page else ''
    return base_url + home_office + job_level + pagination


def check_job_age(job_soup):
    job_age_string = job_soup.select('a span')[-1].text.split('|')[0].strip()
    if job_age_string.startswith('Há'):
        try:
            job_age_days_string = job_age_string.split(' ')[1]
            job_age_days = int(job_age_days_string)
            if job_age_days > MAX_JOB_OPEN_DAYS:
                return False
        except:
            pass
    return True


async def scrap_nerdin_jobs(job_level: JobLevel, ssl_context) -> List[dict | Exception]:
    results = []
    page = 0
    loop = True
    while loop:
        urls = [create_search_url(job_level, page) for page in
                range(page, page + PAGES_PER_SCRAPING_LOOP)]
        responses = await fetch_urls(urls, ssl_context)

        for content in responses.values():
            if isinstance(content, Exception):
                results.append(content)
                loop = False
                continue
            soup = BeautifulSoup(content, 'html.parser')
            job_containers = soup.select("div.container")
            job_anchors = [job.select_one('a') for job in job_containers if check_job_age(job)]
            results.extend([{'Job': sanitize_job_title(anchor.select_one('span:nth-child(1) b').text),
                             'Apply': 'https://www.nerdin.com.br/' + anchor.get('href')} for anchor in
                            job_anchors])
            if len(job_anchors) < 50:
                loop = False
                break
    return results
