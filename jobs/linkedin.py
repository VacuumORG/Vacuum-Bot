import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}

def get_job_links(search: str,cd: bool):
    if cd == True:
        cd = '?f_AL=true&'
    else:
        cd = ''
    url = f'https://www.linkedin.com/jobs/search/?f_WT=2&geoId=106057199&keywords={search}&{cd}?f_AL=true&location=Brazil&position=1&pageNum=0&f_TPR=r604800'
    job_links = []
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('https://br.linkedin.com/jobs/view/'):
            job_links.append(href)

    jobs = []
    links_page_job = job_links
    for idx, link in enumerate(links_page_job):
        if idx == 3:
            break
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_name = soup.select_one('h1', {'class': 'jobs-unified-top-card__job-title'}).get_text(strip=True)

        job = {
            '\nJob ': job_name,
            'Apply ': link
        }
        jobs.append(job)
    return jobs


def format_dict_list(dict_list):
    return "\n".join(f"{key}: {value}" for d in dict_list for key, value in d.items())

linked = format_dict_list(get_job_links(search='junior',cd= True))

print(type(linked))
