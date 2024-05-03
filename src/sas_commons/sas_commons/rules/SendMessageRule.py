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
from datetime import datetime, timedelta
from ..templates import Template, TemplateArguments


class SendMessageRule:
    def __init__(self, id:int, recipients:list[TemplateArguments], template:Template,
                 start_date:datetime, end_date:datetime|None = None,
                 interval:timedelta|None = None, last_executed:datetime|None = None):
        if end_date is not None and (start_date >= end_date):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint start_date({start_date}) < end_date({end_date}): Failed.")
        # start_date and end_date are valid
        
        if last_executed is not None and (start_date > last_executed):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint start_date({start_date}) <= last_executed({last_executed}): Failed")
        if last_executed is not None and end_date is not None and (last_executed > end_date):
            raise ValueError(f"{self.__class__.__qualname__}: Constraint last_executed({last_executed}) <= end_date({end_date}): Failed")
        # last_executed is valid

        if len(recipients) == 0:
            raise ValueError(f"{self.__class__.__qualname__}: Constraint len(recipients) > 0: Failed")

        self._start_date = start_date
        self._end_date = end_date
        self._interval = interval if interval is not None else timedelta()
        self._last_executed = last_executed
        self.template = template
        self.recipients = recipients
        self.id = id

    @property
    def next_execution_date(self) -> datetime:
        dtnow = datetime.now()

        # If the starting date is in the future we don't need to add any intervals.
        if self._start_date >= dtnow:
            return self._start_date

        next_date = self._last_executed
        if next_date is None:
            next_date = self._start_date
        # AT THIS POINT: next_date is a datetime with the last available known execution

        next_date += self._interval
        # AT THIS POINT: next_date holds the next execution date (Could be in the past)
        return next_date
    
    @property
    def next_execution(self) -> timedelta:
        dtnow = datetime.now()
        # next_execution_date
        ned = self.next_execution_date

        if dtnow >= ned: return timedelta() # 0
        return ned - dtnow
    
    def report_executed(self):
        self._last_executed = datetime.now()