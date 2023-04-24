import requests
from bs4 import BeautifulSoup
from typing import List

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}

def thor_jobs(search: str)-> List[dict]:
    vagas=[]

    search_junior = f'https://programathor.com.br/jobs-city/remoto?expertise={search}'
    response = requests.get(search_junior,headers=headers)
    soup = BeautifulSoup(response.text,'html.parser')
    jobs = soup.select('.cell-list')[:3]

    for job in jobs:
        name = job.find_all('h3')[0].get_text()
        link = "https://programathor.com.br"+ job.select('a')[0].attrs['href']
        techs =[]
        for tech in job.find_all('span', {'class': 'tag-list background-gray'}):
            techs.append(tech.get_text())

        vaga_dict = {
            'name': name,
            'link': link,
            'techs': techs
        }

        vagas.append(vaga_dict)

    return vagas


