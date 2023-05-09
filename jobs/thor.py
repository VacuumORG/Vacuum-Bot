from typing import List

from bs4 import BeautifulSoup

from jobs.async_url_fetch import fetch_urls
from jobs.utils import sanitize_job_title


def check_if_job_is_expired(job_soup):
    return 'opacity-60p' in job_soup.attrs['class']


def check_if_job_is_broken(job_soup):
    return 'min-height-180' in job_soup.attrs['class']


async def scrap_thor_jobs(search: str) -> List[dict | Exception]:
    """
    Args:
        search (str): this string can only receive 3 parameters which are 'Júnior'/'Pleno'/'Sênior'.
    Returns:
        List[dict]: returns a dictionary list with the keys 'Job: str'/'Apply: str'/'Techs: list of str'.
    """
    url = f'https://programathor.com.br/jobs-city/remoto?expertise={search}'
    resp_content = await fetch_urls([url])
    if isinstance(resp_content[url], Exception):
        return [resp_content[url]]
    soup = BeautifulSoup(resp_content[url], 'html.parser')
    jobs = soup.select('.cell-list')

    jobs = [job for job in jobs if not check_if_job_is_broken(job) and not check_if_job_is_expired(job)]

    jobs = [{'Job': sanitize_job_title(job.find_all('h3')[0].text),
             'Apply': "https://programathor.com.br" + job.select('a')[0].attrs['href'],
             'Techs': [tech.get_text() for tech in job.find_all('span', {'class': 'tag-list background-gray'})]} for
            job in jobs]

    return jobs
