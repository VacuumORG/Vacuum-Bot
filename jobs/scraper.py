import time

from enums import Seniority
from jobs.linkekin import scrap_linkedin_jobs
from jobs.nerdin import scrap_nerdin_jobs
from jobs.thor import scrap_thor_jobs

SENIORITY_LEVEL_MAP = {Seniority.Junior: "Júnior", Seniority.Pleno: "Pleno", Seniority.Senior: "Sênior"}
TIME_TO_REFRESH_BUFFER = 60 * 30  # 30 min


class Scraper:
    def __init__(self):
        self._buffer = dict()

    async def scrap(self, seniority_level: Seniority):
        if seniority_level in self._buffer:
            buffer_time, buffer_content = self._buffer[seniority_level]
            if (time.time() - buffer_time) < TIME_TO_REFRESH_BUFFER:
                return buffer_content
        seniority_str = SENIORITY_LEVEL_MAP[seniority_level]
        linkedin = await scrap_linkedin_jobs(seniority_str, True)
        nerdin = await scrap_nerdin_jobs(seniority_level)
        thor = await scrap_thor_jobs(seniority_str)
        jobs = [*linkedin, *nerdin, *thor]
        self._buffer[seniority_level] = [time.time(), jobs]
        return jobs
