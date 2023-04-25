import requests
from bs4 import BeautifulSoup
from typing import List


class Sites:
    def __init__(self) -> None:
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.headers = {'User-Agent': self.user_agent}


    def linkedin_jobs(self,search: str, cd: bool) -> List[dict]:
        if cd == True:
            cd = '?f_AL=true&'
        else:
            cd = ''
        url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}location=Brazil&position=1&pageNum=0&f_TPR=r604800'

        jobs = []
        with requests.Session() as session:
            response = session.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            job_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('https://br.linkedin.com/jobs/view/')]

            for link in job_links[:3]:
                response = session.get(link, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                job_name = soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'})
                if not job_name:
                    continue

                job_re = job_name.get_text(strip=True)


            job = {
                'Job': job_re,
                'Apply': link
            }
            jobs.append(job)

        return jobs


    def nerdin_jobs(self,search: str) -> List[dict]:
        url =f'https://www.nerdin.com.br/func/FVagaListar.php?F=HO&NomeEspeciPalavraChave={search}&PermiteTrabalhoRemoto=0'
        response = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        job_links = [link.get('href') for link in soup.find_all('a', href=True) if link.get('href').startswith('vaga/')]

        link_complete = []
        for link in job_links[:3]:
            link_complete.append( 'https://www.nerdin.com.br/' + link)

        b_tag = soup.select('span.style > b')[:3]
        if b_tag:
            text = b_tag[1].text
            print(text)
        print(b_tag)

    def thor_jobs(self,search: str)-> List[dict]:
        vagas=[]

        search_junior = f'https://programathor.com.br/jobs-city/remoto?expertise={search}'
        response = requests.get(search_junior,headers=self.headers)
        soup = BeautifulSoup(response.text,'html.parser')
        jobs = soup.select('.cell-list')[:3]

        for job in jobs:
            name = job.find_all('h3')[0].get_text()
            link = "https://programathor.com.br"+ job.select('a')[0].attrs['href']
            techs =[]
            for tech in job.find_all('span', {'class': 'tag-list background-gray'}):
                techs.append(tech.get_text())

            vaga_dict = {
                'Job': name,
                'Apply': link,
                'Techs': techs
            }

            vagas.append(vaga_dict)

        return vagas

