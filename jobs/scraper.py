import asyncio
import ssl
import time
from typing import Dict

import certifi

from enums import JobLevel
from jobs.linkedin import scrap_linkedin_jobs
from jobs.nerdin import scrap_nerdin_jobs
from jobs.thor import scrap_thor_jobs

JOB_LEVEL_MAP = {JobLevel.Junior: "Júnior", JobLevel.Pleno: "Pleno", JobLevel.Senior: "Sênior"}
TIME_TO_REFRESH_BUFFER = 60 * 10  # 10 min


async def scrap_jobs(job_level: JobLevel, ssl_context):
    job_level_str = JOB_LEVEL_MAP[job_level]
    linkedin = asyncio.create_task(scrap_linkedin_jobs(job_level_str, True, ssl_context))
    nerdin = asyncio.create_task(scrap_nerdin_jobs(job_level, ssl_context))
    thor = asyncio.create_task(scrap_thor_jobs(job_level_str, ssl_context))

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
        self.tasks: Dict[JobLevel, asyncio.Task] = dict()
        self.buffer: Dict[JobLevel, (float, dict)] = dict()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def scrap_task(self, job_level):
        jobs, errors = await scrap_jobs(job_level, self.ssl_context)
        self.buffer[job_level] = [time.time(), jobs]
        return jobs, errors

    async def scrap(self, job_level: JobLevel):
        if job_level in self.tasks:
            _task = self.tasks[job_level]
            await _task
        if job_level in self.buffer:
            buffer_time, buffer_content = self.buffer[job_level]
            if (time.time() - buffer_time) < TIME_TO_REFRESH_BUFFER:
                return buffer_content, []
        task = asyncio.create_task(self.scrap_task(job_level))
        self.tasks[job_level] = task
        await task
        jobs, errors = task.result()
        return jobs, errors
