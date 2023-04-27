import requests
from bs4 import BeautifulSoup
from typing import List


class Sites:
    def __init__(self) -> None:
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.headers = {'User-Agent': self.user_agent}


    def linkedin_jobs(self,search: str, cd: bool) -> List[dict]:
        cd = '?f_AL=true&' if cd else ''

        url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'
        with requests.Session() as session:
            response = session.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            job_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('https://br.linkedin.com/jobs/view/')]
            jobs = [{'Job': soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'}).get_text(strip=True), 'Apply': link} for link in job_links[:3] for soup in [BeautifulSoup(session.get(link, headers=self.headers).text, 'html.parser')] if soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'})]

        return jobs

    def nerdin_jobs(self,search: str) -> List[dict]:
        url =f'https://www.nerdin.com.br/func/FVagaListar.php?F=HO&NomeEspeciPalavraChave={search}&PermiteTrabalhoRemoto=0'
        response = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        job_links = ['https://www.nerdin.com.br/' + link.get('href') for link in soup.find_all('a', href=True) if link.get('href').startswith('vaga/')][:3]
        job_name = soup.select('span:nth-child(1) b')[:3]

        jobs = list(map(lambda x: {'Job': x[1].text, 'Apply': x[0]}, zip(job_links, job_name)))

        return jobs


    def thor_jobs(self,search: str)-> List[dict]:
        """
        Args:
            search (str): this string can only receive 3 parameters which are 'Junior'/'Full/Senior'.
        Returns:
            List[dict]: returns a dictionary list with the keys 'Job'/'Apply'/'Techs'.
        """
        search_junior = f'https://programathor.com.br/jobs-city/remoto?expertise={search}'
        response = requests.get(search_junior,headers=self.headers)
        soup = BeautifulSoup(response.text,'html.parser')
        jobs = soup.select('.cell-list')[:3]

        jobs = [{'Job': job.find_all('h3')[0].get_text(),
          'Apply': "https://programathor.com.br"+ job.select('a')[0].attrs['href'],
          'Techs': [tech.get_text() for tech in job.find_all('span', {'class': 'tag-list background-gray'})]} for job in jobs]

        return jobs

