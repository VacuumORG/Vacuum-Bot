from dataclasses import dataclass
from typing import List, Optional, Union, TypeAlias, Tuple

ScraperValueType: TypeAlias = Optional[Union[str, List[str]]]


@dataclass
class Keyword:
    name: str
    linkedin_value: ScraperValueType = None
    nerdin_value: ScraperValueType = None
    thor_value: ScraperValueType = None
    alias_list: Optional[List[str]] = None

    def __hash__(self):
        return hash(self.name)


def __normalize(_str: str):
    return _str.strip().replace(".", "").replace("-", "").replace(" ", "").upper()


def get_keyword_list():
    return [key.name for key in KEYWORDS]


def get_keyword_by_name(key):
    return KEYWORDS[get_keyword_list().index(key)]


def __look_up_consts(search: str):
    search = __normalize(search)
    for key in KEYWORDS:
        alias = [key.name, *(key.alias_list if key.alias_list else [])]
        normalized_alias = list(map(__normalize, alias))
        if search in normalized_alias:
            return key


def __look_up_nerdin_id(search: str, nerdin_ids: List[Tuple[str, str]]):
    search = __normalize(search)
    ids = []
    for key, _id in nerdin_ids:
        if search == __normalize(key):
            ids.append(_id)
    if ids:
        if len(ids) == 1:
            return ids[0]
        return ids


def __look_up_thor_id(search: str, thor_ids: List[Tuple[str, str]]):
    search = __normalize(search)
    for key, _id in thor_ids:
        if search == __normalize(key):
            return _id


def try_to_find_keyword(search, nerdin_ids, thor_ids):
    if key := __look_up_consts(search):
        return key

    return Keyword(name=search, linkedin_value=search, nerdin_value=__look_up_nerdin_id(search, nerdin_ids),
                   thor_value=__look_up_thor_id(search, thor_ids))


KEYWORDS = [
    Keyword(name="Android", linkedin_value="Android", nerdin_value="CodigoPlataforma=27&",
            thor_value='/jobs-android', ),
    Keyword(name="API", linkedin_value="API", nerdin_value=['CodigoEspecialidade=67&', 'CodigoPlataforma=115&'],
            thor_value="/jobs-api", ),
    Keyword(name="Angular", linkedin_value="Angular", nerdin_value="CodigoPlataforma=75&",
            thor_value="/jobs-angular", ),
    Keyword(name="AWS", linkedin_value="AWS", nerdin_value="CodigoPlataforma=108&",
            thor_value=["/jobs-aws-ec2-elastic-compute-cloud", "/jobs-aws-rds-relational-database-service",
                        "/jobs-aws-s3"], ),
    Keyword(name="Azure", linkedin_value="Azure", nerdin_value="CodigoPlataforma=20&", thor_value="/jobs-azure", ),
    Keyword(name="Big Data", linkedin_value="Big Data", nerdin_value="CodigoEspecialidade=11&",
            thor_value="/jobs-big-data", ),
    Keyword(name="C#", linkedin_value="C%23", nerdin_value="CodigoPlataforma=26&", thor_value="/jobs-c-sharp",
            alias_list=[","]),
    Keyword(name="C++", linkedin_value="C%2B%2B", nerdin_value="CodigoPlataforma=85&", thor_value="/jobs-c++",
            alias_list=["Cplusplus"]),
    Keyword(name="Cloud", linkedin_value="Cloud", nerdin_value=["CodigoPlataforma=38&", "CodigoEspecialidade=10&"],
            thor_value="/jobs-cloud", ),
    Keyword(name="Dados", linkedin_value="Dados", nerdin_value="CodigoArea=5&", thor_value="/jobs-data-science",
            alias_list=["Data Science", "Data"]),
    Keyword(name="DevOps", linkedin_value="DevOps", nerdin_value="CodigoEspecialidade=16&",
            thor_value="/jobs-devops", ),
    Keyword(name="Flutter", linkedin_value="Flutter", nerdin_value="CodigoPlataforma=127&",
            thor_value="/jobs-flutter", ),
    Keyword(name="Front End", linkedin_value="Front End", nerdin_value="CodigoEspecialidade=30&",
            thor_value="/jobs-front-end", alias_list=["Front"]),
    Keyword(name="Go", linkedin_value="Go", nerdin_value="CodigoPlataforma=122&", thor_value="/jobs-go",
            alias_list=["Golang"]),
    Keyword(name="Java", linkedin_value="Java", nerdin_value="CodigoPlataforma=28&", thor_value="/jobs-java", ),
    Keyword(name="JavaScript", linkedin_value="JavaScript", nerdin_value="CodigoPlataforma=61&",
            thor_value="/jobs-javascript", alias_list=["js"]),
    Keyword(name=".NET", linkedin_value=".NET", nerdin_value="CodigoPlataforma=33&", thor_value="/jobs-net",
            alias_list=["dotnet"]),
    Keyword(name=".NET Core", linkedin_value=".NET Core", nerdin_value="CodigoPlataforma=132&",
            thor_value="/jobs-net-core", alias_list=["dotnet core"]),
    Keyword(name="NoSQL", linkedin_value="NoSQL", nerdin_value="CodigoPlataforma=9&", thor_value="/jobs-nosql", ),
    Keyword(name="Node.JS", linkedin_value="Node.JS", nerdin_value="CodigoPlataforma=62&",
            thor_value="/jobs-node-js", alias_list=["node"]),
    Keyword(name="Oracle", linkedin_value="Oracle", nerdin_value="CodigoPlataforma=2&", thor_value="/jobs-oracle", ),
    Keyword(name="PHP", linkedin_value="PHP", nerdin_value="CodigoPlataforma=25&", thor_value="/jobs-php", ),
    Keyword(name="Python", linkedin_value="Python", nerdin_value="CodigoPlataforma=45&", thor_value="/jobs-python", ),
    Keyword(name="QA", linkedin_value="QA", nerdin_value="CodigoPlataforma=103&",
            thor_value="/jobs-quality-assurance", ),
    Keyword(name="ReactJs", linkedin_value="ReactJs", nerdin_value="CodigoPlataforma=76&", thor_value="/jobs-react",
            alias_list=['react']),
    Keyword(name="React Native", linkedin_value="React Native", thor_value="/jobs-react-native", ),
    Keyword(name="Rede", linkedin_value="Rede", nerdin_value="CodigoEspecialidade=20&", ),
    Keyword(name="Ruby", linkedin_value="Ruby", nerdin_value=["CodigoEspecialidade=51&", "CodigoPlataforma=68&"],
            thor_value="/jobs-ruby", ),
    Keyword(name="Swift", linkedin_value="Swift", nerdin_value="CodigoPlataforma=114&", thor_value="/jobs-swift", ),
    Keyword(name="VueJs", linkedin_value="Vue.js", nerdin_value="CodigoPlataforma=130&", thor_value="/jobs-vue-js",
            alias_list=['vue']),
    Keyword(name="BlockChain", linkedin_value="BlockChain", nerdin_value="", thor_value="/jobs-blockchain", ),
    Keyword(name="iOS", linkedin_value="iOS", nerdin_value="CodigoPlataforma=23&", thor_value="/jobs-ios", ),
    Keyword(name="UI/UX", linkedin_value="UI/UX", nerdin_value="CodigoPlataforma=72,37&", alias_list=["UI", "UX"]),
    Keyword(name="Designer", linkedin_value="Designer", nerdin_value="CodigoEspecialidade=44&", ),
    Keyword(name="Tech Lead", linkedin_value="Tech Lead", nerdin_value="CodigoEspecialidade=69&", ),
    Keyword(name="Testes", linkedin_value="Testes", nerdin_value="CodigoEspecialidade=28&",
            thor_value=["/jobs-testes-automatizados", "/jobs-testes-de-regressao", "/jobs-testes-funcionais",
                        "/jobs-testes-unitarios"], alias_list=["tests"]),
    Keyword(name="Security", linkedin_value="security", nerdin_value="CodigoEspecialidade=27&",
            alias_list=["Segurança"]),
    Keyword(name="Back End", linkedin_value="Back-end", nerdin_value="CodigoEspecialidade=31&", alias_list=["Back"]),
    Keyword(name="Full Stack", linkedin_value="Full Stack", nerdin_value="CodigoEspecialidade=32&", ),
    Keyword(name="DBA", linkedin_value="DBA", nerdin_value="CodigoEspecialidade=1&", ),
]
