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
from datetime import datetime, timedelta
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

def test_SMSSender__find_rule_index():
    smsS = SMSSender()

    rule1 = SendMessageRule(datetime(2000, 1, 1), id=1)
    rule2 = SendMessageRule(datetime(2000, 1, 1), id=2)
    asyncio.run(smsS.set_rule(rule1))
    asyncio.run(smsS.set_rule(rule2))

    assert len(smsS.rules) == 2

    # SMSSender.__find_rule_index is renamed (by the python interpreter) as SMSSender._SMSSender__find_rule_index
    assert smsS.rules[asyncio.run(smsS._SMSSender__find_rule_index(rule1.id))] == rule1 # type: ignore (id is set)
    assert smsS.rules[asyncio.run(smsS._SMSSender__find_rule_index(rule2.id))] == rule2 # type: ignore (id is set)

def test_SMSSender__find_ready_rules():
    smsS = SMSSender()

    rule1 = SendMessageRule(datetime.now() - timedelta(1), interval = timedelta(1), id=1) # Always ready to send
    rule2 = SendMessageRule(datetime.now() + timedelta(1), interval = timedelta(1), id=2) # Always in the future

    asyncio.run(smsS.set_rule(rule1))
    asyncio.run(smsS.set_rule(rule2))

    ready_rules = asyncio.run(smsS._find_ready_rules())
    assert rule1 in ready_rules and rule2 not in ready_rules

def test_SMSSender__find_next_execution_interval():
    smsS = SMSSender()

    nei = asyncio.run(smsS._find_next_execution_interval())
    assert nei is None

    rule1 = SendMessageRule(datetime.now() + timedelta(1), interval = timedelta(1), id=1) # Always in the future
    rule2 = SendMessageRule(datetime.now() - timedelta(1), interval = timedelta(1), id=2) # Always in the past

    asyncio.run(smsS.set_rule(rule1))

    nei = asyncio.run(smsS._find_next_execution_interval())
    assert nei is not None
    assert round(nei.total_seconds()) == timedelta(1).total_seconds()

    asyncio.run(smsS.set_rule(rule2))
    assert nei is not None
    assert round(nei.total_seconds()) == timedelta(1).total_seconds()