import sys
import os

# Adicione o diretório pai do arquivo atual ao sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

# Agora você pode importar módulos do diretório pai
from jobs.Sites import Sites

# Resto do seu código


sites = Sites()
print(sites.thor_jobs(search='Júnior'))
