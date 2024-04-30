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


class SendMessageRule:
    def __init__(self, start_date:datetime, end_date:datetime|None = None,
                 interval:timedelta|None = None, last_executed:datetime|None = None):
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
        self._interval = interval
        self._last_executed = last_executed