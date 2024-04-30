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
'''

from sas_daemon import SMSSender
from sas_commons import SendMessageRule
from datetime import datetime
import asyncio


def test_SMSSender__set_rule():
    smsS = SMSSender()

    async def setRules(smsS:SMSSender):
        await asyncio.gather(
            smsS.set_rule(SendMessageRule(datetime(2000, 1, 1), id=1)),
            smsS.set_rule(SendMessageRule(datetime(2000, 1, 1), id=2)),
            smsS.set_rule(SendMessageRule(datetime(2000, 1, 2), id=1)) # Overwrite first rule
        )

    asyncio.run(setRules(smsS))
    assert len(smsS.rules) == 2
    assert smsS.rules[0]._start_date

def test_SMSSender__remove_rule():
    smsS = SMSSender()

    asyncio.run(smsS.set_rule(SendMessageRule(datetime(2000, 1, 1), id=1)))
    asyncio.run(smsS.set_rule(SendMessageRule(datetime(2000, 1, 1), id=2)))
    assert len(smsS.rules) == 2
    asyncio.run(smsS.remove_rule(1))
    asyncio.run(smsS.remove_rule(SendMessageRule(datetime(2000, 1, 1), id=2)))
    assert len(smsS.rules) == 0