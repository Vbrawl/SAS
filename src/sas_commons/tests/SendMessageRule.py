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
from datetime import datetime


def test_SendMessageRule__init():
    smr = SendMessageRule() # No error
    smr2 = SendMessageRule(datetime(2000, 1, 1), datetime(2000, 1, 2)) # No error
    smr3 = SendMessageRule(datetime(2000, 1, 1), last_executed=datetime(2000, 1, 1)) # No error
    smr4 = SendMessageRule(last_executed=datetime(2000, 1, 1), end_date=datetime(2000, 1, 1))

    with pytest.raises(ValueError):
        smr5 = SendMessageRule(start_date=datetime(2000, 1, 2), end_date=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr6 = SendMessageRule(start_date=datetime(2000, 1, 2), last_executed=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr7 = SendMessageRule(end_date=datetime(2000, 1, 1), last_executed=datetime(2000, 1, 2))