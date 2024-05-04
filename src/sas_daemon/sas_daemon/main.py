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

This file (main.py) is the main starting point of the "Daemon" component
of the project (SAS).
'''
from sas_commons import SendMessageRule, TemplateArguments, Template
from datetime import datetime, timedelta
import asyncio


async def main():
    async def cback(ta:TemplateArguments, msg:str):
        print(msg)

    rules = [
        SendMessageRule(0, [TemplateArguments(name="Bruce")], Template("Hello $(name)!"), datetime.now(), end_date=datetime.now()+timedelta(seconds=20), interval=timedelta(seconds=5)),
        SendMessageRule(0, [TemplateArguments(name="John")], Template("Hello $(name)!"), datetime.now(), interval=timedelta(seconds=7)),
        SendMessageRule(0, [TemplateArguments(name="Nick")], Template("Hello $(name)!"), datetime.now(), interval=timedelta(seconds=3))
    ]

    oper = []
    for rule in rules:
        oper.append(asyncio.create_task(rule.infschedule(cback)))
    
    await asyncio.wait(oper)


asyncio.run(main())