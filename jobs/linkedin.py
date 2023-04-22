import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}
url = 'https://www.linkedin.com/jobs/search/?keywords=junior&location=Trabalho%20remoto'

jobs_links = lambda: [str(link.get('href'))
                    for link in BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser').find_all('a')
                    if str(link.get('href')).startswith('https://br.linkedin.com/jobs/view/')]

def scrap_jobs_links():
    links_page_job = jobs_links()
    for link in links_page_job:
        response = requests.get(link)
        soup = BeautifulSoup(response.text,'html.parser')
        job_name = soup.select_one('h1',{'class':'jobs-unified-top-card__job-title'}).get_text(strip=True)
        print(job_name)

    print(links_page_job)

scrap_jobs_links()
