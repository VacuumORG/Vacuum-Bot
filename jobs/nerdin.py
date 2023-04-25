import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}

def nerdin_vagas(search: str):
    url =f'https://www.nerdin.com.br/func/FVagaListar.php?F=HO&NomeEspeciPalavraChave={search}&PermiteTrabalhoRemoto=0'
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    job_links = [link.get('href') for link in soup.find_all('a', href=True) if link.get('href').startswith('vaga/')]

    link_complete = []
    for link in job_links[:3]:
        link_complete.append( 'https://www.nerdin.com.br/' + link)

    b_tag = soup.select('span > b')[:3]
    if b_tag:
        text = b_tag[1].text
        print(text)
    print(b_tag)

nerdin_vagas(search='python')
