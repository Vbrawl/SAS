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

This file contains tests for the SendMessageRule class.
'''

import pytest
from sas_commons import SendMessageRule
from datetime import datetime, timedelta


def test_SendMessageRule__init():
    smr = SendMessageRule(datetime(2000, 1, 1)) # No error
    smr2 = SendMessageRule(datetime(2000, 1, 1), datetime(2000, 1, 2)) # No error
    smr3 = SendMessageRule(datetime(2000, 1, 1), last_executed=datetime(2000, 1, 1)) # No error
    smr4 = SendMessageRule(start_date=datetime(2000, 1, 1), last_executed=datetime(2000, 1, 2), end_date=datetime(2000, 1, 2))

    with pytest.raises(ValueError):
        smr5 = SendMessageRule(start_date=datetime(2000, 1, 2), end_date=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr6 = SendMessageRule(start_date=datetime(2000, 1, 2), last_executed=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr7 = SendMessageRule(start_date=datetime(2000, 1, 1), end_date=datetime(2000, 1, 2), last_executed=datetime(2000, 1, 3))


def test_SendMessageRule__next_execution_date():
    smr = SendMessageRule(datetime(2000, 1, 1))
    assert smr.next_execution_date == datetime(2000, 1, 1)

    smr2 = SendMessageRule(datetime(2000, 1, 1), interval=timedelta(5))
    assert smr2.next_execution_date == datetime(2000, 1, 6)

    smr3 = SendMessageRule(datetime(2000, 1, 1), last_executed = datetime(2000, 1, 2), interval = timedelta(5))
    assert smr3.next_execution_date == datetime(2000, 1, 7)

    tomorrow = datetime.now() + timedelta(days=1)
    smr4 = SendMessageRule(tomorrow)
    assert smr4.next_execution_date == tomorrow


def test_SendMessageRule__next_execution():
    smr = SendMessageRule(datetime(2000, 1, 1))
    assert smr.next_execution == timedelta()

    today = datetime.now()
    smr2 = SendMessageRule(today + timedelta(days=1))
    assert smr2.next_execution == timedelta(days=1)

    smr3 = SendMessageRule(today - timedelta(days=1), interval=timedelta(days=2))
    assert smr3.next_execution == timedelta(days=1)