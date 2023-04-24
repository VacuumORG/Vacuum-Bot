
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}

from typing import List
import requests
from bs4 import BeautifulSoup

def linkedin_jobs(search: str, cd: bool) -> List[dict]:
    if cd == True:
        cd = '?f_AL=true&'
    else:
        cd = ''
    url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'

    jobs = []
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        job_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('https://br.linkedin.com/jobs/view/')]

        for link in job_links[:3]:
            response = session.get(link, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            job_name = soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'})
            if not job_name:
                continue

            job = {
                'Job': job_name.get_text(strip=True),
                'Apply': link
            }
            jobs.append(job)

    return jobs
