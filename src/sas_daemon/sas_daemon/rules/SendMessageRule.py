'''
Copyright 2024 Jim Konstantos <konstantosjim@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file (SendMessageRule.py) contains a class (SendMessageRule) which holds intervals,
dates and other info necessary for sending messages at certain intervals/dates. This file
is part of the "SAS-Commons" module of the "SAS" project.
'''
from __future__ import annotations
from typing import Callable, Coroutine
from datetime import datetime, timedelta
from ..templates import Template, PersonTemplateArguments
import asyncio


class SendMessageRule:
    def __init__(self, recipients:list[PersonTemplateArguments], template:Template,
                 start_date:datetime, end_date:datetime|None = None,
                 interval:timedelta|None = None, last_executed:datetime|None = None, id:int|None = None):
        if end_date is not None and (start_date >= end_date):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint start_date({start_date}) < end_date({end_date}): Failed.")
        # start_date and end_date are valid
        
        if last_executed is not None and (start_date > last_executed):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint start_date({start_date}) <= last_executed({last_executed}): Failed")
        if last_executed is not None and end_date is not None and (last_executed > end_date):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint last_executed({last_executed}) <= end_date({end_date}): Failed")
        # last_executed is valid


        self._start_date = start_date
        self._end_date = end_date
        self._interval = interval if interval is not None else timedelta()
        self._last_executed = last_executed
        self.template = template
        self.recipients = recipients
        self.id = id

    @property
    def next_execution_date(self) -> datetime|None:
        dtnow = datetime.now()

        # If the starting date is in the future we don't need to add any intervals.
        if self._last_executed is None and self._start_date >= dtnow:
            return self._start_date

        next_date = self._last_executed
        if next_date is None:
            next_date = self._start_date
        # AT THIS POINT: next_date is a datetime with the last available known execution

        next_date += self._interval
        # AT THIS POINT: next_date holds the next execution date (Could be in the past)

        if self._end_date and next_date > self._end_date:
            if self._last_executed and self._last_executed < self._end_date:
                return self._end_date
            else:
                return None
        return next_date
    
    @property
    def next_execution(self) -> timedelta|None:
        dtnow = datetime.now()
        # next_execution_date
        ned = self.next_execution_date

        if not ned: return None
        if dtnow >= ned: return timedelta() # 0
        return ned - dtnow
    
    def report_executed(self):
        self._last_executed = datetime.now()

    async def schedule(self, callback:Callable[[SendMessageRule], Coroutine]):
        # Wait until execution
        ne = self.next_execution
        if ne and ne != timedelta(0): await asyncio.sleep(ne.total_seconds())

        # Prepare callback call
        await asyncio.create_task(callback(self))

        # update execution time
        self.report_executed()

    async def infschedule(self, callback:Callable[[SendMessageRule], Coroutine]):
        while self.next_execution_date is not None:
            await self.schedule(callback)