import asyncio
import time
from typing import Dict

from enums import Seniority
from jobs.linkekin import scrap_linkedin_jobs
from jobs.nerdin import scrap_nerdin_jobs
from jobs.thor import scrap_thor_jobs

SENIORITY_LEVEL_MAP = {Seniority.Junior: "Júnior", Seniority.Pleno: "Pleno", Seniority.Senior: "Sênior"}
TIME_TO_REFRESH_BUFFER = 60 * 30  # 30 min


async def scrap_jobs(seniority_level: Seniority):
    seniority_str = SENIORITY_LEVEL_MAP[seniority_level]
    linkedin = await scrap_linkedin_jobs(seniority_str, True)
    nerdin = await scrap_nerdin_jobs(seniority_level)
    thor = await scrap_thor_jobs(seniority_str)
    return [*linkedin, *nerdin, *thor]


class Scraper:
    def __init__(self):
        self._tasks: Dict[Seniority, asyncio.Task] = dict()
        self._buffer: Dict[Seniority, (float, dict)] = dict()

    async def scrap(self, seniority_level: Seniority):
        if seniority_level in self._tasks:
            task = self._tasks[seniority_level]
            await task
        if seniority_level in self._buffer:
            buffer_time, buffer_content = self._buffer[seniority_level]
            if (time.time() - buffer_time) < TIME_TO_REFRESH_BUFFER:
                return buffer_content
        _task = asyncio.create_task(scrap_jobs(seniority_level))
        self._tasks[seniority_level] = _task
        await _task
        jobs = _task.result()
        self._buffer[seniority_level] = [time.time(), jobs]
        del self._tasks[seniority_level]
        return jobs
