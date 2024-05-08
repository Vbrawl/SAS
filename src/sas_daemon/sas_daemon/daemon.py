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
from sas_commons import Database, SendMessageRule
from wsAPI.server import WSAPI
import asyncio



class Daemon:
    def __init__(self):
        self.collect_rules_interval = 60

        self.db = Database("temp.db")
        self.operations:dict[int, asyncio.Task] = {}
        self.op_lock = asyncio.Lock()

        self.wsapi = WSAPI(self.db)
        # Update when a rule is updated, their attributes are automatically updated before sending.
        self.wsapi.OPTIONS["rule"]["add"] = self.rule_add_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["alter"] = self.rule_alter_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["remove"] = self.rule_deregister_and_remove # type: ignore

    async def rule_add_and_register(self, wsapi:WSAPI, **kwargs):
        res = await wsapi.rule_add(**kwargs)
        if "id" in res:
            id:int = res["id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore
            async with self.op_lock:
                self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms))
        return res

    async def rule_alter_and_register(self, wsapi:WSAPI, **kwargs):
        res = await wsapi.rule_alter(**kwargs)
        if "status" in res and res["status"] == "success":
            id:int = kwargs["id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore

            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                if rule is None:
                    del self.operations[id]
                else:
                    self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms))
        return res
    
    async def rule_deregister_and_remove(self, wsapi:WSAPI, **kwargs):
        id = kwargs.get("id", None)
        if isinstance(id, int):
            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                    del self.operations[id]
        return await wsapi.rule_remove(**kwargs)

    async def send_sms(self, pta:SendMessageRule): # callback
        template = pta.template
        if pta.template.id is not None:
            temp = self.db.get_template(pta.template.id)
            if temp is not None:
                template = temp

        for recipient in pta.recipients:
            if getattr(recipient, "id", None) is not None:
                temp = self.db.get_person(recipient.id)
                if temp is not None:
                    recipient = temp
            msg = template.compileFor(recipient)
            # TODO: Use telnyx API to send a message
            print(msg)
    
    async def collect_rules_indefinitely(self):
        while True:
            async with self.op_lock:
                for k,v in self.operations.items():
                    if v.done():
                        del self.operations[k]
            await asyncio.sleep(self.collect_rules_interval)

    async def start(self):
        for rule in self.db.get_rules():
            if rule.id is not None:
                self.operations[rule.id] = asyncio.create_task(rule.infschedule(self.send_sms))
        

        await self.wsapi.start_server()
        await self.collect_rules_indefinitely()