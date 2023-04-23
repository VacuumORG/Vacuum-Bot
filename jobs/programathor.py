import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}

search_pleno = 'https://programathor.com.br/jobs-city/remoto?expertise=Pleno'

search_senior = 'https://programathor.com.br/jobs-city/remoto?expertise=Sênior'

def get_link_jobs(word_key):
    search_junior = f'https://programathor.com.br/jobs-city/remoto?expertise={word_key}'
    response = requests.get(search_junior,headers=headers)
    soup = BeautifulSoup(response.text,'html.parser')
    jobs_name = soup.select('.line-height-30')[:3]
    elements = soup.select('.cell-list a[href]')[:3]
    name_links = []
    for i in range(len(elements)):
        href = elements[i].get('href')
        href = "https://programathor.com.br" + href
        name = jobs_name[i].get_text()
        name_link = {'name': name, 'link_job': href}
        name_links.append(name_link)
    return name_links

print (get_link_jobs())
