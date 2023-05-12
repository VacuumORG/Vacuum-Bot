import asyncio
import time
from typing import Dict

from enums import Seniority
from jobs.linkedin import scrap_linkedin_jobs
from jobs.nerdin import scrap_nerdin_jobs
from jobs.thor import scrap_thor_jobs

SENIORITY_LEVEL_MAP = {Seniority.Junior: "Júnior", Seniority.Pleno: "Pleno", Seniority.Senior: "Sênior"}
TIME_TO_REFRESH_BUFFER = 60 * 10  # 10 min


async def scrap_jobs(seniority_level: Seniority):
    seniority_str = SENIORITY_LEVEL_MAP[seniority_level]
    linkedin = asyncio.create_task(scrap_linkedin_jobs(seniority_str, True))
    nerdin = asyncio.create_task(scrap_nerdin_jobs(seniority_level))
    thor = asyncio.create_task(scrap_thor_jobs(seniority_str))

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
        self.tasks: Dict[Seniority, asyncio.Task] = dict()
        self.buffer: Dict[Seniority, (float, dict)] = dict()

    async def scrap(self, seniority_level: Seniority):
        if seniority_level in self.tasks:
            _task = self.tasks[seniority_level]
            await _task
        if seniority_level in self.buffer:
            buffer_time, buffer_content = self.buffer[seniority_level]
            if (time.time() - buffer_time) < TIME_TO_REFRESH_BUFFER:
                return buffer_content, []
        task = asyncio.create_task(scrap_jobs(seniority_level))
        self.tasks[seniority_level] = task
        await task
        jobs, errors = task.result()
        self.buffer[seniority_level] = [time.time(), jobs]
        del self.tasks[seniority_level]
        return jobs, errors
