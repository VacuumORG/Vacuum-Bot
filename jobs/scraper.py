import asyncio
import ssl
import time
from typing import Dict, Tuple, Optional

import certifi
from discord.ext import tasks

from enums import JobLevel
from jobs import nerdin, thor
from jobs.keywords import try_to_find_keyword, Keyword
from jobs.linkedin import scrap_linkedin_jobs
from jobs.nerdin import scrap_nerdin_jobs
from jobs.thor import scrap_thor_jobs

JOB_LEVEL_MAP = {JobLevel.Junior: "Júnior", JobLevel.Pleno: "Pleno", JobLevel.Senior: "Sênior"}
TIME_TO_REFRESH_BUFFER = 60 * 10  # 10 min


async def scrap_jobs(ssl_context, job_level: JobLevel, keyword: Optional[Keyword] = None):
    job_level_str = JOB_LEVEL_MAP[job_level]
    linkedin = asyncio.create_task(
        scrap_linkedin_jobs(ssl_context, job_level_str, keyword.linkedin_value if keyword else None))
    nerdin = asyncio.create_task(scrap_nerdin_jobs(ssl_context, job_level, keyword.nerdin_value if keyword else None))
    thor = asyncio.create_task(scrap_thor_jobs(ssl_context, job_level_str, keyword.thor_value if keyword else None))

    results = await asyncio.gather(linkedin, nerdin, thor, return_exceptions=True)
    flat_results = []
    for result in results:
        if isinstance(result, list):
            flat_results.extend(result)
        else:
            flat_results.append(result)

    errors = [result for result in flat_results if isinstance(result, Exception)]
    jobs = [result for result in flat_results if result not in errors]
    return jobs, errors


class Scraper:
    def __init__(self):
        self.tasks: Dict[Tuple[JobLevel, str], asyncio.Task] = dict()
        self.buffer: Dict[Tuple[JobLevel, str], (float, dict)] = dict()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._nerdin_ids = None
        self._thor_ids = None

    async def _fetch_ids(self):
        self._nerdin_ids = await nerdin.get_keyword_ids(self.ssl_context)
        self._thor_ids = await thor.get_keyword_ids(self.ssl_context)

    def start(self):
        self.refresh_ids.start()

    @tasks.loop(minutes=5)
    async def refresh_ids(self):
        await self._fetch_ids()

    async def scrap_task(self, job_level, keyword: Optional[Keyword] = None):
        jobs, errors = await scrap_jobs(self.ssl_context, job_level, keyword)
        self.buffer[job_level] = [time.time(), jobs]
        return jobs, errors

    async def scrap(self, job_level: JobLevel, keyword=None):
        if keyword:
            keyword = try_to_find_keyword(search=keyword, nerdin_ids=self._nerdin_ids, thor_ids=self._thor_ids)
        print(f"Scraper process > {job_level.name}, {keyword}")
        search_id = (job_level, keyword)
        if search_id in self.tasks:
            _task = self.tasks[search_id]
            await _task
        if search_id in self.buffer:
            buffer_time, buffer_content = self.buffer[search_id]
            if (time.time() - buffer_time) < TIME_TO_REFRESH_BUFFER:
                return buffer_content, []
        task = asyncio.create_task(self.scrap_task(job_level, keyword))
        self.tasks[search_id] = task
        await task
        jobs, errors = task.result()
        return jobs, errors
