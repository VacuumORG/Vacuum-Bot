from typing import List

from bs4 import BeautifulSoup

from jobs.async_url_fetch import fetch_urls
from jobs.utils import sanitize_job_title


async def scrap_linkedin_jobs(search: str, cd: bool, ssl_context) -> List[dict | Exception]:
    search = f"TI {search}"
    cd = '?f_AL=true&' if cd else ''
    url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r2592000'

    resp_content = await fetch_urls([url], ssl_context)
    if isinstance(resp_content[url], Exception):
        return [resp_content[url]]
    soup = BeautifulSoup(resp_content[url], 'html.parser')

    job_elements = soup.select_one('ul.jobs-search__results-list').select('li')
    jobs = []
    for job_element in job_elements:
        job_div = job_element.select_one('div')
        if not job_div.has_attr('data-entity-urn'):
            job_a = job_element.select_one('a')
            job_id = job_a['data-entity-urn'].split(":")[3]
            job_title = job_a.select_one('div h3').text
        else:
            job_id = job_div['data-entity-urn'].split(":")[3]
            job_title = job_div.select_one('a span').text
        jobs.append({'Job': sanitize_job_title(job_title), 'Apply': f"https://www.linkedin.com/jobs/view/{job_id}"})
    return jobs
