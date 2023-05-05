from typing import List

from bs4 import BeautifulSoup

from jobs.async_url_fetch import fetch_urls
from jobs.utils import sanitize_job_title


async def scrap_linkedin_jobs(search: str, cd: bool) -> List[dict]:
    search = f"TI {search}"
    cd = '?f_AL=true&' if cd else ''
    url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'

    resp_content = await fetch_urls([url])
    soup = BeautifulSoup(resp_content[url], 'html.parser')

    job_elements = soup.select_one('ul.jobs-search__results-list').select('li')
    jobs = []
    for job_element in job_elements:
        job_a = job_element.select_one('div a')
        job_link = job_a.get('href')
        job_title = job_a.select_one('span').text
        jobs.append({'Job': sanitize_job_title(job_title), 'Apply': job_link})
    return jobs
